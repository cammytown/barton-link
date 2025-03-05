# This file is intentionally left empty.
# Views should be imported directly from their modules.

# Import views from tag_views.py
from .tag_views import (
    tags,
    tags_htmx,
    tags_html,
    tag,
    tag_html,
    tag_htmx,
    create_tag,
    edit_tag,
    split_tag,
    toggle_tag,
    add_split_field,
)

# Import views from tag_types_views.py
from .tag_types_views import (
    tag_type,
    tag_type_html,
    tag_type_htmx,
    create_tag_type,
    edit_tag_type,
    tag_types,
    tag_types_html,
    tag_types_htmx,
)

__all__ = [
    # Tag views
    'tags',
    'tags_htmx',
    'tags_html',
    'tag',
    'tag_html',
    'tag_htmx',
    'create_tag',
    'edit_tag',
    'split_tag',
    'toggle_tag',
    'add_split_field',
    
    # Tag type views
    'tag_type',
    'tag_type_html',
    'tag_type_htmx',
    'create_tag_type',
    'edit_tag_type',
    'tag_types',
    'tag_types_html',
    'tag_types_htmx',
]
