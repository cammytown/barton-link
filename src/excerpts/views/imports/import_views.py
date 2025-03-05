from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render
from ...models import Tag, TagType
from barton_link.parser_excerpt import ParserExcerpt
from . import utils
from . import file_handler
from . import text_handler
from . import gdocs_handler
import json

def import_excerpts(request):
    """
    Main import view that handles both GET and POST requests.
    GET: Shows import options page
    POST: Handles import based on selected method
    """
    match request.method:
        case "GET":
            tags = Tag.objects.all()
            tag_types = TagType.objects.all()

            return render(request, "excerpts/import/import_page.html", {
                "tags": tags,
                "tag_types": tag_types,
            })

        case "POST":
            # Get default tags
            default_tags = request.POST.getlist("toggled_tags[]")
            default_tags = [Tag.objects.get(id=tag_id).name for tag_id in default_tags]

            match request.POST.get("import_method"):
                case "text_paste":
                    return text_handler.post_import_text(request, default_tags)

                case "upload":
                    return file_handler.post_import_files(request, default_tags)

                case "gdocs":
                    return gdocs_handler.post_import_gdocs(request, default_tags)

                case _:
                    print("Invalid import method.")
                    return HttpResponseBadRequest(json.dumps({
                        "error": "Invalid import method.",
                    }))

        case _:
            return HttpResponseNotAllowed(["GET", "POST"])

def import_file(request):
    """
    Handle file upload import method selection.
    """
    if request.headers.get("HX-Request") == "true":
        match request.method:
            case "GET":
                return render(request, "excerpts/import/_file_upload.html")
            case _:
                return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()

def import_text(request):
    """
    Handle text paste import method selection.
    """
    if request.headers.get("HX-Request") == "true":
        match request.method:
            case "GET":
                return render(request, "excerpts/import/_text_paste.html")
            case _:
                return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()

def import_gdocs(request):
    """
    Handle Google Docs import method selection.
    """
    if request.headers.get("HX-Request") == "true":
        match request.method:
            case "GET":
                return render(request, "excerpts/import/_gdocs.html")
            case _:
                return HttpResponseNotFound()
    else:
        return HttpResponseNotFound()

def import_excerpts_confirm(request):
    """
    Confirm import excerpts.
    """
    # Get the preview ID from the form
    preview_id = request.POST.get("preview_id")
    if not preview_id:
        return HttpResponseBadRequest(json.dumps({
            "error": "No preview ID provided."
        }))
    
    # Retrieve excerpts from cache
    excerpts, new_tags = utils.retrieve_excerpts_from_cache(preview_id)
    if not excerpts:
        return HttpResponseBadRequest(json.dumps({
            "error": "Import preview not found or expired."
        }))

    # Get selected tags to create
    tags_to_create = set(request.POST.getlist("create_tags[]"))

    # Convert to ParserExcerpt
    parser_excerpts = excerpts  # Already converted by retrieve_excerpts_from_cache

    # Filter out tags that shouldn't be created
    for excerpt in parser_excerpts:
        excerpt.tags = [tag for tag in excerpt.tags if tag not in new_tags or tag in tags_to_create]

    print("Adding excerpts...")
    # Create database Excerpt from ParserExcerpt
    created_excerpts, duplicate_excerpts = utils.actualize_parser_excerpts(parser_excerpts)

    # Remove excerpts from cache
    utils.delete_excerpts_from_cache(preview_id)

    # Return import success page
    return render(request, "excerpts/import/_import_success.html", {
        "excerpts": created_excerpts,
        "internal_duplicates": duplicate_excerpts,
    })
