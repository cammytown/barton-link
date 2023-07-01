import re

from django.http import HttpResponse, HttpResponseNotFound, QueryDict
from django.shortcuts import render

from barton_link.barton_link import BartonLink
from ..models import Excerpt,\
        ExcerptSimilarity,\
        ExcerptVersion,\
        Tag,\
        TagType

barton_link = BartonLink()
from barton_link.base_parser import ParserExcerpt
from barton_link.gdocs_parser import GDocsParser
from barton_link.markdown_parser import MarkdownParser

def analyze_similarities(request):
    """
    Analyze similarities between excerpts using NLP.
    """

    barton_link.load_nlp_models() #@REVISIT architecture

    created_count = 0

    # Get all excerpts, order by ascending id
    excerpts = Excerpt.objects.order_by("id")

    # For each excerpt
    for excerpt in excerpts:
        # Get excerpt text
        excerpt_text = excerpt.content

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
            other_excerpt_text = other_excerpt.content

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

def import_excerpts(request):
    match request.method:
        case "GET":
            tags = Tag.objects.all()
            tag_types = TagType.objects.all()

            return render(request, "excerpts/import/import_page.html", {
                "tags": tags,
                "tag_types": tag_types,
                })

        case "POST":
            # Get files from multiple file input
            files = request.FILES.getlist("files")

            # Get default tags
            default_tags = request.POST.getlist("toggled_tags[]")
            #@REVISIT .name is weird but I guess I want to keep it as str until
            #@ filename tags are real
            default_tags = [Tag.objects.get(id=tag_id).name for tag_id in default_tags]

            filename_to_tag_regex = request.POST.get("filename_to_tag_regex")
            regex_group_separator = request.POST.get("regex_group_separator")

            #@TEMPORARY
            mdParser = MarkdownParser()

            excerpts = []

            # Read files
            print("Reading files...")
            for file in files:
                # If filename_to_tag_regex is not empty
                if filename_to_tag_regex:
                    # Get filename
                    filename = file.name

                    # Get tags from filename
                    filename_tags = get_tags_from_filename(filename,
                                                           filename_to_tag_regex,
                                                           regex_group_separator)

                else:
                    filename_tags = []

                file_content = file.read().decode("utf-8")
                excerpts += mdParser.parse_text(file_content,
                                                default_tags + filename_tags)

            # Check for duplicate excerpts
            print("Checking for duplicate excerpts...")
            duplicates = []
            for excerpt in excerpts:
                # If excerpt is a duplicate
                if Excerpt.objects.filter(content=excerpt.content):
                    # Add excerpt to duplicates
                    duplicates.append(excerpt)

            # Remove duplicates from excerpts
            excerpts = [excerpt for excerpt in excerpts if excerpt not in duplicates]

            # Save excerpts to session as dicts
            request.session["excerpts"] = [excerpt.to_dict() for excerpt in excerpts]

            # Present confirmation page
            return render(request, "excerpts/import/_import_confirmation.html", {
                "excerpts": excerpts,
                "duplicates": duplicates,
                "default_tags": default_tags,
            })

        case _:
            return HttpResponseNotFound()

def get_tags_from_filename(filename: str,
                           regex: str,
                           regex_group_separator = None) -> list[str]:
    """
    Get tags from filename using regex.
    """

    # Get matches
    matches = re.findall(regex, filename)

    # If regex_group_separator is not None
    if regex_group_separator:
        # Split matches
        matches = [match.split(regex_group_separator) for match in matches]

        # Flatten matches
        matches = [match for sublist in matches for match in sublist]

    # Return matches
    return matches

def import_file(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        match request.method:
            case "GET":
                return render(request, "excerpts/import/_file_upload.html")
            case _:
                return HttpResponseNotFound()

    # If not HTMX request
    else:
        return HttpResponseNotFound()

def import_text(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        match request.method:
            case "GET":
                return render(request, "excerpts/import/_text_paste.html")
            case _:
                return HttpResponseNotFound()

    # If not HTMX request
    else:
        return HttpResponseNotFound()

def import_gdocs(request):
    # If HTMX request
    if request.headers.get("HX-Request") == "true":
        match request.method:
            case "GET":
                return render(request, "excerpts/import/_gdocs.html")
            case _:
                return HttpResponseNotFound()

    # If not HTMX request
    else:
        return HttpResponseNotFound()

def import_excerpts_confirm(request):
    """
    Confirm import excerpts.
    """

    # Get excerpts from session
    excerpts = request.session["excerpts"]

    # Convert to ParserExcerpt
    parser_excerpts = [ParserExcerpt.from_dict(excerpt) for excerpt in excerpts]

    print("Adding excerpts...")
    # Add excerpts; checking for duplicates
    # Any duplicates should be internal to the list of excerpts since we
    # already checked for duplicates in the import_excerpts view
    #@REVISIT is this confusing or precarious? can we make it clearer? we rely on this being true

    # Create database Excerpt from ParserExcerpt
    excerpts, internal_duplicates = actualize_parser_excerpts(parser_excerpts)

    # Remove excerpts from session
    del request.session["excerpts"]

    # Return import success page
    return render(request, "excerpts/import/_import_success.html", {
        "excerpts": parser_excerpts,
        "internal_duplicates": internal_duplicates,
    })

#@TODO probably:
# def import_excerpts_cancel(request):
#     """
#     Cancel import excerpts.
#     """

#     # Remove excerpts from session
#     del request.session["excerpts"]

#     # Return import cancel page
#     return render(request, "excerpts/import/_import_cancel.html")

def actualize_parser_excerpts(parser_excerpts: list[ParserExcerpt]):
    """
    Add excerpts from parser excerpt array.
    """

    excerpts = []
    duplicates = []

    for index, parser_excerpt in enumerate(parser_excerpts):
        print(f"Adding excerpt {index + 1} of {len(parser_excerpts)}...")
        print(f"Excerpt: {parser_excerpt}")
        instance, created = actualize_parser_excerpt(parser_excerpt)

        if created:
            excerpts.append(instance)
        else:
            duplicates.append(instance)

    return excerpts, duplicates

def actualize_parser_excerpt(parser_excerpt: ParserExcerpt):
    """
    Add excerpt from parser excerpt.
    """

    print(f"Adding excerpt: {parser_excerpt}")

    # Add children
    children = []
    for child in parser_excerpt.children:
        child_instance, _ = actualize_parser_excerpt(child)
        children.append(child_instance)

    # Create excerpt instance or get existing identical instance
    excerpt_instance, created = Excerpt.objects.get_or_create(
            content=parser_excerpt.content,)

    # Set excerpt instance attributes
    excerpt_instance.metadata = parser_excerpt.metadata

    # Save excerpt instance (create id)
    excerpt_instance.save()

    # Add default tags
    for tag in parser_excerpt.tags:
        # Get or create tag
        #@TODO keep track of created tags; show user
        tag_instance, _ = Tag.objects.get_or_create(name=tag)

        # Add tag to excerpt
        excerpt_instance.tags.add(tag_instance)

    # Add children
    for child in children:
        # Django won't duplicate children; safe to use add()
        #@REVISIT this feels scary. maybe just check anyway?
        excerpt_instance.children.add(child)

    # Save excerpt instance again
    #@REVISIT have to save twice because both need id, right?
    excerpt_instance.save()

    return excerpt_instance, created

def gdocs_test(request):
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

        excerpts, duplicates = actualize_parser_excerpts(parser_excerpts)

        response += f"\nLoaded {len(parser_excerpts)} excerpts from {document_id}."

    return HttpResponse(response)
