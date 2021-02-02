from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple
from uuid import UUID

import sqlalchemy as sa
import sqlalchemy_mixins
from geoalchemy2 import Geometry
from sqlalchemy import Column, and_, func, or_
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.orm import Query, relationship

from app.dto import Access, InternalUserDTO, ItemDTO
from app.models import Collection
from app.models.acl import ACL
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from .series import Series  # noqa: F401


class Item(BaseModel):
    __tablename__ = "items"

    uuid = sa.Column(
        pg.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
        unique=True,
        nullable=False,
    )
    geometry = sa.Column(Geometry(geometry_type="GEOMETRY"))
    properties = sa.Column(pg.JSONB)

    collection_uuid = sa.Column(
        pg.UUID(as_uuid=True),
        sa.ForeignKey("collections.uuid", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    collection = relationship("Collection", back_populates="items")
    series = relationship("Series", back_populates="item",
        cascade="all, delete",
        passive_deletes=True)

    @staticmethod
    def append_property_filter_to_where_clause(
        where_clause: str, property_filter: str, execute_dict: dict
    ) -> str:
        params = property_filter.split(",")

        for i, p in enumerate(params):
            tokens = p.split("=")
            name = "name_" + str(i)
            value = "value_" + str(i)

            where_clause += " properties->>:" + name + " = :" + value
            execute_dict[name] = tokens[0]
            execute_dict[value] = tokens[1]

            if i < (len(params) - 1):
                where_clause += " AND"

        return where_clause

    @staticmethod
    def create_where(filters: dict) -> Tuple[str, Dict[str, Optional[Any]]]:
        where = """
        (
            collections.is_public=true
            OR collections.provider_uuid = :provider_uuid
            OR ((acls.collection_uuid = collections.uuid OR acls.item_uuid = items.uuid) AND acls.access = 'read')
        )"""

        if filters.get("collection_uuid"):
            where += " AND items.collection_uuid = :collection_uuid"

        if filters.get("collection_name"):
            where += " AND collections.name = :collection_name"

        if filters["valid"]:
            where += " AND ST_IsValid(geometry)"

        if (
            filters["spatial_filter"]
            and filters["spatial_filter"]["filter"] == "within-distance"
        ):
            where += """
            AND ST_DWithin(
                geometry,
                :distance_point,
                :distance_d,
                False
            )
            """

        if (
            filters["spatial_filter"]
            and filters["spatial_filter"]["filter"] == "intersect"
        ):
            if "envelope" in filters["spatial_filter"]:
                where += """
                AND ST_Intersects(
                    geometry,
                    ST_MakeEnvelope(:envelope_xmin, :envelope_ymin, :envelope_xmax, :envelope_ymax)
                )
                """
            else:
                where += """
                AND ST_Intersects(
                    geometry,
                    ST_MakePoint(:point_x, :point_y)
                )
                """

        if (
            filters["spatial_filter"]
            and filters["spatial_filter"]["filter"] == "within"
        ):
            if "envelope" in filters["spatial_filter"]:
                where += """
                AND ST_Within(
                    geometry,
                    ST_MakeEnvelope(:envelope_xmin, :envelope_ymin, :envelope_xmax, :envelope_ymax)
                )
                """
            else:
                where += """
                AND ST_Intersects(
                    geometry,
                    ST_MakePoint(:point_x, :point_y)
                )
                """

        exec_dict = {
            "provider_uuid": filters.get("provider_uuid"),
            "collection_uuid": filters.get("collection_uuid"),
            "collection_name": filters.get("collection_name"),
            "offset": filters["offset"],
            "limit": filters["limit"],
        }

        if filters["spatial_filter"] and filters["spatial_filter"]["filter"] in [
            "within",
            "intersect",
        ]:
            if "envelope" in filters["spatial_filter"]:
                exec_dict.update(
                    {
                        "envelope_xmin": filters["spatial_filter"]["envelope"]["xmin"],
                        "envelope_ymin": filters["spatial_filter"]["envelope"]["ymin"],
                        "envelope_xmax": filters["spatial_filter"]["envelope"]["xmax"],
                        "envelope_ymax": filters["spatial_filter"]["envelope"]["ymax"],
                    }
                )
            else:
                exec_dict.update(
                    {
                        "point_x": filters["spatial_filter"]["point"]["x"],
                        "point_y": filters["spatial_filter"]["point"]["y"],
                    }
                )

        if filters["spatial_filter"] and filters["spatial_filter"]["filter"] in [
            "within-distance"
        ]:
            exec_dict.update(
                {
                    "distance_point": filters["spatial_filter"]["distance"][
                        "point"
                    ].wkt,
                    "distance_d": filters["spatial_filter"]["distance"]["d"],
                }
            )

        if filters["property_filter"] is not None:
            where += " AND "
            where = Item.append_property_filter_to_where_clause(
                where, filters["property_filter"], exec_dict
            )

        if filters.get("collection_uuids", None) is not None:
            where += " AND ("

            for i, collection_uuid in enumerate(filters["collection_uuids"]):
                where += "items.collection_uuid = :collection_uuid_" + str(i)

                if i < (len(filters["collection_uuids"]) - 1):
                    where += " OR "

                exec_dict["collection_uuid_" + str(i)] = collection_uuid

            where += ")"

        return where, exec_dict

    @classmethod
    def find_readable_by_collection_name(
        cls,
        user: InternalUserDTO,
        collection_name: str,
        filters: dict,
        transforms: dict,
    ) -> List[ItemDTO]:
        user_uuid = user.uuid
        provider_uuid = user.provider_uuid
        filters["provider_uuid"] = provider_uuid
        filters["collection_name"] = collection_name
        where, exec_dict = cls.create_where(filters)
        result = (
            cls.session.query(
                cls.uuid,
                cls.simplified_geometry(transforms.get("simplify", 0.0)),
                cls.properties,
                cls.collection_uuid,
                cls.created_at,
                cls.updated_at,
                cls.revision,
            )
            .join(Item.collection)
            .outerjoin(
                ACL,
                or_(
                    ACL.granted_provider_uuid == provider_uuid,
                    ACL.granted_user_uuid == user_uuid,
                ),
            )
            .filter(sa.text(where))
            .params(exec_dict)
            .limit(filters["limit"])
            .offset(filters["offset"])
            .all()
        )
        result = [
            ItemDTO(**dict(zip(res.keys(), res)))
            for res in result
            if filters["valid"] is not True or res[1] is not None
        ]
        return result

    @classmethod
    def simplified_geometry(cls, simplify: float) -> Column:
        return (
            cls.geometry
            if simplify == 0.0
            else func.ST_Simplify(cls.geometry, simplify, True).label("geometry")
        )

    @classmethod
    def find_readable(
        cls, user: InternalUserDTO, filters: dict, transforms: dict
    ) -> List[ItemDTO]:
        user_uuid = user.uuid
        provider_uuid = user.provider_uuid
        filters["provider_uuid"] = provider_uuid
        where, exec_dict = cls.create_where(filters)
        result = (
            cls.session.query(
                cls.uuid,
                cls.simplified_geometry(transforms.get("simplify", 0.0)),
                cls.properties,
                cls.collection_uuid,
                cls.created_at,
                cls.updated_at,
                cls.revision,
            )
            .join(Item.collection)
            .outerjoin(
                ACL,
                or_(
                    ACL.granted_provider_uuid == provider_uuid,
                    ACL.granted_user_uuid == user_uuid,
                ),
            )
            .filter(sa.text(where))
            .params(exec_dict)
            .limit(filters["limit"])
            .offset(filters["offset"])
            .all()
        )
        result = [
            ItemDTO(**dict(zip(res.keys(), res)))
            for res in result
            if filters["valid"] is False or res[1] is not None
        ]
        return result

    @classmethod
    def find_readable_by_collection_uuid(
        cls,
        user: InternalUserDTO,
        collection_uuid: UUID,
        filters: dict,
        transforms: dict = {},
    ) -> List[ItemDTO]:
        user_uuid = user.uuid
        provider_uuid = user.provider_uuid
        filters["provider_uuid"] = provider_uuid
        filters["collection_uuid"] = collection_uuid
        where, exec_dict = cls.create_where(filters)
        result = (
            cls.session.query(
                cls.uuid,
                cls.simplified_geometry(transforms.get("simplify", 0.0)),
                cls.properties,
                cls.collection_uuid,
                cls.created_at,
                cls.updated_at,
                cls.revision,
            )
            .join(Item.collection)
            .outerjoin(
                ACL,
                or_(
                    ACL.granted_provider_uuid == provider_uuid,
                    ACL.granted_user_uuid == user_uuid,
                ),
            )
            .filter(sa.text(where))
            .params(exec_dict)
            .limit(filters["limit"])
            .offset(filters["offset"])
            .all()
        )
        result = [
            ItemDTO(**dict(zip(res.keys(), res)))
            for res in result
            if filters["valid"] is False or res[1] is not None
        ]
        return result

    @classmethod
    def find_readable_or_fail(
        cls,
        user: InternalUserDTO,
        item_uuid: UUID,
        collection_uuid: Optional[UUID] = None,
    ) -> Item:
        user_uuid = user.uuid
        provider_uuid = user.provider_uuid
        q = cls.query.outerjoin(
            ACL,
            or_(
                ACL.granted_provider_uuid == provider_uuid,
                ACL.granted_user_uuid == user_uuid,
            ),
        ).filter(cls.uuid == item_uuid)
        if collection_uuid is not None:
            q = q.filter(cls.collection_uuid == collection_uuid)

        q = q.filter(
            or_(
                Item.collection.has(is_public=True),
                Item.collection.has(provider_uuid=provider_uuid),
                and_(
                    or_(
                        ACL.collection_uuid == Item.collection_uuid,
                        ACL.item_uuid == Item.uuid,
                    ),
                    ACL.access == Access.READ.value,
                ),
            )
        )

        res = q.first()
        if res is None:
            raise sqlalchemy_mixins.ModelNotFoundError
        return res

    @classmethod
    def writeable_query_subquery(cls, user: InternalUserDTO) -> Query:
        user_uuid = user.uuid
        provider_uuid = user.provider_uuid
        q = (
            cls.session.query(cls.uuid)
            .outerjoin(
                ACL,
                or_(
                    ACL.granted_provider_uuid == provider_uuid,
                    ACL.granted_user_uuid == user_uuid,
                ),
            )
            .filter(
                or_(
                    Collection.provider_uuid == provider_uuid,
                    and_(
                        or_(
                            ACL.collection_uuid == Item.collection_uuid,
                            ACL.item_uuid == Item.uuid,
                        ),
                        ACL.access == Access.WRITE.value,
                    ),
                )
            )
        )
        return q.subquery()

    @classmethod
    def writeable_query(
        cls,
        user: InternalUserDTO,
        item_uuid: UUID,
        collection_uuid: Optional[UUID] = None,
    ) -> Query:
        writeable_sq = cls.writeable_query_subquery(user)
        q = cls.query.filter(cls.uuid == item_uuid)
        if collection_uuid is not None:
            q = q.filter(Collection.uuid == collection_uuid)
        q = q.filter(cls.uuid.in_(writeable_sq))
        return q

    @classmethod
    def delete_writeable(
        cls,
        user: InternalUserDTO,
        item_uuid: UUID,
        collection_uuid: Optional[UUID] = None,
    ) -> None:
        q = cls.writeable_query(user, item_uuid, collection_uuid)
        q.delete(synchronize_session=False)
        cls.session.commit()
        cls.session.expire_all()

    # TODO: Perhaps use JOIN instead of SUBQUERY
    @classmethod
    def find_writeable_or_fail(
        cls,
        user: InternalUserDTO,
        item_uuid: UUID,
        collection_uuid: Optional[UUID] = None,
    ) -> Item:
        q = cls.writeable_query(user, item_uuid, collection_uuid)
        res = q.first()
        if res is None:
            raise sqlalchemy_mixins.ModelNotFoundError
        return res

    @classmethod
    def find_writeable(
        cls, user: InternalUserDTO, item_uuids: Optional[List[UUID]] = None
    ) -> List[Item]:
        writeable_sq = cls.writeable_query_subquery(user)
        q = cls.query.filter(cls.uuid.in_(writeable_sq))
        if item_uuids is not None:
            q = q.filter(cls.uuid.in_(item_uuids))
        res = q.all()
        return res

    @classmethod
    def find_writeable_by_collection_uuid(
        cls,
        user: InternalUserDTO,
        collection_uuid: UUID,
        item_uuids: Optional[List[UUID]] = None,
    ) -> List[Item]:
        writeable_sq = cls.writeable_query_subquery(user)
        q = cls.query.filter(Collection.uuid == collection_uuid)
        q = q.filter(cls.uuid.in_(writeable_sq))
        if item_uuids is not None:
            q = q.filter(cls.uuid.in_(item_uuids))
        res = q.all()
        return res

    @classmethod
    def delete_by_collection_uuid(
        cls, user: InternalUserDTO, collection_uuid: UUID
    ) -> None:
        owned_sq = cls.writeable_query_subquery(user)
        q = cls.query.filter(Collection.uuid == collection_uuid)
        q = q.filter(cls.uuid.in_(owned_sq))
        q.delete(synchronize_session=False)
        cls.session.commit()
        cls.session.expire_all()

    @classmethod
    def copy_items(cls, src_collection_uuid: UUID, dest_collection_uuid: UUID) -> None:
        cls.session.execute(
            """
            INSERT INTO items (collection_uuid, geometry, properties)
                SELECT :dest_collection_uuid, geometry, properties
                FROM items WHERE collection_uuid = :src_collection_uuid
            """,
            {
                "src_collection_uuid": src_collection_uuid,
                "dest_collection_uuid": dest_collection_uuid,
            },
        )
