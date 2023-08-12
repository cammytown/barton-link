from django.urls import path
from django.urls.conf import include

from . import views

excerpt_patterns = [
    path("add_tag/<int:tag_id>", views.add_tag, name="add_tag"),
    path("add_autotag/<int:tag_id>", views.add_autotag, name="add_autotag"),
    path("remove_tag/<int:tag_id>", views.remove_tag, name="remove_tag"),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),

    path("excerpt/<int:excerpt_id>", views.excerpt, name="excerpt"),
    path("excerpt/<int:excerpt_id>/", include(excerpt_patterns), name="excerpt"),

    path("tags", views.tags, name="tags"),
    path("tags/create", views.create_tag, name="create_tag"),
    path("tags/<int:tag_id>", views.tag, name="tag"),
    path("tags/<int:tag_id>/edit", views.edit_tag, name="tag"),
    path("tags/<int:tag_id>/split", views.split_tag, name="split_tag"),
    path("tags/<int:tag_id>/split/add-split-field",
         views.add_split_field,
         name="add_split_field"),
    path("tags/<int:tag_id>/toggle", views.toggle_tag, name="toggle_tag"),
    # path("tag/<int:tag_id>/merge", views.merge_tag, name="merge_tag"),

    path("tag-types", views.tag_types, name="tag_types"),
    path("tag-types/create", views.create_tag_type, name="create_tag_type"),
    path("tag-types/<int:tag_type_id>", views.tag_type, name="tag_type"),
    path("tag-types/<int:tag_type_id>/edit",
         views.edit_tag_type,
         name="edit_tag_type"),

    path("tools", views.tools, name="tools"),
    path("autotag/", views.autotag_excerpts, name="autotag"),
    path("autotag/<int:excerpt_id>", views.autotag_excerpts, name="autotag"),

    path("analyze-similarities",
         views.analyze_similarities,
         name="analyze_similarities"),
    path("start-similarity-analysis",
         views.start_similarity_analysis,
         name="start_similarity_analysis"),
    path("stop-similarity-analysis",
         views.stop_similarity_analysis,
         name="stop_similarity_analysis"),
    path("get-analysis-progress",
         views.get_analysis_progress,
         name="get_analysis_progress"),

    path("import", views.import_excerpts, name="import"),
    path("import/file-upload", views.import_file, name="import_file_upload"),
    path("import/text-paste", views.import_text, name="import_text_paste"),
    path("import/gdocs", views.import_gdocs, name="import_gdocs"),
    path("confirm-import", views.import_excerpts_confirm, name="import_confirm"),

    path("gdocs-test", views.gdocs_test, name="test"),
]
