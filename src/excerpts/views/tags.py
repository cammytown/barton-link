from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render
from django.core.paginator import Paginator

from ..models import Excerpt, Tag, TagType

def tags(request):
    # Get tag types
    tag_types = TagType.objects.order_by("name")

    # Get tags with NULL tag type
    null_type_tags = Tag.objects.filter(type__isnull=True)

    # Paginate
    #@TODO

    context = {
        "null_type_tags": null_type_tags,
        "tag_types": tag_types
    }

    return render(request, "excerpts/tags_index.html", context)

def tag(request, tag_id):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return tag_htmx(request, tag_id)
    else:
        return tag_html(request, tag_id)

def tag_html(request, tag_id):
    tag = Tag.objects.get(id=tag_id)

    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 50)

    # Get excerpts with tag
    excerpts = tag.excerpts.all()

    # Paginate excerpts
    paginator = Paginator(excerpts, page_size)
    page_obj = paginator.get_page(page_num)

    context = { "tag": tag, "page_obj": page_obj }

    return render(request, "excerpts/tag_page.html", context)

def tag_htmx(request, tag_id):
    tag = Tag.objects.get(id=tag_id)

    match request.method:
        case "GET":
            context = {
                "tag": tag,
                "tag_types": TagType.objects.order_by("name"),
            }

            return render(request, "excerpts/tag_editor.html", context)

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
                return render(request, "excerpts/tag_conflict.html", {
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

            return render(request, "excerpts/tag_header.html", { "tag": tag })

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

def create_tag_type(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/tag_type_create.html")
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

            return render(request, "excerpts/tag_type.html", { "tag_type": tag_type })

def autotag_excerpts(request, excerpt_id=None):
    barton_link.load_nlp_models() #@REVISIT architecture

    # Get excerpts
    if excerpt_id:
        # Get excerpt with id
        excerpts = Excerpt.objects.filter(id=excerpt_id)

        # If no excerpt with id
        if len(excerpts) == 0:
            # Return 404
            return HttpResponseNotFound()
    else:
        # Get all excerpts, order by ascending id
        excerpts = Excerpt.objects.order_by("id")[:100]
        # excerpts = Excerpt.objects.order_by("id")

    # Build list of excerpt texts
    excerpt_texts = [excerpt.content for excerpt in excerpts]

    # Get tags
    tags = Tag.objects.all()

    # Build list of tag names
    tag_names = [tag.name for tag in tags]

    # Compare excerpts to tags
    print(f"Comparing {len(excerpts)} excerpts to {len(tags)} tags...")
    scores = barton_link.compare_lists_sbert(excerpt_texts, tag_names)


    autotag_objs = []
    for i, excerpt in enumerate(excerpts):
        autotag_obj = {
            "excerpt": excerpt,
            "tag_scores": [],
        }

        for j, tag in enumerate(tags):
            # If tag is already on excerpt
            if tag in excerpt.tags.all():
                continue

            # If score is greater than threshold
            if scores[i][j] >= 0.5:
                autotag_obj["tag_scores"].append({
                    "tag": tag,
                    "score": scores[i][j],
                })

        if len(autotag_obj["tag_scores"]) > 0:
            autotag_objs.append(autotag_obj)

    print(f"Found {len(autotag_objs)} excerpts to autotag.")
    print(autotag_objs)
    context = {
        "autotag_objs": autotag_objs,
    }

    return render(request, "excerpts/autotag_confirmation.html", context)

# def autotag_excerpts(request, excerpt_id=None):
#     """
#     Autotag excerpts.

#     Present user with confirmation page before proceeding.
#     """

#     if excerpt_id:
#         # Get excerpt with id
#         excerpts = Excerpt.objects.filter(id=excerpt_id)

#         # If no excerpt with id
#         if len(excerpts) == 0:
#             # Return 404
#             return HttpResponseNotFound()
#     else:
#         # Get all excerpts, order by ascending id
#         excerpts = Excerpt.objects.order_by("id")

#     autotag_objs = []
#     # warnings = []

#     # For each excerpt
#     for excerpt in excerpts:
#         excerpt_autotag_objs = autotag_excerpt(excerpt)

#         # If excerpt has autotags
#         if len(excerpt_autotag_objs) > 0:
#             autotag_objs.append({ "excerpt": excerpt, "tag_objs": excerpt_autotag_objs, })
#             break

#     context = { "autotags": autotag_objs, }

#     return render(request, "excerpts/autotag_confirmation.html", context)

# #@TODO probably move into a class
# def autotag_excerpt(excerpt):
#     """
#     Autotag an excerpt.
#     """

#     # Get all tags
#     #@TODO-4 optimization? does Django cache this?
#     tags = Tag.objects.all()

#     # Get excerpt text
#     excerpt_text = excerpt.content
#     excerpt_autotag_objs = []

#     print(f"Autotagging excerpt {excerpt.id}...", end="\r")

#     # For each tag
#     # inactive_tag_names = []
#     for tag in tags:
#         # Check if tag is already in excerpt
#         if tag in excerpt.tags.all():
#             continue

#         # Get tag name
#         tag_name = tag.name
#         # inactive_tag_names.append(tag_name)

#         # # If tag name is in excerpt text
#         # if tag_name in excerpt_text:

#         # Measure semantic similarity between tag name and excerpt text
#         similarity = barton_link.measure_similarity_sbert(tag_name, excerpt_text)

#         # If similarity is above threshold
#         if similarity > 0.5:
#             # If similarity is 1.0
#             if similarity == 1.0:
#                 print("Warning: Tag name is identical to excerpt text.")

#             excerpt_autotag_objs.append({
#                 "tag": tag,
#                 "similarity": similarity,
#             })

#     return excerpt_autotag_objs

