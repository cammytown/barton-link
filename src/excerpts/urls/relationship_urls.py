from django.urls import path

from ..views.relationships.relationship_views import (
    relationship, create_relationship, delete_relationship
)
from ..views.relationships.relationship_form_views import (
    relationship_form, create_relationship_form, 
    create_entity_relationship_form, relationship_preview
)
from ..views.relationships.relationship_type_views import (
    create_relationship_type
)

urlpatterns = [
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
] 