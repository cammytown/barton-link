from django.http import HttpResponse
from ...models import Excerpt, Tag, TagType
from barton_link.parser_excerpt import ParserExcerpt
import uuid
from django.core.cache import cache

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
    
    # Step 1: Collect all excerpt contents (including children) for duplicate checking
    all_excerpt_contents = {}  # Maps content to excerpt for all excerpts (including children)
    
    # Helper function to collect all excerpt contents recursively
    def collect_all_contents(excerpt, path=""):
        # Add the excerpt to the map
        if excerpt.content in all_excerpt_contents:
            all_excerpt_contents[excerpt.content].append((excerpt, path))
        else:
            all_excerpt_contents[excerpt.content] = [(excerpt, path)]
        
        # Recursively collect children
        for i, child in enumerate(excerpt.children):
            collect_all_contents(child, f"{path}_{i}" if path else str(i))
    
    # Collect all contents
    for i, excerpt in enumerate(excerpts):
        collect_all_contents(excerpt, str(i))
    
    # Step 2: Mark duplicates within the input list
    seen_contents = {}
    for content, excerpt_list in all_excerpt_contents.items():
        if len(excerpt_list) > 1:
            # Mark all but the first occurrence as duplicates
            for excerpt, _ in excerpt_list[1:]:
                excerpt.is_duplicate = True
    
    # Step 3: Check for duplicates against the database
    # Get all unique content strings
    unique_contents = list(all_excerpt_contents.keys())
    
    # Query database once for all potential duplicates
    existing_contents = set(Excerpt.objects.filter(
        content__in=unique_contents
    ).values_list('content', flat=True))
    
    # Mark excerpts as duplicates if they exist in the database
    for content in existing_contents:
        if content in all_excerpt_contents:
            for excerpt, _ in all_excerpt_contents[content]:
                excerpt.is_duplicate = True
    
    # Step 4: Separate top-level duplicates and non-duplicates
    internal_duplicates = []
    non_duplicates = []
    
    for excerpt in excerpts:
        if excerpt.is_duplicate:
            internal_duplicates.append(excerpt)
        else:
            non_duplicates.append(excerpt)
    
    return non_duplicates, internal_duplicates

def identify_new_tags(excerpts):
    """
    Identify which tags in the excerpts don't exist in the database.
    Returns a set of new tag names.
    """
    # Get all unique tags from excerpts
    all_tags = set()
    
    def collect_tags_recursively(excerpt):
        # Add tags from this excerpt
        all_tags.update(excerpt.tags)
        
        # Recursively collect tags from children
        for child in excerpt.children:
            collect_tags_recursively(child)
    
    # Collect tags from all excerpts and their children
    for excerpt in excerpts:
        collect_tags_recursively(excerpt)
    
    # Get existing tags from database
    existing_tags = set(Tag.objects.values_list('name', flat=True))
    
    # Return tags that don't exist in database
    return all_tags - existing_tags

def save_excerpts_to_cache(excerpts, duplicates=None):
    """
    Save excerpts to cache for later confirmation.
    Also saves information about new tags that would be created.
    
    Args:
        excerpts: List of non-duplicate ParserExcerpt objects
        duplicates: List of duplicate ParserExcerpt objects (optional)
        
    Returns:
        tuple: (preview_id, all_excerpts, new_tags) where preview_id is a unique identifier,
        all_excerpts is a list of all excerpts including duplicates with unique children,
        and new_tags is a set of new tag names
    """
    # Combine all excerpts for cache storage
    all_excerpts = list(excerpts)
    
    # Include duplicates that have unique children
    if duplicates:
        for duplicate in duplicates:
            # Check if this duplicate has any non-duplicate children
            has_unique_children = any(not child.is_duplicate for child in duplicate.children)
            if has_unique_children:
                all_excerpts.append(duplicate)
    
    # Generate a unique ID for this import preview
    preview_id = str(uuid.uuid4())
    
    # Identify new tags from all excerpts
    new_tags = identify_new_tags(all_excerpts)
    
    # Store in cache with expiration (24 hours)
    cache_data = {
        'excerpts': [excerpt.to_dict() for excerpt in all_excerpts],
        'new_tags': list(new_tags)
    }
    cache.set(f'import_preview:{preview_id}', cache_data, timeout=86400)  # 24 hours
    
    return preview_id, all_excerpts, new_tags

def retrieve_excerpts_from_cache(preview_id):
    """
    Retrieve excerpts data from cache using the preview_id.
    
    Args:
        preview_id: The unique identifier for the import preview
        
    Returns:
        tuple: (excerpts, new_tags) where excerpts is a list of ParserExcerpt objects
        and new_tags is a list of new tag names. Returns (None, None) if not found.
    """
    # Get data from cache
    cache_data = cache.get(f'import_preview:{preview_id}')
    if not cache_data:
        return None, None
    
    # Convert back to ParserExcerpt objects
    excerpts = [ParserExcerpt.from_dict(exc) for exc in cache_data['excerpts']]
    new_tags = cache_data['new_tags']
    
    return excerpts, new_tags

def delete_excerpts_from_cache(preview_id):
    """
    Delete excerpts data from cache.
    
    Args:
        preview_id: The unique identifier for the import preview
    """
    cache.delete(f'import_preview:{preview_id}')

def save_excerpts_to_session(request, excerpts, duplicates=None):
    """
    Save excerpts to session for later confirmation.
    Also saves information about new tags that would be created.
    
    Args:
        request: The HTTP request
        excerpts: List of non-duplicate ParserExcerpt objects
        duplicates: List of duplicate ParserExcerpt objects (optional)
        
    Returns:
        tuple: (all_excerpts, new_tags) where all_excerpts is a list of all excerpts 
        including duplicates with unique children, and new_tags is a set of new tag names
    """
    # Combine all excerpts for session storage
    all_excerpts = list(excerpts)
    
    # Include duplicates that have unique children
    if duplicates:
        for duplicate in duplicates:
            # Check if this duplicate has any non-duplicate children
            has_unique_children = any(not child.is_duplicate for child in duplicate.children)
            if has_unique_children:
                all_excerpts.append(duplicate)
    
    # Save excerpts
    request.session["excerpts"] = [excerpt.to_dict() for excerpt in all_excerpts]
    
    # Save new tags from all excerpts (including duplicates with unique children)
    new_tags = identify_new_tags(all_excerpts)
    request.session["new_tags"] = list(new_tags)
    
    return all_excerpts, new_tags

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

        # Add to the appropriate list based on whether it was created
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

    # If not created, mark as duplicate
    if not created:
        parser_excerpt.is_duplicate = True

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
    unique_children_count = 0
    
    # First, check if any children already exist in the database
    child_contents = [child.content for child in parser_excerpt.children]
    existing_child_contents = set()
    
    if child_contents:
        existing_child_contents = set(Excerpt.objects.filter(
            content__in=child_contents
        ).values_list('content', flat=True))
    
    # Now process each child
    for child in parser_excerpt.children:
        # Check if this child already exists in the database
        if child.content in existing_child_contents:
            child.is_duplicate = True
            
        child_instance, child_created = actualize_parser_excerpt(child)
        
        if child_created:
            unique_children_count += 1
        else:
            # Ensure the is_duplicate flag is set on the child
            child.is_duplicate = True
            
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
