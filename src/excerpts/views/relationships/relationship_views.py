from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.http import QueryDict

from ...models import (
    Excerpt, 
    Entity, 
    ExcerptRelationship, 
    EntityExcerptRelationship,
    EntityRelationship,
    RelationshipType
)

# Import views from other files
from .relationship_form_views import (
    relationship_form,
    create_relationship_form,
    create_entity_relationship_form,
    relationship_preview
)

from .relationship_type_views import (
    create_relationship_type,
    create_relationship_type_htmx
)

# Constants for relationship types
EXCERPT_EXCERPT = 'excerpt-excerpt'
ENTITY_EXCERPT = 'entity-excerpt'
ENTITY_ENTITY = 'entity-entity'

def relationship(request, rel_type, excerpt_id=None, entity_id=None, relationship_id=None):
    """
    Main relationship view that handles different HTTP methods and relationship types.
    Routes to appropriate handler based on whether it's an HTMX request or not.
    
    Args:
        request: The HTTP request
        rel_type: The type of relationship (excerpt-excerpt, entity-excerpt, or entity-entity)
        excerpt_id: The ID of the excerpt (for listing/creating relationships)
        entity_id: The ID of the entity (for listing/creating entity-entity relationships)
        relationship_id: The ID of the relationship (for deleting)
    """
    # Validate relationship type
    if rel_type not in [EXCERPT_EXCERPT, ENTITY_EXCERPT, ENTITY_ENTITY]:
        raise Http404(f"Relationship type '{rel_type}' not found")
    
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return relationship_htmx(request, rel_type, excerpt_id, entity_id, relationship_id)
    # If not HTMX request
    else:
        return relationship_html(request, rel_type, excerpt_id, entity_id, relationship_id)

def relationship_html(request, rel_type, excerpt_id=None, entity_id=None, relationship_id=None):
    """
    Handle regular browser requests for relationships.
    Currently redirects to the appropriate page as relationships are primarily managed via HTMX.
    
    This could be expanded in the future to provide full-page views for relationship management.
    """
    # For now, redirect to the appropriate page
    if rel_type == EXCERPT_EXCERPT and excerpt_id:
        return redirect('excerpt', excerpt_id=excerpt_id)
    elif rel_type == ENTITY_ENTITY and entity_id:
        return redirect('entity', entity_id=entity_id)
    else:
        raise Http404("Invalid relationship type or missing ID")

def relationship_htmx(request, rel_type, excerpt_id=None, entity_id=None, relationship_id=None):
    """
    Handle HTMX requests for relationships.
    
    Args:
        request: The HTTP request
        rel_type: The type of relationship
        excerpt_id: The ID of the excerpt
        entity_id: The ID of the entity
        relationship_id: The ID of the relationship
    """
    match request.method:
        case "GET":
            # If relationship_id is provided, we're viewing a specific relationship
            if relationship_id:
                # Not implemented yet
                return HttpResponse("Viewing specific relationship not implemented yet", status=501)
            
            # If excerpt_id is provided, we're listing relationships for an excerpt
            elif excerpt_id:
                return list_relationships(request, rel_type, excerpt_id)
            
            # If entity_id is provided, we're listing relationships for an entity
            elif entity_id:
                return list_entity_relationships(request, rel_type, entity_id)
            
            # Otherwise, invalid request
            else:
                return HttpResponse("Invalid request", status=400)
        
        case "POST":
            # Creating a new relationship
            return create_relationship(request, rel_type)
        
        case "DELETE":
            # Deleting a relationship
            if relationship_id:
                return delete_relationship(request, rel_type, relationship_id)
            else:
                return HttpResponse("Relationship ID required for DELETE", status=400)
        
        case _:
            return HttpResponse(status=405)

def list_relationships(request, rel_type, excerpt_id):
    """View for listing relationships for an excerpt"""
    excerpt = get_object_or_404(Excerpt, id=excerpt_id)
    
    # Get parent and child relationships
    parent_relationships = ExcerptRelationship.objects.filter(parent=excerpt)
    child_relationships = ExcerptRelationship.objects.filter(child=excerpt)
    
    # Get relationship types for creating new relationships
    relationship_types = RelationshipType.objects.filter(
        applicable_contexts__contains=RelationshipType.EXCERPT_EXCERPT
    )
    
    context = {
        'rel_type': rel_type,
        'excerpt': excerpt,
        'parent_relationships': parent_relationships,
        'child_relationships': child_relationships,
        'relationship_types': relationship_types,
    }
    
    return render(request, 'excerpts/relationships/_relationships_list.html', context)

def list_entity_relationships(request, rel_type, entity_id):
    """View for listing relationships for an entity"""
    entity = get_object_or_404(Entity, id=entity_id)
    
    # Get parent and child relationships
    parent_relationships = EntityRelationship.objects.filter(parent=entity)
    child_relationships = EntityRelationship.objects.filter(child=entity)
    
    context = {
        'rel_type': rel_type,
        'entity': entity,
        'parent_relationships': parent_relationships,
        'child_relationships': child_relationships,
    }
    
    return render(request, 'excerpts/relationships/_entity_relationships_list.html', context)

def create_relationship(request, rel_type):
    """View for creating a new relationship"""
    if rel_type == EXCERPT_EXCERPT:
        source_excerpt_id = request.POST.get('source_excerpt_id')
        target_excerpt_id = request.POST.get('target_excerpt_id')
        relationship_type_id = request.POST.get('relationship_type_id')
        direction = request.POST.get('direction', 'parent')
        
        source_excerpt = get_object_or_404(Excerpt, id=source_excerpt_id)
        target_excerpt = get_object_or_404(Excerpt, id=target_excerpt_id)
        relationship_type = get_object_or_404(RelationshipType, id=relationship_type_id)
        
        # Create the relationship based on the direction
        if direction == 'parent':
            # Source excerpt is the parent
            relationship = ExcerptRelationship.objects.create(
                parent=source_excerpt,
                child=target_excerpt,
                relationship_type=relationship_type
            )
        else:
            # Source excerpt is the child
            relationship = ExcerptRelationship.objects.create(
                parent=target_excerpt,
                child=source_excerpt,
                relationship_type=relationship_type
            )
        
        # Return the updated relationships list
        return list_relationships(request, rel_type, source_excerpt_id)
    
    elif rel_type == ENTITY_ENTITY:
        source_entity_id = request.POST.get('source_entity_id')
        target_entity_id = request.POST.get('target_entity_id')
        relationship_type_id = request.POST.get('relationship_type_id')
        direction = request.POST.get('direction', 'parent')
        
        source_entity = get_object_or_404(Entity, id=source_entity_id)
        target_entity = get_object_or_404(Entity, id=target_entity_id)
        relationship_type = get_object_or_404(RelationshipType, id=relationship_type_id)
        
        # Create the relationship based on the direction
        if direction == 'parent':
            # Source entity is the parent
            relationship = EntityRelationship.objects.create(
                parent=source_entity,
                child=target_entity,
                relationship_type=relationship_type
            )
        else:
            # Source entity is the child
            relationship = EntityRelationship.objects.create(
                parent=target_entity,
                child=source_entity,
                relationship_type=relationship_type
            )
        
        # Return the updated relationships list
        return list_entity_relationships(request, rel_type, source_entity_id)
    
    else:  # ENTITY_EXCERPT
        # Not implemented yet
        return HttpResponse("Entity-Excerpt relationships not implemented yet", status=501)

def delete_relationship(request, rel_type, relationship_id):
    """View for deleting a relationship"""
    if rel_type == EXCERPT_EXCERPT:
        relationship = get_object_or_404(ExcerptRelationship, id=relationship_id)
        excerpt_id = relationship.parent.id  # Store the excerpt ID before deleting
        relationship.delete()
        
        # Return the updated relationships list
        return list_relationships(request, rel_type, excerpt_id)
    
    elif rel_type == ENTITY_ENTITY:
        relationship = get_object_or_404(EntityRelationship, id=relationship_id)
        entity_id = relationship.parent.id  # Store the entity ID before deleting
        relationship.delete()
        
        # Return the updated relationships list
        return list_entity_relationships(request, rel_type, entity_id)
    
    else:  # ENTITY_EXCERPT
        # Not implemented yet
        return HttpResponse("Entity-Excerpt relationships not implemented yet", status=501)