import abc

from sqlalchemy.sql import Insert, Update
from sqlalchemy.dialects.mysql.dml import insert

from ..base import BaseRepository, ModelType, ModelCreateType, BaseRepositoryGeneric
from ...models.base import BaseModelBase


class MySqlBaseRepository(BaseRepository, BaseRepositoryGeneric[ModelType, ModelCreateType], abc.ABC):

    def resolve_relationships(self, entity: ModelType | ModelCreateType) -> list[Insert | Update]:
        result = []
        if self._field_chains is None:
            return []
        for chain in self._field_chains:
            relation, *following = chain.split(".")
            try:
                sub_entity = getattr(entity, relation)
            except AttributeError:
                raise ValueError(f"field {relation} doesn't exist on {entity.__class__.__name__}")
            if sub_entity is not None:
                result += self._resolve_relations(sub_entity, *following)

        return result

    def _resolve_relations(self, entity: BaseModelBase, *relations) -> list[Insert | Update]:
        results = []
        while True:
            relation = relations[0] if relations else None
            following = relations[1:]
            if entity is None:
                break
            if isinstance(entity, list):
                for sub_entity in entity:
                    results += self._resolve_relations(sub_entity, relation, *following)
                break

            insert_exclude = entity.__relationship_fields__
            if hasattr(entity, "id") is True:
                insert_exclude = insert_exclude.union({"id"})
            results.append(
                insert(entity.__sa_model__).values(
                    entity.dict(exclude=insert_exclude, show_secrets=True)
                ).on_duplicate_key_update(
                    entity.dict(exclude=entity.__relationship_fields__, exclude_unset=True, show_secrets=True)
                )
            )
            if not relation:
                break
            entity = getattr(entity, relation, None)  # type: ignore

        return results
