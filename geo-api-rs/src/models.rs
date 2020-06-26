use serde::{Deserialize, Serialize};
use tokio_pg_mapper_derive::PostgresMapper;
use uuid::Uuid;

/// Our claims struct, it needs to derive `Serialize` and/or `Deserialize`
#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,
    pub exp: usize,
    pub provider_uuid: String,
}

#[derive(Debug)]
pub struct MyClaims(pub Option<Claims>);

#[derive(Deserialize, PostgresMapper, Serialize)]
#[pg_mapper(table = "users")]
pub struct User {
    pub uuid: uuid::Uuid,
    pub email: String,
    #[serde(skip_serializing)]
    pub password: String,
    pub provider_uuid: uuid::Uuid,
    //pub created_at: Timestamp<NaiveDateTime>,
    //pub updated_at: Timestamp<NaiveDateTime>,
    pub revision: i32,
}

#[derive(Deserialize, PostgresMapper, Serialize, Debug)]
#[pg_mapper(table = "collections")]
pub struct Collection {
    pub uuid: Option<uuid::Uuid>,
    pub name: Option<String>,
    pub provider_uuid: Option<uuid::Uuid>,
    pub is_public: Option<bool>,
}

//#[derive(PostgresMapper)]
//#[pg_mapper(table = "items")]
#[derive(Debug)]
pub struct Item {
    pub uuid: Option<uuid::Uuid>,
    pub collection_uuid: Option<uuid::Uuid>,
    pub geometry: Option<geo_types::Geometry<f64>>,
    //pub geometry: postgis::ewkb::Geometry,
    pub properties: serde_json::Value,
}

#[derive(Debug)]
pub struct ItemFilters {
    pub offset: Option<i64>,
    pub limit: Option<i64>,
    pub collection_uuid: Option<Uuid>,
    pub provider_uuid: Uuid,
    pub spatial_filter: Option<String>,
    pub spatial_filter_envelope_xmin: Option<f64>,
    pub spatial_filter_envelope_ymin: Option<f64>,
    pub spatial_filter_envelope_xmax: Option<f64>,
    pub spatial_filter_envelope_ymax: Option<f64>,
    pub simplify: Option<f64>,
}
