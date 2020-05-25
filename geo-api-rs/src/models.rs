#[derive(Debug)]

pub struct Item {
    pub id: uuid::Uuid,
    pub geometry: geo_types::Geometry<f64>, //postgis::ewkb::Geometry,
    pub properties: serde_json::Value,
}
