# Future Position X monorepo

## tl;dr

This repository includes those primary projects:

* Frontend [geo-editor](http://editor.dev.gia.fpx.se) [(src)](geo-editor/)
* Backend [geo-api](http://dev.gia.fpx.se/docs) [(src)](geo-api/)

### Architecture

```plantuml :architecture
@startuml

package "Frontends" {
  [geo-editor]
  [geo-api-docs]
}

node "Apis" {
  [geo-api]
}

node "Backend applications" {
  [geo-api-impl] as geoApp
}

database "Databases" {
    [Postgis(geo)] as geoDb
}

[geo-editor] ==> [geo-api]
[geo-api-docs] ==> [geo-api]
[geo-api] ==> geoApp
geoApp ==> geoDb
gg ==> gg
@enduml

```

![Architecture](diagrams/architecture.svg)
