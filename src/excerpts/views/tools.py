# Tools-specific functionality

from django.http import HttpResponse, HttpResponseNotFound, HttpResponseNotAllowed
from django.shortcuts import render

from ..models import RelationshipType
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
    """
    RelationshipType.objects.get_or_create(name="is_related_to")
    RelationshipType.objects.get_or_create(name="is_part_of")
    RelationshipType.objects.get_or_create(name="is_synonymous_with")
    RelationshipType.objects.get_or_create(name="is_antonymous_with")

    return HttpResponse("Default relationship types created.") 