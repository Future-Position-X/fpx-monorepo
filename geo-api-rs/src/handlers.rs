use lambda_http::http::header::{CONTENT_ENCODING, CONTENT_TYPE};
use lambda_http::{Body, IntoResponse, Request, Response};
use lambda_runtime::{error::HandlerError, Context};
use std::time::Instant;

use flate2::write::GzEncoder;
use flate2::Compression;
use std::io::prelude::*;

use crate::services;
use crate::shared_now;

fn compress_gzip(geojson: String) -> Body {
    let mut e = GzEncoder::new(Vec::new(), Compression::default());
    e.write_all(geojson.as_bytes()).unwrap();
    Body::from(e.finish().unwrap())
}
fn compress_brotli(geojson: String) -> Body {
    use std::io;
    let mut buffer = Vec::<u8>::new();
    let mut b = geojson.as_bytes();
    {
        let mut writer = brotli::CompressorWriter::new(&mut buffer, 4096, 4, 22);
        let mut buf = [0u8; 4096];
        loop {
            match b.read(&mut buf[..]) {
                Err(e) => {
                    if let io::ErrorKind::Interrupted = e.kind() {
                        continue;
                    }
                    panic!(e);
                }
                Ok(size) => {
                    if size == 0 {
                        match writer.flush() {
                            Err(e) => {
                                if let io::ErrorKind::Interrupted = e.kind() {
                                    continue;
                                }
                                panic!(e)
                            }
                            Ok(_) => break,
                        }
                    }
                    match writer.write_all(&buf[..size]) {
                        Err(e) => panic!(e),
                        Ok(_) => {}
                    }
                }
            }
        }
    }

    Body::from(buffer)
}
pub fn handler(req: Request, _: Context) -> Result<impl IntoResponse, HandlerError> {
    let use_br = match req.headers().get("accept-encoding") {
        Some(x) => x.to_str().unwrap_or("gzip").contains("br"),
        None => true,
    };
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

    let body = if use_br {
        compress_brotli(geojson)
    } else {
        compress_gzip(geojson)
    };

    let enc = if use_br { "br" } else { "gzip" };

    println!(
        "compressed(use_br: {}) geojson: {}",
        use_br,
        shared_now(None).elapsed().as_millis()
    );

    let res = Response::builder()
        .status(200)
        .header(CONTENT_TYPE, "application/json")
        .header(CONTENT_ENCODING, enc)
        .body(body)
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
        assert_eq!(response.body().len(), 4536893)
    }
}
