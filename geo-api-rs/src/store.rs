use std::clone::Clone;
use std::string::ToString;

use crate::models::Item;
use deadpool_postgres::Client;
use geo_postgis::ToPostgis;
use tokio_postgres::types::ToSql;

#[derive(Debug, Clone)]
pub enum Variant {
    UuidValue(uuid::Uuid),
    GeometryValue(Option<postgis::ewkb::Geometry>),
    JsonValue(serde_json::Value),
}

pub struct InsertBatcher<'a> {
    client: &'a Client,
    column_names: Vec<String>,
    insert_string: String,
    values_string: String,
    batch_count: usize,
    batched_values: Vec<Box<dyn ToSql + Sync>>,
}

pub async fn add_items(client: &Client, items: &[Item]) {
    let mut batcher: InsertBatcher = InsertBatcher::new(
        client,
        "items",
        vec![
            String::from("uuid"),
            String::from("collection_uuid"),
            String::from("geometry"),
            String::from("properties"),
        ],
    );
    for item in items {
        let geom = match &item.geometry {
            Some(v) => Some(v.to_postgis_wgs84()),
            None => None,
        };
        batcher.prepare_batch(
            item.uuid.unwrap_or_else(uuid::Uuid::new_v4),
            item.collection_uuid.unwrap(),
            geom,
            item.properties.clone(),
        );
    }
    batcher.execute().await
}

impl<'a> InsertBatcher<'a> {
    pub fn new(client: &'a Client, table_name: &str, column_names: Vec<String>) -> Self {
        let column_names_str = column_names.join(",");
        let sql = format!("INSERT INTO {}({}) VALUES", table_name, column_names_str);

        InsertBatcher {
            client,
            column_names,
            insert_string: sql,
            values_string: String::from(""),
            batch_count: 0,
            batched_values: Vec::<Box<dyn ToSql + Sync>>::new(),
        }
    }

    pub fn insert_batch(&mut self, batch: Vec<Variant>) {
        for value in batch.iter() {
            match *value {
                Variant::UuidValue(ref v) => {
                    self.batched_values.push(Box::new(*v));
                }
                Variant::GeometryValue(ref v) => {
                    self.batched_values.push(Box::new(v.clone()));
                }
                Variant::JsonValue(ref v) => {
                    self.batched_values.push(Box::new(v.clone()));
                }
            };
        }

        let number_of_fields = self.column_names.len();
        let start_value = self.batch_count * number_of_fields;

        self.batch_count += 1;

        let mut place_holder_strs: Vec<String> = Vec::new();

        for i in start_value..(start_value + number_of_fields) {
            place_holder_strs.push(format!("${}", i + 1));
        }

        let place_holder_str = place_holder_strs.join(",");
        self.values_string += &format!(" ({}),", place_holder_str);
    }

    pub async fn execute(&mut self) {
        // Example Fast Import
        // INSERT INTO films (code, title, did, date_prod, kind) VALUES
        //     ('B6717', 'Tampopo', 110, '1985-02-10', 'Comedy'),
        //     ('HG120', 'The Dinner Game', 140, DEFAULT, 'Comedy');

        // INSERT INTO sensor_values(timestamp,sensor_id,value)
        //    VALUES  ($1,$2,$3), ($4,$5,$6), ($7,$8,$9), ($10,$11,$12), ($13,$14,$15), ($16,$17,$18);

        let binds_borrowed = self.batched_values.iter().map(|s| &**s).collect::<Vec<_>>();

        self.values_string.pop();
        let _stmt = self.insert_string.to_string() + " " + &self.values_string;

        let stmt = self.client.prepare(&_stmt).await.unwrap();

        let _res = self.client.query(&stmt, &*binds_borrowed).await.unwrap();

        //self.client.execute(&self.insert_string, &*binds_borrowed);

        // match self.conn.execute(&self.insert_string, &*binds_borrowed) {

        //     Err(why) => {
        //         warn!("{}", self.insert_string);
        //         bail!("error: {}", why);

        //         println!("{}", self.insert_string);
        //         println!("error: {}", why);
        //     }
        //     Ok(result) => {
        //         println!("success");
        //     },
        // };

        //self.conn.commit();
        //self.conn.batch_execute("COMMIT").unwrap();
    }

    pub fn prepare_batch(
        &mut self,
        uuid: uuid::Uuid,
        collection_uuid: uuid::Uuid,
        geometry: Option<postgis::ewkb::Geometry>,
        properties: serde_json::Value,
    ) {
        let mut variants: Vec<Variant> = Vec::new();
        variants.push(Variant::UuidValue(uuid));
        variants.push(Variant::UuidValue(collection_uuid));
        variants.push(Variant::GeometryValue(geometry));
        variants.push(Variant::JsonValue(properties));

        self.insert_batch(variants);
    }
}
