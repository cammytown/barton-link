from django.shortcuts import render
from django.http import HttpResponse
from django.http import QueryDict

from ...models import RelationshipType

def create_relationship_type(request):
    """View for creating a new relationship type"""
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return create_relationship_type_htmx(request)
    else:
        return HttpResponse(status=405)

def create_relationship_type_htmx(request):
    """HTMX handler for creating a new relationship type"""
    match request.method:
        # If GET request
        case "GET":
            return render(request, "excerpts/entities/_relationship_type_create.html", {})
        
        # If POST request
        case "POST":
            # Parse HTMX POST request
            request_data = QueryDict(request.body)
            
            # Extract relationship type name and description
            relationship_type_name = request_data.get("name")
            relationship_type_description = request_data.get("description")
            
            # Create relationship type
            relationship_type = RelationshipType.objects.create(
                name=relationship_type_name,
                description=relationship_type_description,
                # Default to all contexts, can be updated later if needed
                applicable_contexts=f"{RelationshipType.ENTITY_ENTITY},{RelationshipType.EXCERPT_EXCERPT},{RelationshipType.ENTITY_EXCERPT}"
            )
            
            # Render relationship type
            context = { "relationship_type": relationship_type }
            return render(request, "excerpts/entities/_relationship_type.html", context)
        
        # If other request
        case _:
            return HttpResponse(status=405) 