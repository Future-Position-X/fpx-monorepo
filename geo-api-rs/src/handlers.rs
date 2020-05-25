use lambda_http::http::header::CONTENT_TYPE;
use lambda_http::{IntoResponse, Request, Response};
use lambda_runtime::{error::HandlerError, Context};
use std::time::Instant;

use crate::services;
use crate::shared_now;
pub fn handler(_: Request, _: Context) -> Result<impl IntoResponse, HandlerError> {
    let instant = Instant::now();
    let _ = shared_now(Some(instant));

    let items = services::get_items();

    let mut features = vec![];

    for rec in items {
        let geojson_geometry = geojson::Geometry::new(geojson::Value::from(&rec.geometry));
        let properties = rec.properties.as_object().unwrap().to_owned();
        let feature = geojson::Feature {
            bbox: None,
            geometry: Some(geojson_geometry),
            id: Some(geojson::feature::Id::String(rec.id.to_string())),
            properties: Some(properties),
            foreign_members: None,
        };

        features.push(feature);
    }
    println!(
        "filled features vec: {}",
        shared_now(None).elapsed().as_millis()
    );

    let feature_collection = geojson::FeatureCollection {
        bbox: None,
        features: features,
        foreign_members: None,
    };
    println!(
        "created feature collection: {}",
        shared_now(None).elapsed().as_millis()
    );

    let geojson = feature_collection.to_string();

    println!(
        "created geojson: {}",
        shared_now(None).elapsed().as_millis()
    );

    let res = Response::builder()
        .status(200)
        .header(CONTENT_TYPE, "application/json")
        .body(geojson)
        .expect("that should have worked!");

    println!(
        "created response: {}",
        shared_now(None).elapsed().as_millis()
    );

    Ok(res)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn handler_handles() {
        let request = Request::default();
        /*
        let expected = json!({
            "message": "Go Serverless v1.0! Your function executed successfully!"
        })
        .into_response();
        */
        let response = handler(request, Context::default())
            .expect("expected Ok(_) value")
            .into_response();
        assert_eq!(response.body().len(), 30490681)
    }
}
