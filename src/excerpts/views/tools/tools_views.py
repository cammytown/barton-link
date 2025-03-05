# Tools-specific functionality

from django.shortcuts import render, redirect
from django.contrib import messages

# Import views from other files
from .similarity_views import (
    analyze_similarities,
    start_similarity_analysis,
    stop_similarity_analysis,
    get_analysis_progress,
)

from .autotag_views import (
    autotag_excerpts,
    start_autotag,
    stop_autotag,
    get_autotag_progress,
)

def tools(request):
    """
    Tools page.
    """
    return render(request, "excerpts/tools/tools_page.html")

def create_default_relationship_types(request):
    """
    Create default relationship types.
    
    GET parameters:
        force: If 'true', will update existing types to match defaults
    """
    from ...utils import setup_default_relationship_types
    
    # Check if force parameter is provided
    force = request.GET.get('force', '').lower() == 'true'
    
    created_count, updated_count = setup_default_relationship_types(force=force)
    
    if created_count > 0:
        messages.success(request, f"Successfully created {created_count} relationship types.")
    
    if updated_count > 0:
        messages.success(request, f"Successfully updated {updated_count} relationship types.")
    
    if created_count == 0 and updated_count == 0:
        messages.info(request, "All default relationship types already exist.")
    
    return redirect('tools')
