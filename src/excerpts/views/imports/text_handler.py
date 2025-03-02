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
