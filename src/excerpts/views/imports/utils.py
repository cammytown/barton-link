from django.http import HttpResponse
from ...models import Excerpt, Tag, TagType
from barton_link.parser_excerpt import ParserExcerpt

def check_for_duplicate_excerpts(excerpts):
    """
    Check for duplicate excerpts both within the input list and against the database.
    Returns a tuple of (non_duplicates, duplicates).
    
    Note: Even if a parent excerpt is a duplicate, its children might be unique.
    The actualize_parser_excerpt function will handle adding unique children to
    existing parent excerpts.
    
    IMPORTANT: This function only identifies top-level duplicates. If a duplicate has
    children, it should still be processed to ensure its unique children are saved.
    
    Args:
        excerpts: List of ParserExcerpt objects to check for duplicates
        
    Returns:
        tuple: (non_duplicates, duplicates) where both are lists of ParserExcerpt objects
    """
    print("Checking for duplicate excerpts...")
    
    # Step 1: Check for duplicates within the input list
    seen_contents = {}
    internal_duplicates = []
    unique_excerpts = []
    
    for excerpt in excerpts:
        # If this excerpt has children, we need to process it regardless
        # to ensure its unique children are saved
        if excerpt.children:
            unique_excerpts.append(excerpt)
        elif excerpt.content in seen_contents:
            internal_duplicates.append(excerpt)
        else:
            seen_contents[excerpt.content] = True
            unique_excerpts.append(excerpt)
    
    # Step 2: Check for duplicates against the database
    # Get all unique content strings from excerpts without children
    unique_contents = [e.content for e in unique_excerpts if not e.children]
    
    # Query database once for all potential duplicates
    #@REVISIT method
    existing_contents = set(Excerpt.objects.filter(
        content__in=unique_contents
    ).values_list('content', flat=True))
    
    # Separate duplicates and non-duplicates
    db_duplicates = []
    non_duplicates = []
    
    for excerpt in unique_excerpts:
        # If this excerpt has children, we need to process it regardless
        # to ensure its unique children are saved
        if excerpt.children:
            non_duplicates.append(excerpt)
        elif excerpt.content in existing_contents:
            db_duplicates.append(excerpt)
        else:
            non_duplicates.append(excerpt)
    
    # Combine all duplicates
    all_duplicates = internal_duplicates + db_duplicates
    
    return non_duplicates, all_duplicates

def identify_new_tags(excerpts):
    """
    Identify which tags in the excerpts don't exist in the database.
    Returns a set of new tag names.
    """
    # Get all unique tags from excerpts
    all_tags = set()
    for excerpt in excerpts:
        all_tags.update(excerpt.tags)
    
    # Get existing tags from database
    existing_tags = set(Tag.objects.values_list('name', flat=True))
    
    # Return tags that don't exist in database
    return all_tags - existing_tags

def save_excerpts_to_session(request, excerpts):
    """
    Save excerpts to session for later confirmation.
    Also saves information about new tags that would be created.
    """
    # Save excerpts
    request.session["excerpts"] = [excerpt.to_dict() for excerpt in excerpts]
    
    # Save new tags
    new_tags = identify_new_tags(excerpts)
    request.session["new_tags"] = list(new_tags)

def actualize_parser_excerpts(parser_excerpts: list[ParserExcerpt]):
    """
    Add excerpts from parser excerpt array.
    Returns a tuple of (created_excerpts, duplicate_excerpts).
    
    Both lists contain the original ParserExcerpt objects, not the Django model instances.
    This ensures consistency with what the templates expect.
    
    Note: This function processes all excerpts, including duplicates with children,
    to ensure that unique children of duplicate parents are saved.
    """
    created_excerpts = []
    duplicate_excerpts = []

    for index, parser_excerpt in enumerate(parser_excerpts):
        print(f"Adding excerpt {index + 1} of {len(parser_excerpts)}...")
        print(f"Excerpt: {parser_excerpt}")
        instance, created = actualize_parser_excerpt(parser_excerpt)

        if created:
            created_excerpts.append(parser_excerpt)
        else:
            duplicate_excerpts.append(parser_excerpt)

    return created_excerpts, duplicate_excerpts

def get_or_create_default_tag_type():
    """
    Get or create the default TagType.
    """
    default_tag_type, created = TagType.objects.get_or_create(
        id=1,
        defaults={
            'name': 'default',
            'description': 'Default tag type'
        }
    )
    return default_tag_type

def actualize_parser_excerpt(parser_excerpt: ParserExcerpt):
    """
    Add excerpt from parser excerpt.
    Returns a tuple of (excerpt_instance, was_created).
    """
    print(f"Adding excerpt: {parser_excerpt}")

    # Create excerpt instance or get existing identical instance first
    # This way we know if we're dealing with an existing excerpt before processing children
    excerpt_instance, created = Excerpt.objects.get_or_create(
            content=parser_excerpt.content,)

    # Set excerpt instance attributes
    excerpt_instance.metadata = parser_excerpt.metadata

    # Save excerpt instance (create id)
    excerpt_instance.save()

    # Ensure default tag type exists
    #@REVISIT architecture
    default_tag_type = get_or_create_default_tag_type()

    # Add default tags
    for tag in parser_excerpt.tags:
        # Get or create tag with default tag type
        tag_instance, _ = Tag.objects.get_or_create(
            name=tag,
            defaults={'type': default_tag_type, 'description': ''}
        )

        # Add tag to excerpt
        excerpt_instance.tags.add(tag_instance)

    # Process children after parent is created/retrieved
    children = []
    for child in parser_excerpt.children:
        child_instance, _ = actualize_parser_excerpt(child)
        children.append(child_instance)

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
