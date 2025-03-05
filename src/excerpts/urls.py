from django.urls import path
from django.urls.conf import include

# Import views directly from their feature directories
from .views.excerpts.excerpt_views import (
    index, search, excerpt, create_excerpt, 
    add_tag, add_autotag, remove_tag
)
from .views.entities.entity_views import (
    entities, entity, create_entity
)
from .views.relationships.relationship_views import (
    relationship, create_relationship, delete_relationship
)
from .views.relationships.relationship_form_views import (
    relationship_form, create_relationship_form, 
    create_entity_relationship_form, relationship_preview
)
from .views.relationships.relationship_type_views import (
    create_relationship_type
)
from .views.tags.tag_views import (
    tags, tag, create_tag, edit_tag, split_tag,
    add_split_field, toggle_tag
)
from .views.tags.tag_types_views import (
    tag_types, tag_type, create_tag_type, edit_tag_type
)
from .views.tools.tools_views import (
    tools, create_default_relationship_types
)
from .views.tools.similarity_views import (
    analyze_similarities, start_similarity_analysis, 
    stop_similarity_analysis, get_analysis_progress
)
from .views.tools.autotag_views import (
    autotag_excerpts, start_autotag, stop_autotag, get_autotag_progress
)
from .views.imports.import_views import (
    import_excerpts, import_file, import_text,
    import_gdocs, import_excerpts_confirm
)
from .views.imports.gdocs_handler import gdocs_test

excerpt_patterns = [
    path("add_tag/<int:tag_id>", add_tag, name="add_tag"),
    path("add_autotag/<int:tag_id>", add_autotag, name="add_autotag"),
    path("remove_tag/<int:tag_id>", remove_tag, name="remove_tag"),
]

urlpatterns = [
    path("", index, name="index"),
    path("search", search, name="search"),

    path("excerpt/<int:excerpt_id>", excerpt, name="excerpt_detail"),
    path("excerpt/<int:excerpt_id>/", include(excerpt_patterns), name="excerpt"),
    path("excerpt/create", create_excerpt, name="create_excerpt"),

    path("entities", entities, name="entities"),
    path("entities/create", create_entity, name="create_entity"),
    path("entity/<int:entity_id>", entity, name="entity_detail"),

    path("relationships/create", create_relationship, name="create_relationship"),
    path("relationships/create_type", create_relationship_type, name="create_relationship_type"),
    path("relationships/preview", relationship_preview, name="relationship_preview"),

    # Consolidated relationship view - RESTful approach
    # For excerpt-based relationships
    path("relationships/<str:rel_type>/<int:excerpt_id>", 
         relationship, 
         name="relationship"),
    # For entity-based relationships
    path("relationships/<str:rel_type>/entity/<int:entity_id>", 
         relationship, 
         name="entity_relationship"),
    # For deleting relationships
    path("relationships/<str:rel_type>/<int:relationship_id>/delete", 
         relationship, 
         name="relationship_delete"),
    # Separate URL for relationship form - excerpt-based
    path("relationships/<str:rel_type>/<int:excerpt_id>/form", 
         relationship_form, 
         name="relationship_form"),
    # Separate URL for relationship form - entity-based
    path("relationships/<str:rel_type>/entity/<int:entity_id>/form", 
         relationship_form, 
         name="entity_relationship_form"),

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

    path("tools", tools, name="tools"),

    path("autotag", autotag_excerpts, name="autotag"),

    # path("autotag/<int:excerpt_id>", views.autotag_excerpts, name="autotag"),
    path("start-autotag", start_autotag, name="start_autotag"),
    path("stop-autotag", stop_autotag, name="stop_autotag"),
    path("get-autotag-progress",
            get_autotag_progress,
            name="get_autotag_progress"),

    path("analyze-similarities",
         analyze_similarities,
         name="analyze_similarities"),
    path("start-similarity-analysis",
         start_similarity_analysis,
         name="start_similarity_analysis"),
    path("stop-similarity-analysis",
         stop_similarity_analysis,
         name="stop_similarity_analysis"),
    path("get-analysis-progress",
         get_analysis_progress,
         name="get_analysis_progress"),

    path("create-default-relationship-types",
            create_default_relationship_types,
            name="create_default_relationship_types"),

    path("import", import_excerpts, name="import"),
    path("import/file-upload", import_file, name="import_file_upload"),
    path("import/text-paste", import_text, name="import_text_paste"),
    path("import/gdocs", import_gdocs, name="import_gdocs"),
    path("confirm-import", import_excerpts_confirm, name="import_confirm"),

    path("gdocs-test", gdocs_test, name="test"),
]
