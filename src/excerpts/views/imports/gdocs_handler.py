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

    # Save excerpts to session
    utils.save_excerpts_to_session(request, excerpts)

    # Present confirmation page
    return render(request, "excerpts/import/_import_confirmation.html", {
        "excerpts": excerpts,
        "duplicates": duplicates,
        "default_tags": default_tags,
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
