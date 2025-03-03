from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.views.decorators.http import require_http_methods

from ..models import (
    Excerpt, 
    Entity, 
    ExcerptRelationship, 
    EntityExcerptRelationship,
    EntityRelationship,
    RelationshipType
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
    if excerpt_id:
        return redirect('excerpt_detail', excerpt_id=excerpt_id)
    elif entity_id:
        return redirect('entity_detail', entity_id=entity_id)
    else:
        # If no excerpt_id or entity_id, redirect to excerpts list
        return redirect('index')

def relationship_htmx(request, rel_type, excerpt_id=None, entity_id=None, relationship_id=None):
    """
    Handle HTMX requests for relationships.
    Routes to appropriate handler based on HTTP method.
    """
    # Handle different HTTP methods
    if request.method == "GET":
        # For GET requests, we're listing relationships
        if rel_type == ENTITY_ENTITY and entity_id:
            return list_entity_relationships(request, rel_type, entity_id)
        else:
            return list_relationships(request, rel_type, excerpt_id)
    
    elif request.method == "POST":
        # Creating a new relationship
        return create_relationship(request, rel_type)
    
    elif request.method == "DELETE":
        # Deleting a relationship
        return delete_relationship(request, rel_type, relationship_id)
    
    # Method not allowed
    return HttpResponse(status=405)

def relationship_form(request, rel_type, excerpt_id=None, entity_id=None):
    """
    View for displaying the form to create a new relationship.
    This is a separate endpoint specifically for the form.
    """
    # Validate relationship type
    if rel_type not in [EXCERPT_EXCERPT, ENTITY_EXCERPT, ENTITY_ENTITY]:
        raise Http404(f"Relationship type '{rel_type}' not found")
    
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        if rel_type == ENTITY_ENTITY:
            return create_entity_relationship_form(request, rel_type, entity_id)
        else:
            return create_relationship_form(request, rel_type, excerpt_id)
    # If not HTMX request, redirect to the appropriate page
    else:
        if excerpt_id:
            return redirect('excerpt_detail', excerpt_id=excerpt_id)
        elif entity_id:
            return redirect('entity_detail', entity_id=entity_id)
        else:
            return redirect('index')

def list_relationships(request, rel_type, excerpt_id):
    """View for displaying relationships of a specific type"""
    excerpt = get_object_or_404(Excerpt, id=excerpt_id)
    
    if rel_type == EXCERPT_EXCERPT:
        # Get all relationships where this excerpt is either parent or child
        parent_relationships = ExcerptRelationship.objects.filter(parent=excerpt)
        child_relationships = ExcerptRelationship.objects.filter(child=excerpt)
        
        # Combine both types of relationships for display
        excerpt_relationships = list(parent_relationships) + list(child_relationships)
        
        context = {
            'rel_type': rel_type,
            'excerpt': excerpt,
            'excerpt_relationships': excerpt_relationships,
        }
        
    elif rel_type == ENTITY_EXCERPT:
        # Get all relationships between entities and this excerpt
        entity_relationships = EntityExcerptRelationship.objects.filter(excerpt=excerpt)
        
        context = {
            'rel_type': rel_type,
            'excerpt': excerpt,
            'entity_relationships': entity_relationships,
        }
    
    return render(request, 'excerpts/relationships/_relationship_list.html', context)

def list_entity_relationships(request, rel_type, entity_id):
    """View for displaying entity-entity relationships"""
    entity = get_object_or_404(Entity, id=entity_id)
    
    # Get all relationships where this entity is either entity_a or entity_b
    entity_a_relationships = EntityRelationship.objects.filter(entity_a=entity)
    entity_b_relationships = EntityRelationship.objects.filter(entity_b=entity)
    
    # Combine both types of relationships for display
    entity_relationships = list(entity_a_relationships) + list(entity_b_relationships)
    
    context = {
        'rel_type': rel_type,
        'entity': entity,
        'entity_relationships': entity_relationships,
    }
    
    return render(request, 'excerpts/relationships/_relationship_list.html', context)

def create_relationship_form(request, rel_type, excerpt_id):
    """View for displaying the form to create a new relationship"""
    excerpt = get_object_or_404(Excerpt, id=excerpt_id)
    
    if rel_type == EXCERPT_EXCERPT:
        # Get all relationship types applicable for excerpt-to-excerpt relationships
        relationship_types = RelationshipType.objects.filter(
            applicable_contexts__contains=RelationshipType.EXCERPT_EXCERPT
        )
        
        # Get all excerpts except the current one
        available_excerpts = Excerpt.objects.exclude(id=excerpt_id)
        
        context = {
            'rel_type': rel_type,
            'excerpt': excerpt,
            'relationship_types': relationship_types,
            'available_excerpts': available_excerpts,
        }
        
    elif rel_type == ENTITY_EXCERPT:
        # Get all relationship types applicable for entity-to-excerpt relationships
        relationship_types = RelationshipType.objects.filter(
            applicable_contexts__contains=RelationshipType.ENTITY_EXCERPT
        )
        
        # Get all entities
        available_entities = Entity.objects.all()
        
        context = {
            'rel_type': rel_type,
            'excerpt': excerpt,
            'relationship_types': relationship_types,
            'available_entities': available_entities,
        }
    
    return render(request, 'excerpts/relationships/_relationship_form.html', context)

def create_entity_relationship_form(request, rel_type, entity_id):
    """View for displaying the form to create a new entity-entity relationship"""
    entity = get_object_or_404(Entity, id=entity_id)
    
    # Get all relationship types applicable for entity-to-entity relationships
    relationship_types = RelationshipType.objects.filter(
        applicable_contexts__contains=RelationshipType.ENTITY_ENTITY
    )
    
    # Get all entities except the current one
    available_entities = Entity.objects.exclude(id=entity_id)
    
    context = {
        'rel_type': rel_type,
        'entity': entity,
        'relationship_types': relationship_types,
        'available_entities': available_entities,
    }
    
    return render(request, 'excerpts/relationships/_relationship_form.html', context)

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
            # Target excerpt is the parent
            relationship = ExcerptRelationship.objects.create(
                parent=target_excerpt,
                child=source_excerpt,
                relationship_type=relationship_type
            )
        
        # Return the updated relationships list
        return list_relationships(request, rel_type, source_excerpt_id)
    
    elif rel_type == ENTITY_EXCERPT:
        excerpt_id = request.POST.get('excerpt_id')
        entity_id = request.POST.get('entity_id')
        relationship_type_id = request.POST.get('relationship_type_id')
        
        excerpt = get_object_or_404(Excerpt, id=excerpt_id)
        entity = get_object_or_404(Entity, id=entity_id)
        relationship_type = get_object_or_404(RelationshipType, id=relationship_type_id)
        
        # Create the relationship
        relationship = EntityExcerptRelationship.objects.create(
            entity=entity,
            excerpt=excerpt,
            relationship_type=relationship_type
        )
        
        # Return the updated relationships list
        return list_relationships(request, rel_type, excerpt_id)
    
    elif rel_type == ENTITY_ENTITY:
        entity_a_id = request.POST.get('entity_a_id')
        entity_b_id = request.POST.get('entity_b_id')
        relationship_type_id = request.POST.get('relationship_type_id')
        
        entity_a = get_object_or_404(Entity, id=entity_a_id)
        entity_b = get_object_or_404(Entity, id=entity_b_id)
        relationship_type = get_object_or_404(RelationshipType, id=relationship_type_id)
        
        # Create the relationship
        relationship = EntityRelationship.objects.create(
            entity_a=entity_a,
            entity_b=entity_b,
            relationship_type=relationship_type
        )
        
        # Return the updated relationships list
        return list_entity_relationships(request, rel_type, entity_a_id)

def delete_relationship(request, rel_type, relationship_id):
    """View for deleting a relationship"""
    if rel_type == EXCERPT_EXCERPT:
        relationship = get_object_or_404(ExcerptRelationship, id=relationship_id)
        
        # Store the excerpt ID before deleting the relationship
        excerpt_id = relationship.parent.id
        if relationship.child.id == excerpt_id:
            excerpt_id = relationship.child.id
        
        # Delete the relationship
        relationship.delete()
        
        # Return the updated relationships list
        return list_relationships(request, rel_type, excerpt_id)
    
    elif rel_type == ENTITY_EXCERPT:
        relationship = get_object_or_404(EntityExcerptRelationship, id=relationship_id)
        
        # Store the excerpt ID before deleting the relationship
        excerpt_id = relationship.excerpt.id
        
        # Delete the relationship
        relationship.delete()
        
        # Return the updated relationships list
        return list_relationships(request, rel_type, excerpt_id)
    
    elif rel_type == ENTITY_ENTITY:
        relationship = get_object_or_404(EntityRelationship, id=relationship_id)
        
        # Store the entity ID before deleting the relationship
        entity_id = relationship.entity_a.id
        
        # Delete the relationship
        relationship.delete()
        
        # Return the updated relationships list
        return list_entity_relationships(request, rel_type, entity_id)

def relationship_preview(request):
    """
    View for generating a preview of a relationship based on selected items.
    This is called via HTMX to show a real-time preview of the relationship.
    
    Note: This implementation uses server-side rendering with HTMX for simplicity and to avoid JavaScript.
    For production environments with high traffic, this could be optimized with client-side rendering.

    """
    rel_type = request.GET.get('rel_type')
    
    # Validate relationship type
    if rel_type not in [EXCERPT_EXCERPT, ENTITY_EXCERPT, ENTITY_ENTITY]:
        return HttpResponse("Invalid relationship type", status=400)
    
    # Get relationship type if provided
    relationship_type_id = request.GET.get('relationship_type_id')
    selected_relationship_type = None
    if relationship_type_id:
        try:
            selected_relationship_type = RelationshipType.objects.get(id=relationship_type_id)
        except RelationshipType.DoesNotExist:
            pass
    
    context = {
        'rel_type': rel_type,
        'selected_relationship_type': selected_relationship_type,
    }
    
    if rel_type == ENTITY_ENTITY:
        entity_id = request.GET.get('entity_a_id')
        entity_b_id = request.GET.get('entity_b_id')
        
        if entity_id:
            try:
                entity = Entity.objects.get(id=entity_id)
                context['entity'] = entity
            except Entity.DoesNotExist:
                pass
        
        if entity_b_id:
            try:
                selected_entity = Entity.objects.get(id=entity_b_id)
                context['selected_entity'] = selected_entity
            except Entity.DoesNotExist:
                pass
    
    elif rel_type == ENTITY_EXCERPT:
        excerpt_id = request.GET.get('excerpt_id')
        entity_id = request.GET.get('entity_id')
        
        if excerpt_id:
            try:
                excerpt = Excerpt.objects.get(id=excerpt_id)
                context['excerpt'] = excerpt
            except Excerpt.DoesNotExist:
                pass
        
        if entity_id:
            try:
                selected_entity = Entity.objects.get(id=entity_id)
                context['selected_entity'] = selected_entity
            except Entity.DoesNotExist:
                pass
    
    elif rel_type == EXCERPT_EXCERPT:
        source_excerpt_id = request.GET.get('source_excerpt_id')
        target_excerpt_id = request.GET.get('target_excerpt_id')
        
        # Check if this is a flip request
        if 'direction' in request.GET:
            direction = request.GET.get('direction')
        else:
            # Use the current direction from the form
            direction = 'parent'
        
        if source_excerpt_id:
            try:
                excerpt = Excerpt.objects.get(id=source_excerpt_id)
                context['excerpt'] = excerpt
            except Excerpt.DoesNotExist:
                pass
        
        if target_excerpt_id:
            try:
                selected_excerpt = Excerpt.objects.get(id=target_excerpt_id)
                context['selected_excerpt'] = selected_excerpt
            except Excerpt.DoesNotExist:
                pass
        
        context['direction'] = direction
    
    return render(request, 'excerpts/relationships/_relationship_preview.html', context) 