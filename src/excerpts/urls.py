from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:page_num>/", views.index, name="index"),

    path("excerpt/<int:excerpt_id>/", views.excerpt, name="excerpt"),
    path("tag/<int:tag_id>/", views.tag, name="tag"),

    path("test/", views.test, name="test"),
]
