# from django.shortcuts import render

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.core.paginator import Paginator

# from barton_link.gdocs import GDocs
# from barton_link.barton_link import BartonLink
from barton_link.gdocs import GDocs
from .models import Excerpt, Tag, Project, Character

def index(request, page_num=1):
    results_per_page = 50
    # start_idx = (page_num - 1) * results_per_page
    # end_idx = start_idx + results_per_page

    # latest_excerpts = Excerpt.objects.order_by("-id")[start_idx:end_idx]
    latest_excerpts = Excerpt.objects.order_by("-id")
    paginator = Paginator(latest_excerpts, results_per_page)

    page_obj = paginator.get_page(page_num)

    context = {
            "page_obj": page_obj,
            }

    return render(request, "excerpts/index.html", context)

def excerpt(request, excerpt_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)

    context = { "excerpt": excerpt }
    return render(request, "excerpts/excerpt_page.html", context)

def edit(request, excerpt_id):
    excerpt = Excerpt.objects.get(id=excerpt_id)

    context = { "excerpt": excerpt }
    return render(request, "excerpts/edit_page.html", context)

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
