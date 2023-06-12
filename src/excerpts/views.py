# from django.shortcuts import render

from django.http import HttpResponse
from django.urls import reverse
from django.template import loader
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

# from barton_link.gdocs import GDocs
from barton_link.barton_link import BartonLink
from barton_link.gdocs import GDocs
from .models import Excerpt, Tag, Project, Character, ExcerptSimilarity

def index(request):
    return search(request)

def search(request):
    page_num = request.GET.get("page", 1)

    # Extract search field and filters
    search = request.GET.get("search", "")

    # Search for excerpts
    excerpts = Excerpt.objects.filter(excerpt__icontains=search)
    # excerpts = Excerpt.objects.order_by("-id")

    results_per_page = 10
    paginator = Paginator(excerpts, results_per_page)
    page_obj = paginator.get_page(page_num)

    # Build previous and next page links
    prev_page_url = None
    next_page_url = None

    if page_obj.has_previous():
        prev_page_url = reverse("search") + f"?page={page_obj.previous_page_number()}"

        if search:
            prev_page_url += f"&search={search}"

    if page_obj.has_next():
        next_page_url = reverse("search") + f"?page={page_obj.next_page_number()}"

        if search:
            next_page_url += f"&search={search}"

    # Render list
    context = {
        "excerpts": excerpts,
        "page_obj": page_obj,
        "prev_page_url": prev_page_url,
        "next_page_url": next_page_url,
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

    return render(request, "excerpts/excerpt_tags.html", { "excerpt": excerpt, })

def remove_tag(request, excerpt_id, tag_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    tag = Tag.objects.get(id=tag_id)

    excerpt.tags.remove(tag)

    return render(request, "excerpts/excerpt_tags.html", { "excerpt": excerpt, })

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

        return render(request, "excerpts/excerpt_projects.html", { "excerpt": excerpt, })

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

            return render(request, "excerpts/excerpt_projects.html", { "excerpt": excerpt, })

        # If request is GET
        elif request.method == "GET":
            # Render add project form
            return render(request, "excerpts/add_project.html", { "excerpt": excerpt, })

        else:
            #@REVISIT
            return HttpResponse("Invalid request method.")

def remove_project(request, excerpt_id, project_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)
    project = Project.objects.get(id=project_id)

    excerpt.projects.remove(project)

    return render(request, "excerpts/excerpt_projects.html", { "excerpt": excerpt, })

def tag(request, tag_id):
    tag = Tag.objects.get(id=tag_id)
    context = { "tag": tag, }
    return render(request, "excerpts/tag_page.html", context)

def autotag_excerpts(request):
    """
    Autotag excerpts.

    Present user with confirmation page before proceeding.
    """

    barton_link = BartonLink()

    # Get all excerpts, order by ascending id
    excerpts = Excerpt.objects.order_by("id")

    # Get all tags
    tags = Tag.objects.all()

    autotags = []

    # For each excerpt
    for excerpt in excerpts:
        # Get excerpt text
        excerpt_text = excerpt.excerpt

        # For each tag
        for tag in tags:
            # Check if tag is already in excerpt
            if tag in excerpt.tags.all():
                continue

            # Get tag name
            tag_name = tag.name

            # If tag name is in excerpt text
            if tag_name in excerpt_text:
                # Measure semantic similarity between tag name and excerpt text
                similarity = barton_link.measure_similarity_sbert(tag_name, excerpt_text)

                # If similarity is above threshold
                if similarity > 0.7:
                    # Add tag to excerpt
                    # excerpt.tags.add(tag)
                    autotags.append({
                        "excerpt": excerpt,
                        "tag": tag,
                        "similarity": similarity,
                        })

        if len(autotags) > 0:
            break

    context = { "autotags": autotags, }

    return render(request, "excerpts/autotag_confirmation.html", context)

def analyze_similarities(request):
    """
    Analyze similarities between excerpts using NLP.
    """

    barton_link = BartonLink()

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

def test(request):
    #@TEMPORARY
    # barton_link = BartonLink()
    # barton_link.load_google_doc("1_naaQhlNJMOLVbsgnlyp7ejEZbP_vS-llK-ZGAIO3DI")

    # Initialize Google Docs API
    gdocs = GDocs()

    # Load credentials
    gdocs.load_credentials()

    # Load doc-ids.txt
    #@TODO-4 temporary
    with open("../../../data/debug/gdoc_ids.txt", "r") as f:
        document_ids = f.readlines()

    # Split document_ids on == (format is document_name == document_id)
    document_ids = [document_id.split(" == ")[1].strip() for document_id in document_ids]

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

                print(f"Excerpt already exists in database: {excerpt_dict['excerpt']}")

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
