# This file is intentionally left empty.
# Views should be imported directly from their modules.

# Import all views from the entity_views module
from .entity_views import (
    entities,
    entity,
    create_entity,
    create_entity_htmx,
)

__all__ = [
    'entities',
    'entity',
    'create_entity',
    'create_entity_htmx',
]
