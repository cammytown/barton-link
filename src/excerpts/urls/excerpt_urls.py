from django.urls import path, include

from ..views.excerpts.excerpt_views import (
    index, search, excerpt, create_excerpt, 
    add_tag, add_autotag, remove_tag
)

# URLs for actions on a specific excerpt
excerpt_patterns = [
    path("add_tag/<int:tag_id>", add_tag, name="add_tag"),
    path("add_autotag/<int:tag_id>", add_autotag, name="add_autotag"),
    path("remove_tag/<int:tag_id>", remove_tag, name="remove_tag"),
]

# Main excerpt URL patterns
urlpatterns = [
    path("", index, name="index"),
    path("search", search, name="search"),
    path("excerpt/<int:excerpt_id>", excerpt, name="excerpt_detail"),
    path("excerpt/<int:excerpt_id>/", include(excerpt_patterns), name="excerpt"),
    path("excerpt/create", create_excerpt, name="create_excerpt"),
] 