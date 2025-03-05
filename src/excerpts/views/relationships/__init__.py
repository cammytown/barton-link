# This file is intentionally left empty.
# Views should be imported directly from their modules.

# Import views from relationship_views.py
from .relationship_views import (
    relationship,
    relationship_html,
    relationship_htmx,
    list_relationships,
    list_entity_relationships,
    create_relationship,
    delete_relationship,
)

# Import views from relationship_form_views.py
from .relationship_form_views import (
    relationship_form,
    create_relationship_form,
    create_entity_relationship_form,
    relationship_preview,
)

# Import views from relationship_type_views.py
from .relationship_type_views import (
    create_relationship_type,
    create_relationship_type_htmx,
)

__all__ = [
    # Core relationship views
    'relationship',
    'relationship_html',
    'relationship_htmx',
    'list_relationships',
    'list_entity_relationships',
    'create_relationship',
    'delete_relationship',
    
    # Form-related views
    'relationship_form',
    'create_relationship_form',
    'create_entity_relationship_form',
    'relationship_preview',
    
    # Relationship type views
    'create_relationship_type',
    'create_relationship_type_htmx',
]
