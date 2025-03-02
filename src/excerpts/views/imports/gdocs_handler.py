import re
from django.shortcuts import render
from django.http import HttpResponse
from barton_link.gdocs_parser import GDocsParser
from . import utils

def post_import_gdocs(request, default_tags):
    """
    Handle Google Docs imports.
    """
    # Get Google Docs URLs textarea
    gdoc_urls = request.POST.get("gdocs_urls").split("\n")

    # Extract document IDs from URLs
    doc_id_regex = r"/document/d/([a-zA-Z0-9-_]+)"
    document_ids = [re.search(doc_id_regex, url).group(1) for url in gdoc_urls]

    # Initialize Google Docs API
    gdocs = GDocsParser()

    # Load credentials
    gdocs.load_credentials()

    parser_excerpts = []

    # Load and parse each Google Doc
    for document_id in document_ids:
        # Load document
        document = gdocs.get_document(document_id)
        parser_excerpts += gdocs.parse_document(document, default_tags)

    # Check for duplicate excerpts
    excerpts, duplicates = utils.check_for_duplicate_excerpts(parser_excerpts)

    # Count non-duplicate excerpts
    non_duplicate_count = sum(1 for e in excerpts if not e.is_duplicate)

    # Save excerpts to cache instead of session and get a preview ID
    preview_id, all_excerpts, new_tags = utils.save_excerpts_to_cache(excerpts, duplicates)

    # Present confirmation page
    return render(request, "excerpts/import/_import_confirmation.html", {
        "excerpts": excerpts,
        "duplicates": duplicates,
        "default_tags": default_tags,
        "new_tags": new_tags,
        "non_duplicate_count": non_duplicate_count,
        "preview_id": preview_id,  # Pass the preview ID to the template
    })

def gdocs_test(request):
    """
    Test function for Google Docs integration.
    """
    # Initialize Google Docs API
    gdocs = GDocsParser()

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

    # Load and parse each Google Doc
    for document_id in document_ids:
        # Load document
        document = gdocs.get_document(document_id)
        parser_excerpts = gdocs.parse_document(document)

        excerpts, duplicates = utils.actualize_parser_excerpts(parser_excerpts)

        response += f"\nLoaded {len(parser_excerpts)} excerpts from {document_id}."

    return HttpResponse(response)
