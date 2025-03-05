from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render
from django.core.paginator import Paginator
from django.urls import reverse

from barton_link import barton_link

from ...models import Excerpt,\
        Tag,\
        TagType,\
        ExcerptAutoTag\

def tags(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return tags_htmx(request)
    else:
        return tags_html(request)

def tags_htmx(request):
    match request.method:
        case "POST":
            # Parse request body
            data = QueryDict(request.body)

            # Get tag name
            tag_name = data["tag_name"]

            # If tag name is empty
            if not tag_name:
                # Return 400; bad request
                return HttpResponse(status=400)

            #@REVISIT redundancies:

            # If tag name is already taken by another tag
            conflict_tag = Tag.objects.filter(name=tag_name)
            if conflict_tag:
                # Ask to merge tags
                return render(request, "excerpts/tag_conflict.html", {
                    "tag": conflict_tag,
                })

            # Get tag type
            tag_type_id = data["tag_type_id"]
            tag_type = TagType.objects.get(id=tag_type_id)

            # If tag type does not exist
            if not tag_type:
                # If id is 1
                if tag_type_id == 1:
                    # Create default tag type
                    #@REVISIT implementation
                    tag_type = TagType.objects.create(name="default")
                else:
                    #@TODO allow user to create tag type?

                    # Return 400; bad request
                    return HttpResponse(status=400)

            # Create tag
            tag = Tag.objects.create(name=tag_name, type=tag_type)

            return render(request, "excerpts/tags/_tag.html", { "tag": tag })

        case _:
            return HttpResponse(status=405)


def tags_html(request):
    match request.method:
        case "GET":
            # Get tag types
            tag_types = TagType.objects.order_by("id")

            # Get tags with NULL tag type
            null_type_tags = Tag.objects.filter(type__isnull=True)

            # Paginate
            #@TODO

            context = {
                "null_type_tags": null_type_tags,
                "tag_types": tag_types
            }

            return render(request, "excerpts/tags/tags_index.html", context)

        case _:
            return HttpResponse(status=405)

def tag(request, tag_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return tag_htmx(request, tag_id)
    else:
        return tag_html(request, tag_id)

def tag_html(request, tag_id):
    tag = Tag.all_objects.get(id=tag_id)

    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 50)

    # Get excerpts with tag
    excerpts = tag.excerpts.all()

    # Paginate excerpts
    paginator = Paginator(excerpts, page_size)
    page_obj = paginator.get_page(page_num)

    context = { "tag": tag, "page_obj": page_obj }

    return render(request, "excerpts/tags/tag_page.html", context)

def tag_htmx(request, tag_id):
    tag = Tag.objects.get(id=tag_id)

    match request.method:
        case "PUT":
            # Get tag name from request body
            tag_name = QueryDict(request.body)["tag_name"]
            tag_type_id = QueryDict(request.body)["tag_type_id"]

            # If tag name is empty
            if not tag_name:
                # Return 400; bad request
                return HttpResponse(status=400)

            # If tag name is already taken by another tag
            conflict_tag = Tag.objects.filter(name=tag_name).exclude(id=tag_id)
            if conflict_tag:
                # Ask to merge tags
                return render(request, "excerpts/tags/_tag_conflict.html", {
                    "tag": tag,
                    "conflict_tag": conflict_tag,
                })

            # # If tag type is not empty
            # if tag_type_id:
            # Get tag type
            tag_type = TagType.objects.get(id=tag_type_id)

            # If tag type does not exist
            if not tag_type:
                # If id is 1
                if tag_type_id == 1:
                    # Create default tag type
                    #@REVISIT implementation
                    tag_type = TagType.objects.create(name="default")
                else:
                    #@TODO allow user to create tag type

                    # Return 400; bad request
                    return HttpResponse(status=400)

            tag.type = tag_type

            # Update tag name
            tag.name = tag_name

            tag.save()

            return render(request, "excerpts/tags/_tag_header.html", { "tag": tag })

        case "DELETE":
            # Delete tag
            #@TODO soft delete
            # tag.delete()

            # Return 204; success with no content
            # return HttpResponse(status=204)
            return HttpResponse(status=405)

        case _:
            # Return 405; method not allowed
            return HttpResponse(status=405)

def create_tag(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        if request.method == "GET":
            context = {
                "tag_types": TagType.objects.order_by("name"),
            }

            return render(request, "excerpts/tags/_tag_form.html", context)
        else:
            return HttpResponse(status=405)
    else:
        return HttpResponse(status=405)

def edit_tag(request, tag_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        # Get tag
        tag = Tag.objects.get(id=tag_id)

        context = {
            "tag": tag,
            "tag_types": TagType.objects.order_by("name"),
        }

        return render(request, "excerpts/tags/_tag_form.html", context)
    else:
        return HttpResponse(status=405)

def split_tag(request, tag_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        match request.method:
            case "GET":
                # Get tag
                tag = Tag.objects.get(id=tag_id)

                context = {
                    "tag": tag,
                    "tag_types": TagType.objects.order_by("name"),
                }

                return render(request, "excerpts/tags/_tag_splitter.html", context)

            case "POST":
                # Get original tag
                original_tag = Tag.objects.get(id=tag_id)

                # Get tag names from tag_names[] in request
                tag_names = request.POST.getlist("tag_names[]")

                # Remove empty strings
                tag_names = list(filter(None, tag_names))

                # If tag names is empty
                if not tag_names:
                    # Return 400; bad request
                    return HttpResponse(status=400)

                # If tag names contains original tag name
                if original_tag.name in tag_names:
                    # Return 400; bad request
                    return HttpResponse(status=400)

                new_tags = []

                # For each tag name
                for tag_name in tag_names:
                    # Get tag if it exists
                    tag = Tag.objects.filter(name=tag_name).first()

                    # If tag doesn't exist
                    if not tag:
                        # Create tag
                        tag = Tag.objects.create(name=tag_name)

                    # Add tag to new tags
                    new_tags.append(tag)

                # Get excerpts with original tag
                excerpts = original_tag.excerpts.all()

                # For each excerpt
                for excerpt in excerpts:
                    # For each new tag
                    for new_tag in new_tags:
                        # Add new tag to excerpt
                        excerpt.tags.add(new_tag)

                    # Remove original tag from excerpt
                    excerpt.tags.remove(original_tag)

                # Delete original tag
                original_tag.soft_delete()

                return render(request,
                              "excerpts/tags/_tag_header.html",
                              { "tag": original_tag })

    else:
        return HttpResponse(status=405)

#@REVISIT weird naming/architecture; probably more appropriate to have two
#@ different get requests; one for toggle on template and for off template
def toggle_tag(request, tag_id):
    """
    Returns a partial template for the tag and a hidden input element for use
    in the tag toggle form.
    """

    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        # toggle_on true if POST, false if DELETE
        if request.method == "POST":
            toggle_on = True
        elif request.method == "DELETE":
            toggle_on = False
        else:
            return HttpResponse(status=405)

        # Get tag
        tag = Tag.objects.get(id=tag_id)

        return render(request,
                      "excerpts/tags/_tag_toggle.html",
                      { "tag": tag, "toggle_on": toggle_on })
    else:
        return HttpResponse(status=405)

#@REVISIT naming
def add_split_field(request, tag_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/tags/_tag_split_field.html")
    else:
        return HttpResponse(status=405)