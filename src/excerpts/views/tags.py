from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render
from django.core.paginator import Paginator

from ..models import Excerpt, Tag

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
            return render(request, "excerpts/tag_editor.html", { "tag": tag })

        case "PUT":
            # Get tag name from request body
            tag_name = QueryDict(request.body)["name"]

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

