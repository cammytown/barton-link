from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render, get_object_or_404

from ...models import Entity, EntityRelationship, RelationshipType, EntityExcerptRelationship, Excerpt

def entities(request):
    """View for displaying all entities"""
    entities_list = Entity.objects.all()
    
    context = {
        'entities': entities_list,
    }
    
    return render(request, "excerpts/entities/entity_index.html", context)

def entity(request, entity_id):
    """View for displaying entity details"""
    entity = get_object_or_404(Entity, id=entity_id)
    
    # Get related excerpts
    related_excerpts = Excerpt.objects.filter(related_entities=entity)
    
    # Get entity-entity relationships for initial display
    entity_a_relationships = EntityRelationship.objects.filter(entity_a=entity)
    entity_b_relationships = EntityRelationship.objects.filter(entity_b=entity)
    entity_relationships = list(entity_a_relationships) + list(entity_b_relationships)
    
    context = {
        'entity': entity,
        'excerpts': related_excerpts,
        'rel_type': 'entity-entity',
        'entity_relationships': entity_relationships,
    }
    
    return render(request, "excerpts/entities/entity_page.html", context)

def create_entity(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return create_entity_htmx(request)
        # return HttpResponse(status=405)
    else:
        # return create_entity_html(request)
        return HttpResponse(status=405)

def create_entity_htmx(request):
    match request.method:
        # If GET request
        case "GET":
            return render(request, "excerpts/entities/_entity_create.html", {})
        
        # If POST request
        case "POST":
            # Parse HTMX POST request
            request_data = QueryDict(request.body)
            
            # Extract entity name and description
            entity_name = request_data.get("entity_name")
            entity_description = request_data.get("entity_description")
            
            # Create entity
            entity = Entity.objects.create(name=entity_name, description=entity_description)
            
            # Render entity
            context = { "entity": entity }
            return render(request, "excerpts/entities/_entity.html", context)
        
        # If other request
        case _:
            return HttpResponse(status=405)

# def create_entity_html(request):
#     # If GET request
#     if request.method == "GET":
#         return render(request, "excerpts/entities/entity_create.html", {})
    
#     # If POST request
#     elif request.method == "POST":
#         # Parse POST request
#         entity_name = request.POST.get("entity_name")
#         entity_description = request.POST.get("entity_description")

#         # Create entity
#         entity = Entity.objects.create(name=entity_name, description=entity_description)
        
#         # Redirect to entity page
#         return HttpResponse(status=201)
