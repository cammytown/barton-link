from django.http import HttpResponse
from django.shortcuts import render

from ...services import SimilarityAnalysisService

similarity_analysis = SimilarityAnalysisService()

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