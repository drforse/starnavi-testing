from typing import TypeVar, Callable

from sqlalchemy.orm import selectinload, lazyload, subqueryload, joinedload, raiseload, noload
from sqlalchemy.sql import Select, Delete, Update, Insert

QueryType = TypeVar("QueryType", Select, Delete, Update, Insert)

SA_LOADINGS: dict[str, Callable] = {
    "selectin": selectinload,
    "select": lazyload,
    "subquery": subqueryload,
    "joined": joinedload,
    "raise": raiseload,
    "raise_on_sql": raiseload,
    "noload": noload
}


SA_LOADINGS_NAMES = {"selectin": "selectinload",
                     "select": "lazyload",
                     "subquery": "subqueryload",
                     "joined": "joinedload",
                     "raise": "raiseload",
                     "raise_on_sql": "raiseload",
                     "noload": "noload"}

DEFAULT_SA_LOADING = "selectin"


def add_loading_to_query(
        query: QueryType,
        *args: str,
        sa_loading: str = DEFAULT_SA_LOADING) -> QueryType:
    """
    :param query: should be one of: Select, Delete, Insert, Update
    :param sa_loading: selectin, select, subquery, joined, raise, raise_on_sql, noload
    :return:
    """
    sa_loads = SA_LOADINGS.get(sa_loading)
    if sa_loads is None:
        raise ValueError(f"sa_loading {sa_loading} not found")
    for arg in args:
        first_step, *steps = arg.split(".")
        load = sa_loads(first_step)
        for step in steps:
            load = getattr(load, SA_LOADINGS_NAMES[sa_loading])(step)
        query = query.options(load)
    return query
