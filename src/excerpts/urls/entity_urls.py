from django.urls import path

from ..views.entities.entity_views import (
    entities, entity, create_entity
)

urlpatterns = [
    path("entities", entities, name="entities"),
    path("entities/create", create_entity, name="create_entity"),
    path("entity/<int:entity_id>", entity, name="entity_detail"),
] 