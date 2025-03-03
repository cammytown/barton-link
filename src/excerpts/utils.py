from .models import RelationshipType

def setup_default_relationship_types(force=False):
    """
    Creates default relationship types if they don't already exist.
    
    Args:
        force (bool): If True, will update existing types to match defaults.
                     If False, will only create missing types.
    
    Returns:
        tuple: (created_count, updated_count) - Number of types created and updated
    """
    # Define default relationship types
    default_types = [
        # Core relationship types (applicable in multiple contexts)
        {
            "name": "Relates to",
            "description": "Generic relationship (X relates to Y)",
            "applicable_contexts": f"{RelationshipType.ENTITY_ENTITY},{RelationshipType.EXCERPT_EXCERPT},{RelationshipType.ENTITY_EXCERPT}"
        },
        
        # Entity-to-Entity specific relationships
        {
            "name": "Is",
            "description": "Identity relationship (X is Y)",
            "applicable_contexts": RelationshipType.ENTITY_ENTITY
        },
        {
            "name": "Obtains",
            "description": "Possession or attribute relationship (X has Y)",
            "applicable_contexts": RelationshipType.ENTITY_ENTITY
        },
        {
            "name": "Contains",
            "description": "Containment relationship (X contains Y)",
            "applicable_contexts": RelationshipType.ENTITY_ENTITY
        },
        {
            "name": "Part of",
            "description": "Component relationship (X is part of Y)",
            "applicable_contexts": RelationshipType.ENTITY_ENTITY
        },
        {
            "name": "Creates",
            "description": "One entity creates another",
            "applicable_contexts": RelationshipType.ENTITY_ENTITY
        },
        {
            "name": "Destroys",
            "description": "One entity destroys another",
            "applicable_contexts": RelationshipType.ENTITY_ENTITY
        },
        {
            "name": "Becomes",
            "description": "One entity becomes another",
            "applicable_contexts": RelationshipType.ENTITY_ENTITY
        },
        # {
        #     "name": "Owns",
        #     "description": "One entity owns another",
        #     "applicable_contexts": RelationshipType.ENTITY_ENTITY
        # },
        # {
        #     "name": "Controls",
        #     "description": "One entity controls or influences another",
        #     "applicable_contexts": RelationshipType.ENTITY_ENTITY
        # },
        # {
        #     "name": "Knows",
        #     "description": "One entity knows another",
        #     "applicable_contexts": RelationshipType.ENTITY_ENTITY
        # },
        
        # Excerpt-to-Excerpt specific relationships
        {
            "name": "Responds",
            "description": "One excerpt responds to another",
            "applicable_contexts": RelationshipType.EXCERPT_EXCERPT
        },
        {
            "name": "Extends",
            "description": "One excerpt extends or elaborates on another",
            "applicable_contexts": RelationshipType.EXCERPT_EXCERPT
        },
        # {
        #     "name": "Opposes",
        #     "description": "One excerpt opposes or contradicts another",
        #     "applicable_contexts": RelationshipType.EXCERPT_EXCERPT
        # },
        {
            "name": "Rephrases",
            "description": "One excerpt expresses the same idea as another using different words",
            "applicable_contexts": RelationshipType.EXCERPT_EXCERPT
        },
        {
            "name": "Summarizes",
            "description": "One excerpt summarizes another",
            "applicable_contexts": RelationshipType.EXCERPT_EXCERPT
        },
        # {
        #     "name": "Follows",
        #     "description": "One excerpt follows chronologically after another",
        #     "applicable_contexts": RelationshipType.EXCERPT_EXCERPT
        # },
        
        # Entity-to-Excerpt specific relationships
        {
            "name": "Mentions",
            "description": "An excerpt mentions an entity",
            "applicable_contexts": RelationshipType.ENTITY_EXCERPT
        },
        {
            "name": "Describes",
            "description": "An excerpt describes an entity",
            "applicable_contexts": RelationshipType.ENTITY_EXCERPT
        },
    ]
    
    # Create relationship types if they don't exist
    created_count = 0
    updated_count = 0
    
    for rt_data in default_types:
        # Check if this relationship type already exists
        existing = RelationshipType.objects.filter(name=rt_data["name"]).first()
        
        if not existing:
            # Create new type
            RelationshipType.objects.create(**rt_data)
            created_count += 1
        elif force:
            # Update existing type if force is True
            for key, value in rt_data.items():
                setattr(existing, key, value)
            existing.save()
            updated_count += 1
    
    return (created_count, updated_count) 