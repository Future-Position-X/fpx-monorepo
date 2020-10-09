from typing import Any, Dict, List, Optional, Sequence, Union

import yaml
from deepmerge import conservative_merger
from pydantic.schema import get_model_name_map
from starlette.routing import BaseRoute

from fastapi import routing
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.models import OpenAPI
from fastapi.openapi.utils import get_flat_models_from_routes, get_openapi_path
from fastapi.utils import get_model_definitions

geojson_file = open("geojson.yaml")
geojson = yaml.load(geojson_file, Loader=yaml.FullLoader)
print(geojson)


def get_openapi(
    *,
    title: str,
    version: str,
    openapi_version: str = "3.0.2",
    description: Optional[str] = None,
    routes: Sequence[BaseRoute],
    tags: Optional[List[Dict[str, Any]]] = None,
    servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
) -> Dict:
    info = {"title": title, "version": version}
    if description:
        info["description"] = description
    output: Dict[str, Any] = {"openapi": openapi_version, "info": info}
    if servers:
        output["servers"] = servers
    components: Dict[str, Dict] = {}
    paths: Dict[str, Dict] = {}
    flat_models = get_flat_models_from_routes(routes)
    # ignore mypy error until enum schemas are released
    model_name_map = get_model_name_map(flat_models)  # type: ignore
    # ignore mypy error until enum schemas are released
    definitions = get_model_definitions(
        flat_models=flat_models, model_name_map=model_name_map  # type: ignore
    )
    for route in routes:
        if isinstance(route, routing.APIRoute):
            result = get_openapi_path(route=route, model_name_map=model_name_map)
            if result:
                path, security_schemes, path_definitions = result
                if path:
                    old_path = paths.get(route.path_format, {})  # New
                    new_path = conservative_merger.merge(old_path, path)  # New
                    paths[route.path_format] = new_path  # New
                    # paths.setdefault(route.path_format, {}).update(path)  # Old
                if security_schemes:
                    components.setdefault("securitySchemes", {}).update(
                        security_schemes
                    )
                if path_definitions:
                    definitions.update(path_definitions)
    if definitions:
        definitions.update(geojson)
        components["schemas"] = {k: definitions[k] for k in sorted(definitions)}
    if components:
        output["components"] = components
    output["paths"] = paths
    if tags:
        output["tags"] = tags
    return jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)
