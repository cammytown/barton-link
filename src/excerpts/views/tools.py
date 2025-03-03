# Tools-specific functionality

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.contrib import messages

from ..services import SimilarityAnalysisService

similarity_analysis = SimilarityAnalysisService()

def tools(request):
    """
    Tools page.
    """
    return render(request, "excerpts/tools/tools_page.html")

def analyze_similarities(request):
    """
    Index page for excerpt similarity analysis.
    """
    status = similarity_analysis.get_status()
    return render(request, "excerpts/tools/analyze_similarities.html", status)

def start_similarity_analysis(request):
    """
    Start similarity analysis.
    """
    similarity_analysis.start()
    return get_analysis_progress(request)

def stop_similarity_analysis(request):
    """
    Stop similarity analysis.
    """
    similarity_analysis.stop()
    return HttpResponse("Similarity analysis stopped.")

def get_analysis_progress(request):
    """
    Get similarity analysis progress.
    """
    status = similarity_analysis.get_status()
    return render(request, "excerpts/tools/_analysis_progress.html", status)

def create_default_relationship_types(request):
    """
    Create default relationship types.
    
    GET parameters:
        force: If 'true', will update existing types to match defaults
    """
    from ..utils import setup_default_relationship_types
    
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