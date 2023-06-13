from django.urls import path
from django.urls.conf import include

from . import views

excerpt_patterns = [
    path("", views.excerpt, name="excerpt"),
    path("edit/", views.edit, name="edit"),
    path("delete/", views.delete, name="delete"),

    path("add_tag/<int:tag_id>", views.add_tag, name="add_tag"),
    path("add_autotag/<int:tag_id>", views.add_autotag, name="add_autotag"),
    path("remove_tag/<int:tag_id>", views.remove_tag, name="remove_tag"),

    path("add_project", views.add_project, name="add_project"),
    path("add_project/<int:project_id>", views.add_project, name="add_project"),
    path("remove_project/<int:project_id>", views.remove_project, name="remove_project"),
]

urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),

    path("excerpt/<int:excerpt_id>/", include(excerpt_patterns), name="excerpt"),

    path("tag/<int:tag_id>", views.tag, name="tag"),

    path("autotag/", views.autotag_excerpts, name="autotag"),
    path("autotag/<int:excerpt_id>", views.autotag_excerpts, name="autotag"),
    # path("analyze-similarities/", views.analyze_similarities, name="analyze_similarities"),

    path("gdocs-test", views.gdocs_test, name="test"),
]
