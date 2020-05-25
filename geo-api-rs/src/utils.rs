use lazy_static::lazy_static;
use std::sync::{Arc, Mutex};
use std::time::Instant;

lazy_static! {
    static ref SHARED_NOW: Mutex<Arc<Instant>> = Mutex::new(Arc::new(Instant::now()));
}

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
