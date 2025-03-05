# This file is intentionally left empty.
# Views should be imported directly from their modules.

# Import all views from the excerpt_views module
from .excerpt_views import (
    index,
    search,
    excerpt,
    excerpt_html,
    excerpt_htmx,
    create_excerpt,
    add_tag,
    add_autotag,
    remove_tag,
)

__all__ = [
    'index',
    'search',
    'excerpt',
    'excerpt_html',
    'excerpt_htmx',
    'create_excerpt',
    'add_tag',
    'add_autotag',
    'remove_tag',
]
