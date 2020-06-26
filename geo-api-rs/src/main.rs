mod db;
mod errors;
mod handlers;
mod middlewares;
mod models;
mod store;

mod config;

mod utils {
    lazy_static! {
        static ref SHARED_NOW: Mutex<Arc<Instant>> = Mutex::new(Arc::new(Instant::now()));
    }
    use lazy_static::lazy_static;
    use std::sync::{Arc, Mutex};
    use std::time::Instant;

    pub fn shared_now(instant_opt: Option<Instant>) -> Instant {
        match instant_opt {
            Some(instant) => {
                let mut lock = SHARED_NOW.lock().unwrap();
                let inner = Arc::new(instant);
                *lock = inner.clone();
                *inner
            }
            None => {
                let lock = SHARED_NOW.lock().unwrap();
                *lock.clone()
            }
        }
    }
}

use crate::handlers::{
    create_session, get_collection, get_collections, get_items, get_user, get_user_uuid,
    post_items, put_items,
};
use actix_web::middleware::{Compress, Logger};

use actix_cors::Cors;
use actix_web::{web, App, HttpServer};

use dotenv::dotenv;
use handlers::get_users;

use tokio_postgres::NoTls;

#[actix_rt::main]
async fn main() -> std::io::Result<()> {
    dotenv().ok();
    std::env::set_var("RUST_LOG", "actix_web=debug");
    env_logger::init();
    let config = crate::config::Config::from_env().unwrap();
    let server_addr = config.server_addr.clone();
    let pool = config.pg.create_pool(NoTls).unwrap();
    let server = HttpServer::new(move || {
        App::new()
            .wrap(Logger::default())
            .wrap(Cors::default())
            .wrap(Compress::default())
            .data(pool.clone())
            .app_data(config.clone())
            .app_data(web::PayloadConfig::default().limit(usize::max_value()))
            .service(web::resource("/sessions").route(web::post().to(create_session)))
            .service(
                web::scope("/users")
                    .service(web::resource("").route(web::get().to(get_users)))
                    .service(web::resource("/uuid").route(web::get().to(get_user_uuid)))
                    .service(web::resource("/{user_uuid}").route(web::get().to(get_user))),
            )
            .service(
                web::scope("/collections")
                    .service(web::resource("").route(web::get().to(get_collections)))
                    .service(
                        web::scope("/{collection_uuid}")
                            .service(web::resource("").route(web::get().to(get_collection)))
                            .service(
                                web::scope("/items").service(
                                    web::resource("")
                                        .route(web::get().to(get_items))
                                        .route(web::post().to(post_items))
                                        .route(web::put().to(put_items)),
                                ),
                            ),
                    ),
            )
    })
    .bind(&server_addr)?
    .run();
    println!("Server running at http://{}/", &server_addr);

    server.await
}
