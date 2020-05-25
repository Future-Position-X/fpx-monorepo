use crate::models::Item;
use crate::utils::shared_now;
use geo_postgis::FromPostgis;
use postgres::{Client, NoTls};

pub fn get_items() -> Vec<Item> {
    let mut client = Client::connect(
        format!(
            "host={} port={} dbname={} user={} password={}",
            "gia-dev.cjesin4yac8j.eu-north-1.rds.amazonaws.com",
            5432,
            "gia",
            "master",
            "lN1Pb60MO6sC",
        )
        .as_str(),
        NoTls,
    )
    .unwrap();
    println!(
        "client connected: {}",
        shared_now(None).elapsed().as_millis()
    );

    let mut items: Vec<Item> = vec![];
    let sql = "
SELECT uuid, geometry, properties
FROM public.items
WHERE collection_uuid = '08f8a8e1-f13a-4b61-9d27-4073aabfc976'
OFFSET 0
LIMIT 1000000;
    ";
    let mut first = true;
    for row in client.query(sql, &[]).unwrap() {
        if first {
            println!("first row: {}", shared_now(None).elapsed().as_millis());
            first = false;
        }
        let id = row.get(0);
        let geometry: postgis::ewkb::Geometry = row.get(1);
        let properties = row.get(2);

        items.push(Item {
            id: id,
            geometry: Option::<geo_types::Geometry<f64>>::from_postgis(&geometry).unwrap(),
            properties: properties,
        });
    }
    println!(
        "last row({}): {}",
        items.len(),
        shared_now(None).elapsed().as_millis()
    );
    items
}
