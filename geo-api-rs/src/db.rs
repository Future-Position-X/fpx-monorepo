use crate::store::add_items as add_items_b;
use crate::{
    errors::MyError,
    models::{Item, User},
};
use deadpool_postgres::Client;

use crate::models::{Collection, ItemFilters};

use tokio_pg_mapper::FromTokioPostgresRow;
use tokio_postgres::types::ToSql;

pub async fn get_users(client: &Client) -> Result<Vec<User>, MyError> {
    let _stmt = "SELECT * FROM users".to_string();
    let stmt = client.prepare(&_stmt).await.unwrap();

    let users = client
        .query(&stmt, &[])
        .await?
        .iter()
        .map(|row| User::from_row_ref(row).unwrap())
        .collect::<Vec<User>>();
    Ok(users)
}

pub async fn get_user(client: &Client, uuid: &uuid::Uuid) -> Result<User, MyError> {
    let stmt = "SELECT * FROM users WHERE uuid=$1 LIMIT 1".to_string();

    let mut users = client
        .query(stmt.as_str(), &[uuid])
        .await?
        .iter()
        .map(|row| User::from_row_ref(row).unwrap())
        .collect::<Vec<User>>();
    if users.is_empty() {
        Err(MyError::NotFound)
    } else {
        Ok(users.pop().unwrap())
    }
}

pub async fn get_user_by_email(client: &Client, email: &str) -> Result<User, MyError> {
    let stmt = "SELECT * FROM users WHERE email=$1 LIMIT 1".to_string();

    let mut users = client
        .query(stmt.as_str(), &[&email])
        .await?
        .iter()
        .map(|row| User::from_row_ref(row).unwrap())
        .collect::<Vec<User>>();
    if users.is_empty() {
        Err(MyError::NotFound)
    } else {
        Ok(users.pop().unwrap())
    }
}

pub async fn get_collections(
    client: &Client,
    provider_uuid: &uuid::Uuid,
) -> Result<Vec<Collection>, MyError> {
    let _stmt = format!(
        "SELECT * FROM collections WHERE is_public=true OR provider_uuid='{}'",
        provider_uuid
    );
    let stmt = client.prepare(&_stmt).await.unwrap();

    let collections = client
        .query(&stmt, &[])
        .await?
        .iter()
        .map(|row| Collection::from_row_ref(row).unwrap())
        .collect::<Vec<Collection>>();
    Ok(collections)
}

pub async fn get_collection(
    client: &Client,
    provider_uuid: &uuid::Uuid,
    collection_uuid: &uuid::Uuid,
) -> Result<Collection, MyError> {
    let _stmt = format!(
        "SELECT * FROM collections WHERE uuid='{}' AND (is_public=true OR provider_uuid='{}')",
        collection_uuid, provider_uuid
    );

    let stmt = client.prepare(&_stmt).await.unwrap();

    let mut collections = client
        .query(&stmt, &[])
        .await?
        .iter()
        .map(|row| Collection::from_row_ref(row).unwrap())
        .collect::<Vec<Collection>>();

    let collection = collections.pop().ok_or(MyError::NotFound)?;
    Ok(collection)
}

pub async fn delete_items(client: &Client, collection_uuid: &uuid::Uuid) -> Result<(), MyError> {
    let _stmt = format!(
        "DELETE FROM items WHERE collection_uuid='{}'",
        collection_uuid
    );
    let stmt = client.prepare(&_stmt).await.unwrap();

    let _ = client.query(&stmt, &[]).await?;
    Ok(())
}
pub async fn insert_items(
    client: &Client,
    items: Vec<Item>,
    collection_uuid: &uuid::Uuid,
) -> Result<Vec<uuid::Uuid>, MyError> {
    let _ = delete_items(client, collection_uuid).await;
    add_items_batch(client, items).await
}

pub async fn add_items_batch(
    client: &Client,
    mut items: Vec<Item>,
) -> Result<Vec<uuid::Uuid>, MyError> {
    //add_items(client, items).await
    let mut uuids = vec![];
    for item in items.iter_mut() {
        let uuid = uuid::Uuid::new_v4();
        item.uuid = Some(uuid);
        uuids.push(uuid);
    }
    add_items_b(client, &items).await;
    Ok(uuids)
}

pub enum ParamVariant {
    UuidValue(uuid::Uuid),
    F64Value(f64),
    I64Value(i64),
}

pub fn create_where(filters: &ItemFilters) -> (String, Vec<ParamVariant>) {
    let mut params: Vec<ParamVariant> = vec![];
    let mut where_query = format!(
        "
        (
            collections.is_public=true
            OR collections.provider_uuid = ${}
        )
        ",
        params.len() + 1
    );

    params.push(ParamVariant::UuidValue(filters.provider_uuid));

    if filters.collection_uuid.is_some() {
        where_query = format!(
            "{} AND collection_uuid = ${}",
            where_query,
            params.len() + 1
        );
        params.push(ParamVariant::UuidValue(filters.collection_uuid.unwrap()));
    }

    if filters.spatial_filter.is_some() && filters.spatial_filter.as_ref().unwrap() == "intersect" {
        where_query = format!(
            "
                {}
                AND ST_Intersects(
                geometry,
                ST_MakeEnvelope(${},${},${},${})
            )",
            where_query,
            params.len() + 1,
            params.len() + 2,
            params.len() + 3,
            params.len() + 4
        );
        params.push(ParamVariant::F64Value(
            filters.spatial_filter_envelope_xmin.unwrap(),
        ));
        params.push(ParamVariant::F64Value(
            filters.spatial_filter_envelope_ymin.unwrap(),
        ));
        params.push(ParamVariant::F64Value(
            filters.spatial_filter_envelope_xmax.unwrap(),
        ));
        params.push(ParamVariant::F64Value(
            filters.spatial_filter_envelope_ymax.unwrap(),
        ));
    }

    if filters.limit.is_some() {
        where_query = format!("{} LIMIT ${}", where_query, params.len() + 1);
        params.push(ParamVariant::I64Value(filters.limit.unwrap()))
    }

    if filters.offset.is_some() {
        where_query = format!("{} OFFSET ${}", where_query, params.len() + 1);
        params.push(ParamVariant::I64Value(filters.offset.unwrap()))
    }

    (where_query, params)
}

pub async fn get_items(client: &Client, filters: &ItemFilters) -> Result<Vec<Item>, MyError> {
    use crate::utils::shared_now;
    use geo_postgis::FromPostgis;
    let (where_query, params) = create_where(filters);
    let stmt = format!(
        "SELECT items.uuid, items.collection_uuid, ST_SIMPLIFY(items.geometry, {}, false) as geometry, items.properties FROM public.items JOIN public.collections ON items.collection_uuid = collections.uuid WHERE {}",
        filters.simplify.map_or(0.0, |v| v),
        where_query
    );

    // Making a prepared statement gives pretty bad query plan on after 5 executions (https://www.cybertec-postgresql.com/en/tech-preview-how-postgresql-12-handles-prepared-plans/), i.e better to either use "SET plan_cache_mode = 'force_custom_plan';" if using preopared statements or just not use prepared statements event if it's nice with parameterized queries to not have sql injections
    // let prepared_stmt = client.prepare(&stmt).await.unwrap();

    let mut batched_values = Vec::<Box<dyn ToSql + Sync>>::new();
    for value in params.iter() {
        match *value {
            ParamVariant::UuidValue(ref v) => {
                batched_values.push(Box::new(*v));
            }
            ParamVariant::F64Value(ref v) => {
                batched_values.push(Box::new(*v));
            }
            ParamVariant::I64Value(ref v) => {
                batched_values.push(Box::new(*v));
            }
        };
    }

    let binds_borrowed = batched_values.iter().map(|s| &**s).collect::<Vec<_>>();

    let mut first = true;
    let items = client
        .query(stmt.as_str(), &*binds_borrowed)
        .await?
        .iter()
        .map(|row| {
            if first {
                println!("first row: {}", shared_now(None).elapsed().as_millis());
                first = false;
            }
            let uuid = row.get(0);
            let collection_uuid = row.get(1);
            let pg_geometry: Option<postgis::ewkb::Geometry> = row.try_get(2).ok();
            let geo_geometry = match pg_geometry {
                Some(g) => Option::<geo_types::Geometry<f64>>::from_postgis(&g),
                None => return None,
            };
            let properties = row.get(3);
            Some(Item {
                uuid: Some(uuid),
                collection_uuid: Some(collection_uuid),
                geometry: geo_geometry,
                properties,
            })
        })
        .filter_map(|i| i)
        .collect::<Vec<Item>>();
    println!(
        "collected items({}): {}",
        items.len(),
        shared_now(None).elapsed().as_millis()
    );
    Ok(items)
}
