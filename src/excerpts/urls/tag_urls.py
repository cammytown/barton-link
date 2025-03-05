from django.urls import path

from ..views.tags.tag_views import (
    tags, tag, create_tag, edit_tag, split_tag,
    add_split_field, toggle_tag
)
from ..views.tags.tag_types_views import (
    tag_types, tag_type, create_tag_type, edit_tag_type
)

urlpatterns = [
    path("tags", tags, name="tags"),
    path("tags/create", create_tag, name="create_tag"),
    path("tags/<int:tag_id>", tag, name="tag"),
    path("tags/<int:tag_id>/edit", edit_tag, name="tag"),
    path("tags/<int:tag_id>/split", split_tag, name="split_tag"),
    path("tags/<int:tag_id>/split/add-split-field",
         add_split_field,
         name="add_split_field"),
    path("tags/<int:tag_id>/toggle", toggle_tag, name="toggle_tag"),
    # path("tag/<int:tag_id>/merge", views.merge_tag, name="merge_tag"),

    path("tag-types", tag_types, name="tag_types"),
    path("tag-types/create", create_tag_type, name="create_tag_type"),
    path("tag-types/<int:tag_type_id>", tag_type, name="tag_type"),
    path("tag-types/<int:tag_type_id>/edit",
         edit_tag_type,
         name="edit_tag_type"),
] 