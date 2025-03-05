from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404

from ...models import (
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

def relationship_form(request, rel_type, excerpt_id=None, entity_id=None):
    """View for displaying the relationship form based on relationship type"""
    if rel_type == EXCERPT_EXCERPT and excerpt_id:
        return create_relationship_form(request, rel_type, excerpt_id)
    elif rel_type == ENTITY_ENTITY and entity_id:
        return create_entity_relationship_form(request, rel_type, entity_id)
    else:
        raise Http404("Invalid relationship type or missing ID")

def create_relationship_form(request, rel_type, excerpt_id):
    """View for displaying the form to create a new excerpt-excerpt relationship"""
    excerpt = get_object_or_404(Excerpt, id=excerpt_id)
    
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

def relationship_preview(request):
    """View for previewing a relationship before creating it"""
    # Get parameters from request
    rel_type = request.GET.get('rel_type')
    relationship_type_id = request.GET.get('relationship_type_id')
    direction = request.GET.get('direction', 'parent')
    
    # Validate relationship type
    if rel_type not in [EXCERPT_EXCERPT, ENTITY_EXCERPT, ENTITY_ENTITY]:
        return HttpResponse("Invalid relationship type", status=400)
    
    # Get relationship type
    relationship_type = get_object_or_404(RelationshipType, id=relationship_type_id)
    
    # Handle different relationship types
    if rel_type == EXCERPT_EXCERPT:
        source_excerpt_id = request.GET.get('source_excerpt_id')
        target_excerpt_id = request.GET.get('target_excerpt_id')
        
        source_excerpt = get_object_or_404(Excerpt, id=source_excerpt_id)
        target_excerpt = get_object_or_404(Excerpt, id=target_excerpt_id)
        
        context = {
            'rel_type': rel_type,
            'relationship_type': relationship_type,
            'direction': direction,
            'source_excerpt': source_excerpt,
            'target_excerpt': target_excerpt,
        }
    
    elif rel_type == ENTITY_ENTITY:
        source_entity_id = request.GET.get('source_entity_id')
        target_entity_id = request.GET.get('target_entity_id')
        
        source_entity = get_object_or_404(Entity, id=source_entity_id)
        target_entity = get_object_or_404(Entity, id=target_entity_id)
        
        context = {
            'rel_type': rel_type,
            'relationship_type': relationship_type,
            'direction': direction,
            'source_entity': source_entity,
            'target_entity': target_entity,
        }
    
    else:  # ENTITY_EXCERPT
        # Not implemented yet
        return HttpResponse("Entity-Excerpt relationships not implemented yet", status=501)
    
    return render(request, 'excerpts/relationships/_relationship_preview.html', context) 