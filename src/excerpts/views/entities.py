from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render, get_object_or_404

from ..models import Entity, EntityRelationship, RelationshipType, EntityExcerptRelationship, Excerpt

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

def create_relationship(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return create_relationship_htmx(request)
        # return HttpResponse(status=405)
    else:
        # return create_relationship_html(request)
        return HttpResponse(status=405)

def create_relationship_htmx(request):
    match request.method:
        # If GET request
        case "GET":
            return render(request, "excerpts/entities/_relationship_create.html", {})
        
        # If POST request
        case "POST":
            # Parse HTMX POST request
            request_data = QueryDict(request.body)
            
            # Extract entity IDs
            entity_a_id = request_data.get("entity_a")
            entity_b_id = request_data.get("entity_b")

            # Extract relationship type
            relationship_type = request_data.get("relationship_type")
            
            # Create relationship
            EntityRelationship.objects.create(
                entity_a_id=entity_a_id,
                entity_b_id=entity_b_id,
                relationship_type=relationship_type
            )
            
            # Render relationship
            context = { "relationship": relationship }
            return render(request, "excerpts/entities/_relationship.html", context)
        
        # If other request
        case _:
            return HttpResponse(status=405)

def create_relationship_type(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return create_relationship_type_htmx(request)
        # return HttpResponse(status=405)
    else:
        # return create_relationship_type_html(request)
        return HttpResponse(status=405)

def create_relationship_type_htmx(request):
    match request.method:
        # If GET request
        case "GET":
            return render(request, "excerpts/entities/_relationship_type_create.html", {})
        
        # If POST request
        case "POST":
            # Parse HTMX POST request
            request_data = QueryDict(request.body)
            
            # Extract relationship type name and description
            relationship_type_name = request_data.get("relationship_type_name")
            relationship_type_description = request_data.get("relationship_type_description")
            
            # Create relationship type
            # relationship_type = RelationshipType.objects.create(
            #     name=relationship_type_name,
            #     description=relationship_type_description
            # )

            #@REVISIT weird:
            return create_relationship_htmx(request)
            
            # Render relationship type
            # context = { "relationship_type": relationship_type }
            # return render(request,
            #               "excerpts/entities/_relationship_type.html",
            #               context)
        
        # If other request
        case _:
            return HttpResponse(status=405)
