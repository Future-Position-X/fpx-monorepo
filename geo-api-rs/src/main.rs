use lambda_http::{lambda, IntoResponse, Request};
use lambda_runtime::{error::HandlerError, Context};
use serde_json::json;

use postgres::{Client, NoTls};

use postgis::ewkb;
// use postgres_openssl::MakeTlsConnector;

//use geojson::{Feature, GeoJson, Geometry, Value};
use std::collections::HashMap;

use geo_postgis::FromPostgis;

fn main() {
    lambda!(handler)
}
#[derive(Debug)]
struct Record {
    id: uuid::Uuid,
    geometry: ewkb::Geometry,
    properties: serde_json::Value,
}

fn handler(
    _: Request,
    _: Context,
) -> Result<impl IntoResponse, HandlerError> {

    /*
    let connector = MakeTlsConnector::new(builder.build());

    let mut client = Client::connect(
        format!(
            "host={} port={} dbname={} user={} password={} sslmode=require",
            "gia-dev.cjesin4yac8j.eu-north-1.rds.amazonaws.com",
            5432,
            "gia",
            "master",
            "lN1Pb60MO6sC",
        )
        .as_str(),
        connector,
    )?;
    */
    let mut client = Client::connect(format!(
        "host={} port={} dbname={} user={} password={}",
        "gia-dev.cjesin4yac8j.eu-north-1.rds.amazonaws.com",
        5432,
        "gia",
        "master",
        "lN1Pb60MO6sC",
    )
    .as_str(), NoTls).unwrap();

    let mut records: Vec<Record> = vec![];

    for row in client.query("SELECT uuid, geometry, properties from items LIMIT 1", &[]).unwrap() {
        let id = row.get(0);
        let geometry = row.get(1);
        let properties = row.get(2);
        records.push(Record{
            id,
            geometry,
            properties,
        });        
        println!("Selected: {:?}", &records);
    }

    //use geo_types::Geometry;

    let mut features = vec![]; 
    for rec in records {
        let geometry: geo_types::Geometry<f64> = Option::<geo_types::Geometry<f64>>::from_postgis(&rec.geometry).unwrap();
        //let postgis_point = postgis::ewkb::Point { x: 1., y: -2., srid: None };
        //let geo_point = geo_types::Point::from_postgis(&postgis_point);

        //features.push(g);
        //let geo_point = geo_types::Point::new(40.02f32, 116.34f32);
        //let geojson_point = geojson::Value::from(&geo_point);
        
        //features.push(geojson_point);
        let gj =  geojson::Geometry::new(geojson::Value::from(&geometry));
        
        //features.push(gj);

        /*
        let a: serde_json::map::Map<String, serde_json::Value> = rec.properties.into_iter()
        .filter_map(|(k, v)| {
            Some((k, serde_json::Value::String(v?)))
        })
        .collect();
        */
        
        let a = rec.properties;
        let b = a.as_object().unwrap().to_owned();
        let geojson = geojson::GeoJson::Feature(geojson::Feature {
            bbox: None,
            geometry: Some(gj),
            id: Some(geojson::feature::Id::String(rec.id.to_string())),
            properties: Some(b),
            foreign_members: None
        });

        features.push(geojson);
        
    }
    // `serde_json::Values` impl `IntoResponse` by default
    // creating an application/json response
    Ok(json!({
        "message": format!("Go Serverless v1.0{:?}! Your function executed successfully!", &features)
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn handler_handles() {
        let request = Request::default();
        let expected = json!({
            "message": "Go Serverless v1.0! Your function executed successfully!"
        })
        .into_response();
        let response = handler(request, Context::default())
            .expect("expected Ok(_) value")
            .into_response();
        assert_eq!(response.body(), expected.body())
    }
}
