use crate::config::Config;
use crate::models::{Claims, MyClaims};
use actix_web::dev::Payload;
use actix_web::error::ErrorUnauthorized;
use actix_web::FromRequest;
use actix_web::{Error, HttpRequest};
use futures::future::{err, ok, Ready};
use jsonwebtoken::{decode, Algorithm, DecodingKey, Validation};

impl FromRequest for MyClaims {
    type Error = Error;
    type Future = Ready<Result<MyClaims, Error>>;
    type Config = ();

    fn from_request(_req: &HttpRequest, _payload: &mut Payload) -> Self::Future {
        let _auth = _req.headers().get("Authorization");
        match _auth {
            Some(_) => {
                let _split: Vec<&str> = _auth.unwrap().to_str().unwrap().split("Bearer").collect();
                let token = _split[1].trim();
                let _var = &_req.app_data::<Config>().unwrap().jwt_secret;
                let key = _var.as_bytes();
                match decode::<Claims>(
                    token,
                    &DecodingKey::from_secret(key),
                    &Validation::new(Algorithm::HS256),
                ) {
                    Ok(_token) => ok(MyClaims(Some(_token.claims))),
                    Err(_e) => err(ErrorUnauthorized("invalid token!")),
                }
            }
            None => ok(MyClaims(None)),
        }
    }
}
