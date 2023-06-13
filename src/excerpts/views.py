# from django.shortcuts import render

from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.template import loader
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

# from barton_link.gdocs import GDocs
from barton_link.barton_link import BartonLink
from barton_link.gdocs import GDocs
from .models import Excerpt, Tag, Project, Character, ExcerptSimilarity

barton_link = BartonLink()

def index(request):
    return search(request)

def search(request):
    page_num = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 50)

    # Extract search field and filters
    search = request.GET.get("search", "")

    # Search for excerpts
    excerpts = Excerpt.objects.filter(excerpt__icontains=search)
    # excerpts = Excerpt.objects.order_by("-id")

    paginator = Paginator(excerpts, page_size)
    page_obj = paginator.get_page(page_num)

    # Build previous and next page links
    prev_page_url = None
    next_page_url = None

    if page_obj.has_previous():
        prev_page_url = reverse("search") + \
                f"?page={page_obj.previous_page_number()}"

        if search:
            prev_page_url += f"&search={search}"

    if page_obj.has_next():
        next_page_url = reverse("search") + \
                f"?page={page_obj.next_page_number()}"

        if search:
            next_page_url += f"&search={search}"

    # Render list
    context = {
        "excerpts": excerpts,
        "page_obj": page_obj,
        "prev_page_url": prev_page_url,
        "next_page_url": next_page_url,
        "page_sizes": [10, 25, 50, 100],
        "page_size": page_size,
        "search": search,
        }

    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        return render(request, "excerpts/excerpt_list.html", context)
    else:
        return render(request, "excerpts/excerpt_search.html", context)

def excerpt(request, excerpt_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)

    # If GET request
    if request.method == "GET":
        context = { "excerpt": excerpt }
        return render(request, "excerpts/excerpt_page.html", context)

    # If DELETE request
    elif request.method == "DELETE":
        # excerpt.delete()
        return HttpResponse(status=204)

def edit(request, excerpt_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)

    context = { "excerpt": excerpt }
    return render(request, "excerpts/edit_page.html", context)

def delete(request, excerpt_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)

    # Mark excerpt as deleted
    #@TODO-3: maintenance op to actually delete excerpts marked as deleted
    excerpt.is_deleted = True
    excerpt.save()

    # Redirect to search page
    return redirect("search")

def add_tag(request, excerpt_id, tag_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    tag = Tag.objects.get(id=tag_id)

    excerpt.tags.add(tag)

    return render(request, "excerpts/excerpt_tags.html", { "excerpt": excerpt })

def add_autotag(request, excerpt_id, tag_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    tag = Tag.objects.get(id=tag_id)

    # Add tag to excerpt with is_autotag=True
    excerpt.tags.add(tag, through_defaults={ "is_autotag": True })

    return render(request,
                  "excerpts/excerpt_tags.html",
                  {
                      "excerpt": excerpt,
                      "show_unused_tags": False
                  })

def remove_tag(request, excerpt_id, tag_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    tag = Tag.objects.get(id=tag_id)

    excerpt.tags.remove(tag)

    return render(request,
                  "excerpts/excerpt_tags.html",
                  { "excerpt": excerpt })

def add_project(request, excerpt_id, project_id=None):
    """
    Add a project to an excerpt.

    If a project_id is provided, add the project with that id to the excerpt.
    Otherwise, create a new project and add it to the excerpt.
    """

    # Get excerpt
    excerpt = Excerpt.objects.get(id=excerpt_id)

    # If project_id is provided
    if project_id:
        # Get project
        #@TODO Handle case where project_id is invalid
        project = Project.objects.get(id=project_id)

        # Add project to excerpt
        excerpt.projects.add(project)

        return render(request,
                      "excerpts/excerpt_projects.html",
                      { "excerpt": excerpt })

    else:
        # If request is POST
        if request.method == "POST":
            # Get project_name from POST
            project_name = request.POST["project_name"]

            # Create project
            project = Project(name=project_name)
            project.save()

            # Add project to excerpt
            excerpt.projects.add(project)

            return render(request,
                          "excerpts/excerpt_projects.html",
                          { "excerpt": excerpt, })

        # If request is GET
        elif request.method == "GET":
            # Render add project form
            return render(request,
                          "excerpts/add_project.html",
                          { "excerpt": excerpt, })

        else:
            #@REVISIT
            return HttpResponse("Invalid request method.")

def remove_project(request, excerpt_id, project_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    project = Project.objects.get(id=project_id)

    excerpt.projects.remove(project)

    return render(request,
                  "excerpts/excerpt_projects.html",
                  { "excerpt": excerpt, })

def tag(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    context = { "tag": tag, }
    return render(request, "excerpts/tag_page.html", context)

def autotag_excerpts(request, excerpt_id=None):
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
    excerpt_texts = [excerpt.excerpt for excerpt in excerpts]

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
#     excerpt_text = excerpt.excerpt
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

def analyze_similarities(request):
    """
    Analyze similarities between excerpts using NLP.
    """

    created_count = 0

    # Get all excerpts, order by ascending id
    excerpts = Excerpt.objects.order_by("id")

    # For each excerpt
    for excerpt in excerpts:
        # Get excerpt text
        excerpt_text = excerpt.excerpt

        # For each other excerpt
        for other_excerpt in excerpts[excerpt.id:]:
            # If other_excerpt is the same as excerpt
            #@REVISIT perhaps unnecessary with the excerpts[excerpt.id:] slice
            if other_excerpt == excerpt:
                # Skip
                continue

            #@REVISIT also should be unnecessary with excerpts[excerpt.id:]
            # The order is important for querying the database
            assert other_excerpt.id > excerpt.id

            # Get other_excerpt text
            other_excerpt_text = other_excerpt.excerpt

            # Measure similarities
            sbert_similarity = barton_link.measure_excerpt_similarity_sbert(
                    excerpt_text,
                    other_excerpt_text
                    )

            # spacy_similarity = barton_link.measure_excerpt_similarity_spacy(
            #         excerpt_text,
            #         other_excerpt_text
            #         )

            threshold = 0.4

            # If similarity is below threshold
            if abs(sbert_similarity) < threshold:
                # Skip
                continue

            print(f"Similarity between {excerpt.id} and {other_excerpt.id} " \
                    + f" exceeds threshold < -{threshold} or > {threshold}")
            print(f"SBERT: {sbert_similarity}")
            # print(f"SpaCy: {spacy_similarity}")
            print(excerpt_text)
            print("-----")
            print(other_excerpt_text)
            print("===== (similarities added: " + str(created_count) + ")")

            # Check if similarity already exists
            similarity_entry = ExcerptSimilarity.objects.filter(
                    excerpt1=excerpt,
                    excerpt2=other_excerpt,
                    )
            if similarity_entry:
                # Check for differing similarity values
                if similarity_entry.sbert_similarity != sbert_similarity:
                    print(f"WARNING: SBERT similarity mismatch for " \
                            + "{excerpt.id} and {other_excerpt.id}:")
                    print(f"Existing: {similarity_entry.sbert_similarity}")
                    print(f"New: {sbert_similarity}")
                    print("Updating similarity value...")

                    # Update similarity value
                    similarity_entry.sbert_similarity = sbert_similarity

                    # Save similarity entry
                    similarity_entry.save()

                #@REVISIT do we care abouy spacy? probably not.

            # If similarity does not already exist
            else:
                # Create ExcerptSimilarity instance
                similarity_entry = ExcerptSimilarity(
                        excerpt1=excerpt,
                        excerpt2=other_excerpt,
                        sbert_similarity=sbert_similarity,
                        # spacy_similarity=spacy_similarity
                        )
                similarity_entry.save()

                created_count += 1

    return HttpResponse(f"Created {created_count} new ExcerptSimilarity entries.")

def gdocs_test(request):
    # Initialize Google Docs API
    gdocs = GDocs()

    # Load credentials
    gdocs.load_credentials()

    # Load doc-ids.txt
    #@TODO-4 temporary
    with open("../data/debug/gdoc_ids.txt", "r") as f:
        document_ids = f.readlines()

    # Split document_ids on == (format is document_name == document_id)
    document_ids = [document_id.split(" == ")[1].strip() \
            for document_id in document_ids]

    response = f"Loaded {len(document_ids)} document ids."

    # Print all document_ids
    # for document_id in document_ids:
    #     response += f"\ndoc: {document_id}"

    # print(response)
    # exit()

    # Load and parse each Google Doc
    for document_id in document_ids:
        # Load document
        document = gdocs.get_document(document_id)
        excerpt_dicts = gdocs.parse_document(document)

        # Turn excerpt_dicts into Excerpt instances
        excerpts = []
        for exc_idx, excerpt_dict in enumerate(excerpt_dicts):
            # Check if excerpt already exists in database
            if Excerpt.objects.filter(
                    excerpt=excerpt_dict["excerpt"],
                    metadata=excerpt_dict["metadata"],
                    ).exists():

                print("Excerpt already exists in database: " \
                        + f"{excerpt_dict['excerpt']}")

                excerpt_dict["excerpt_instance"] = None

                # Skip to next excerpt
                continue

            # print(f"Excerpt does not exist in database: {excerpt_dict['excerpt']}")

            # Create Excerpt instance
            #@REVISIT architecture
            excerpt_dict["excerpt_instance"] = Excerpt(
                excerpt=excerpt_dict["excerpt"],
                metadata=excerpt_dict["metadata"],
            )

            excerpts.append(excerpt_dict["excerpt_instance"])

        # Insert excerpts into database
        Excerpt.objects.bulk_create(excerpts)

        # Add tags to excerpts
        for excerpt_dict in excerpt_dicts:
            if "excerpt_instance" not in excerpt_dict:
                raise Exception("Excerpt instance not found in excerpt_dict")

            # If excerpt_instance is None
            if not excerpt_dict["excerpt_instance"]:
                # Skip to next excerpt
                #@REVISIT architecture
                continue

            excerpt = excerpt_dict["excerpt_instance"]

            for tag_name in excerpt_dict["tags"]:
                tag = Tag.objects.get_or_create(name=tag_name)[0]
                excerpt.tags.add(tag)

        response += f"\nLoaded {len(excerpt_dicts)} excerpts from {document_id}."

    return HttpResponse(response)
