use crate::db::{add_items_batch, insert_items};
use crate::models::{Claims, Item, ItemFilters, MyClaims};
use crate::{db, errors::MyError, utils::shared_now};

use actix_web::web::Path;
use actix_web::{web, Error, HttpRequest, HttpResponse};
use bytes::Bytes;
use deadpool_postgres::{Client, Pool};

use geo_types::Geometry;
use geojson::GeoJson;
use std::convert::TryInto;
use std::time::Instant;

use crate::config::Config;
use actix_web::error::ErrorUnauthorized;
use bcrypt::verify;
use chrono::{Duration, Utc};
use jsonwebtoken::{encode, EncodingKey, Header};
use serde::{Deserialize, Serialize};
/*
`${BASE_URL}/collections/${collectionId}/items?
limit=100000&
spatial_filter=intersect&
spatial_filter.envelope.xmin=${bounds.minX}&
spatial_filter.envelope.ymin=${bounds.minY}&
spatial_filter.envelope.xmax=${bounds.maxX}&
spatial_filter.envelope.ymax=${bounds.maxY}&
simplify=${simplify}`,
 */

#[derive(Deserialize, Debug)]
pub struct ItemsRequest {
    offset: Option<i64>,
    limit: Option<i64>,
    spatial_filter: Option<String>,
    #[serde(alias = "spatial_filter.envelope.xmin")]
    spatial_filter_envelope_xmin: Option<f64>,
    #[serde(alias = "spatial_filter.envelope.ymin")]
    spatial_filter_envelope_ymin: Option<f64>,
    #[serde(alias = "spatial_filter.envelope.xmax")]
    spatial_filter_envelope_xmax: Option<f64>,
    #[serde(alias = "spatial_filter.envelope.ymax")]
    spatial_filter_envelope_ymax: Option<f64>,
    simplify: Option<f64>,
}

#[derive(Deserialize, Debug)]
pub struct CreateSession {
    pub email: String,
    pub password: String,
}

#[derive(Deserialize, Serialize, Debug)]
pub struct Session {
    pub token: String,
}

#[derive(Deserialize, Serialize, Debug)]
pub struct UserUuid {
    pub uuid: uuid::Uuid,
}

impl ItemsRequest {
    pub fn to_item_filter(item_request: &Self) -> ItemFilters {
        ItemFilters {
            offset: item_request.offset,
            limit: item_request.limit,
            collection_uuid: None,
            provider_uuid: uuid::Uuid::nil(),
            spatial_filter: item_request.spatial_filter.clone(),
            spatial_filter_envelope_xmin: item_request.spatial_filter_envelope_xmin,
            spatial_filter_envelope_ymin: item_request.spatial_filter_envelope_ymin,
            spatial_filter_envelope_xmax: item_request.spatial_filter_envelope_xmax,
            spatial_filter_envelope_ymax: item_request.spatial_filter_envelope_ymax,
            simplify: item_request.simplify,
        }
    }
}

pub async fn create_session(
    req: HttpRequest,
    db_pool: web::Data<Pool>,
    create_session: web::Json<CreateSession>,
) -> Result<HttpResponse, Error> {
    let client: Client = db_pool.get().await.map_err(MyError::PoolError)?;

    let user = db::get_user_by_email(&client, &create_session.email).await?;

    let authenticated = verify(&create_session.password, &user.password).unwrap();

    if authenticated {
        let jwt_secret = &req.app_data::<Config>().unwrap().jwt_secret;
        let claims = Claims {
            sub: user.uuid.to_string(),
            exp: (Utc::now() + Duration::days(14)).timestamp() as usize,
            provider_uuid: user.provider_uuid.to_string(),
        };
        let token = encode(
            &Header::default(),
            &claims,
            &EncodingKey::from_secret(jwt_secret.as_ref()),
        )
        .map_err(|_| MyError::AuthenticationFailed)?;

        let session = Session { token };

        Ok(HttpResponse::Ok().json(session))
    } else {
        Err(MyError::AuthenticationFailed.into())
    }
}

pub async fn get_users(db_pool: web::Data<Pool>) -> Result<HttpResponse, Error> {
    let client: Client = db_pool.get().await.map_err(MyError::PoolError)?;

    let users = db::get_users(&client).await.unwrap();

    Ok(HttpResponse::Ok().json(users))
}

pub async fn get_user(db_pool: web::Data<Pool>, info: Path<String>) -> Result<HttpResponse, Error> {
    let client: Client = db_pool.get().await.map_err(MyError::PoolError)?;

    let user_uuid = uuid::Uuid::parse_str(info.as_str()).map_err(MyError::UuidError)?;
    let user = db::get_user(&client, &user_uuid).await.unwrap();

    Ok(HttpResponse::Ok().json(user))
}

pub async fn get_user_uuid(claims: MyClaims) -> Result<HttpResponse, Error> {
    if claims.0.is_none() {
        return Err(ErrorUnauthorized("No authorization token"));
    }
    let user_uuid = UserUuid {
        uuid: uuid::Uuid::parse_str(claims.0.unwrap().sub.as_str()).unwrap(),
    };
    Ok(HttpResponse::Ok().json(user_uuid))
}

pub async fn get_collections(db_pool: web::Data<Pool>) -> Result<HttpResponse, Error> {
    let client: Client = db_pool.get().await.map_err(MyError::PoolError)?;

    let collections = db::get_collections(&client, &uuid::Uuid::nil())
        .await
        .unwrap();

    Ok(HttpResponse::Ok().json(collections))
}

pub async fn get_collection(
    db_pool: web::Data<Pool>,
    info: Path<String>,
) -> Result<HttpResponse, Error> {
    let client: Client = db_pool.get().await.map_err(MyError::PoolError)?;
    let collection_uuid = uuid::Uuid::parse_str(info.as_str()).map_err(MyError::UuidError)?;

    let collections = db::get_collection(&client, &uuid::Uuid::nil(), &collection_uuid)
        .await
        .unwrap();

    Ok(HttpResponse::Ok().json(collections))
}

pub async fn post_items(
    db_pool: web::Data<Pool>,
    info: web::Path<String>,
    body: Bytes,
) -> Result<HttpResponse, Error> {
    let client: Client = db_pool.get().await.map_err(MyError::PoolError)?;
    let geojson = match std::str::from_utf8(&body)
        .unwrap()
        .parse::<GeoJson>()
        .unwrap()
    {
        GeoJson::FeatureCollection(n) => n,
        _ => panic!("boom"),
    };
    let mut items = vec![];
    let collection_uuid = uuid::Uuid::parse_str(info.as_str()).ok();
    for feature in geojson.features {
        //let geo = TryInto::<Geometry<_>>::try_into(feature.geometry.unwrap().value).unwrap();

        let geo = match feature.geometry {
            Some(v) => TryInto::<Geometry<_>>::try_into(v.value).ok(),
            None => None,
        };
        let item = Item {
            uuid: None,
            collection_uuid,
            geometry: geo,
            properties: serde_json::value::Value::Object(feature.properties.unwrap()),
        };

        items.push(item);
    }

    let uuids = insert_items(&client, items, &collection_uuid.unwrap()).await?;
    Ok(HttpResponse::Ok().json(uuids))
}

pub async fn put_items(
    db_pool: web::Data<Pool>,
    info: Path<String>,
    body: Bytes,
) -> Result<HttpResponse, Error> {
    let client: Client = db_pool.get().await.map_err(MyError::PoolError)?;
    let geojson = match std::str::from_utf8(&body).unwrap().parse::<GeoJson>() {
        Ok(GeoJson::FeatureCollection(n)) => n,
        Err(e) => {
            dbg!(&e);
            dbg!(&body);
            panic!(e);
        }
        _ => panic!("boom"),
    };
    let mut items = vec![];

    let collection_uuid = uuid::Uuid::parse_str(info.as_str()).ok();

    for feature in geojson.features {
        //let geo = TryInto::<Geometry<_>>::try_into(feature.geometry.unwrap().value).unwrap();

        let geo = match feature.geometry {
            Some(v) => TryInto::<Geometry<_>>::try_into(v.value).ok(),
            None => None,
        };
        let item = Item {
            uuid: None,
            collection_uuid,
            geometry: geo,
            properties: serde_json::value::Value::Object(feature.properties.unwrap()),
        };

        items.push(item);
    }

    let uuids = add_items_batch(&client, items).await?;
    Ok(HttpResponse::Ok().json(uuids))
}

pub async fn get_items(
    db_pool: web::Data<Pool>,
    info: Path<String>,
    web::Query(q): web::Query<ItemsRequest>,
    claims: MyClaims,
) -> Result<HttpResponse, Error> {
    dbg!(&claims);
    println!(
        "handle request: {}",
        shared_now(Some(Instant::now())).elapsed().as_millis()
    );
    let client: Client = db_pool.get().await.map_err(MyError::PoolError)?;
    println!(
        "got db client from pool: {}",
        shared_now(None).elapsed().as_millis()
    );
    let mut filters = ItemsRequest::to_item_filter(&q);
    filters.collection_uuid = uuid::Uuid::parse_str(info.as_str()).ok();
    filters.provider_uuid = match claims.0 {
        Some(c) => uuid::Uuid::parse_str(c.provider_uuid.as_str()).unwrap(),
        None => uuid::Uuid::nil(),
    };
    let items = db::get_items(&client, &filters).await.unwrap();
    println!(
        "got items from store: {}",
        shared_now(None).elapsed().as_millis()
    );
    let mut features = vec![];

    for item in items {
        //let geo = Option::<geo_types::Geometry<f64>>::from_postgis(&item.geometry).unwrap();
        //let geo_value = geojson::Value::from(geo);
        //let geojson_geometry = geojson::Geometry::new(geo_value);

        let geojson_geometry = match &item.geometry {
            Some(v) => Some(geojson::Geometry::new(geojson::Value::from(v))),
            None => None,
        };
        let properties = item.properties.as_object().unwrap().to_owned();
        let feature = geojson::Feature {
            bbox: None,
            geometry: geojson_geometry,
            id: Some(geojson::feature::Id::String(item.uuid.unwrap().to_string())),
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
        features,
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

    Ok(HttpResponse::Ok().body(geojson))
}
