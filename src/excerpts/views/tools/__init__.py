# This file is intentionally left empty.
# Views should be imported directly from their modules.

# Import views from tools_views.py
from .tools_views import (
    tools,
    create_default_relationship_types,
)

# Import views from similarity_views.py
from .similarity_views import (
    analyze_similarities,
    start_similarity_analysis,
    stop_similarity_analysis,
    get_analysis_progress,
)

# Import views from autotag_views.py
from .autotag_views import (
    autotag_excerpts,
    start_autotag,
    stop_autotag,
    get_autotag_progress,
)

__all__ = [
    # Core tools views
    'tools',
    'create_default_relationship_types',
    
    # Similarity analysis views
    'analyze_similarities',
    'start_similarity_analysis',
    'stop_similarity_analysis',
    'get_analysis_progress',
    
    # Autotag views
    'autotag_excerpts',
    'start_autotag',
    'stop_autotag',
    'get_autotag_progress',
]
