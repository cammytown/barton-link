from django.shortcuts import render
from barton_link.markdown_parser import MarkdownParser
from . import utils

def post_import_files(request, default_tags = []):
    """
    Handle file upload imports.
    """
    # Get files from multiple file input
    files = request.FILES.getlist("files")

    filename_to_tag_regex = request.POST.get("filename_to_tag_regex")
    regex_group_separator = request.POST.get("regex_group_separator")

    mdParser = MarkdownParser()
    parser_excerpts = []

    # Read files
    print("Reading files...")
    for file in files:
        # If filename_to_tag_regex is not empty
        if filename_to_tag_regex:
            # Get filename
            filename = file.name

            # Get tags from filename
            filename_tags = utils.get_tags_from_filename(filename,
                                                   filename_to_tag_regex,
                                                   regex_group_separator)
        else:
            filename_tags = []

        # Parse file into ParserExcerpt objects
        file_content = file.read().decode("utf-8")
        parser_excerpts += mdParser.parse_text(file_content,
                                           default_tags + filename_tags)

    # Check for duplicate excerpts
    excerpts, duplicates = utils.check_for_duplicate_excerpts(parser_excerpts)

    # Save excerpts to session as dicts
    utils.save_excerpts_to_session(request, excerpts)

    # Get new tags
    new_tags = utils.identify_new_tags(excerpts)

    # Present confirmation page
    return render(request, "excerpts/import/_import_confirmation.html", {
        "excerpts": excerpts,
        "duplicates": duplicates,
        "default_tags": default_tags,
        "new_tags": new_tags,
    })
