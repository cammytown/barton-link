from django.shortcuts import render
from barton_link.markdown_parser import MarkdownParser
from . import utils

def post_import_text(request, default_tags = []):
    """
    Handle text paste imports.
    """
    # Get text from textarea
    text = request.POST.get("excerpts")

    # Parse text into ParserExcerpt objects
    mdParser = MarkdownParser()
    parser_excerpts = mdParser.parse_text(text, default_tags)

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
