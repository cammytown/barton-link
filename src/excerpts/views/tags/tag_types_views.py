from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render
# from django.core.paginator import Paginator

from ...models import TagType

def tag_type(request, tag_type_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return tag_type_htmx(request, tag_type_id)

    else:
        #@TODO
        return HttpResponse(status=405)
        # return tag_type_html(request, tag_type_id)

def tag_type_html(request, tag_type_id):
    # Get tag type
    tag_type = TagType.objects.get(id=tag_type_id)

    # Get tags with tag type
    tags = tag_type.tags.all()

    # Paginate tags
    #@TODO

    context = { "tag_type": tag_type, "tags": tags }

    return render(request, "excerpts/tags/tag_type_page.html", context)

def tag_type_htmx(request, tag_type_id):
    match request.method:
        case "PUT":
            # Get tag type
            tag_type = TagType.objects.get(id=tag_type_id)

            # Parse request body
            data = QueryDict(request.body)

            # Get tag type name
            tag_type_name = data["tag_type_name"]

            # Get tag type description
            tag_type_description = data["tag_type_description"]

            #@TODO redundant code with POST

            # If tag type name is empty
            if not tag_type_name:
                # Return 400; bad request
                return HttpResponse(status=400)

            # If tag type name is already taken by another tag type
            conflict_tag_type = TagType.objects.filter(name=tag_type_name) \
                    .exclude(id=tag_type_id)

            if conflict_tag_type:
                #@TODO
                return HttpResponse(status=405)
                # # Ask to merge tag types
                # return render(request, "excerpts/tag_type_conflict.html", {
                #     "tag_type": tag_type,
                #     "conflict_tag_type": conflict_tag_type,
                # })

            # Update tag type name
            tag_type.name = tag_type_name

            # Update tag type description
            tag_type.description = tag_type_description

            # Save tag type
            tag_type.save()

            return render(request,
                          "excerpts/tags/_tag_type_header.html",
                          { "tag_type": tag_type })

        case "DELETE":
            # Delete tag type
            #@TODO soft delete
            # tag_type.delete()

            # Return 204; success with no content
            # return HttpResponse(status=204)
            return HttpResponse(status=405)

        case _:
            # Return 405; method not allowed
            return HttpResponse(status=405)

def create_tag_type(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/tags/_tag_type_form.html")
    else:
        return HttpResponse(status=405)

def edit_tag_type(request, tag_type_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/tags/_tag_type_form.html", {
            "tag_type": TagType.objects.get(id=tag_type_id)
        })

    else:
        return HttpResponse(status=405)

def tag_types(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return tag_types_htmx(request)
    else:
        return tag_types_html(request)

def tag_types_html(request):
    return HttpResponse(status=405)
    #@TODO
    # # Get all tag types
    # tag_types = TagType.objects.order_by("name")

    # context = { "tag_types": tag_types }

    # return render(request, "excerpts/tag_types_index.html", context)

def tag_types_htmx(request):
    match request.method:
        case "POST":
            # Parse request body
            data = QueryDict(request.body)

            # Get tag type name
            tag_type_name = data["tag_type_name"]

            # Get tag type description
            tag_type_description = data["tag_type_description"]

            # If tag type name is empty
            if not tag_type_name:
                # Return 400; bad request
                return HttpResponse(status=400)

            # If tag type name is already taken
            if TagType.objects.filter(name=tag_type_name).exists():
                # Return 409; conflict
                return HttpResponse(status=409)

            # Create tag type
            print(f"Creating tag type: {tag_type_name} ({tag_type_description})")
            tag_type = TagType(name=tag_type_name,
                               description=tag_type_description)
            tag_type.save()

            return render(request, "excerpts/tags/_tag_type.html", { "tag_type": tag_type })

