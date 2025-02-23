from django.http import HttpResponse
from ...models import Excerpt, Tag
from barton_link.base_parser import ParserExcerpt

def check_for_duplicate_excerpts(excerpts):
    """
    Check for duplicate excerpts in the database.
    Returns a tuple of (non_duplicates, duplicates).
    """
    print("Checking for duplicate excerpts...")
    duplicates = []
    for excerpt in excerpts:
        # If excerpt is a duplicate
        if Excerpt.objects.filter(content=excerpt.content):
            # Add excerpt to duplicates
            duplicates.append(excerpt)

    # Remove duplicates from excerpts
    excerpts = [excerpt for excerpt in excerpts if excerpt not in duplicates]

    return excerpts, duplicates

def save_excerpts_to_session(request, excerpts):
    """
    Save excerpts to session for later confirmation.
    """
    request.session["excerpts"] = [excerpt.to_dict() for excerpt in excerpts]

def actualize_parser_excerpts(parser_excerpts: list[ParserExcerpt]):
    """
    Add excerpts from parser excerpt array.
    Returns a tuple of (created_excerpts, duplicate_excerpts).
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
    Returns a tuple of (excerpt_instance, was_created).
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

def get_tags_from_filename(filename: str,
                           regex: str,
                           regex_group_separator = None) -> list[str]:
    """
    Get tags from filename using regex.
    """
    import re

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
