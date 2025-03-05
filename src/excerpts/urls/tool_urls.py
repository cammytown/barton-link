from django.urls import path

from ..views.tools.tools_views import (
    tools, create_default_relationship_types
)
from ..views.tools.similarity_views import (
    analyze_similarities, start_similarity_analysis, 
    stop_similarity_analysis, get_analysis_progress
)
from ..views.tools.autotag_views import (
    autotag_excerpts, start_autotag, stop_autotag, get_autotag_progress
)

urlpatterns = [
    path("tools", tools, name="tools"),
    
    # Autotag URLs
    path("autotag", autotag_excerpts, name="autotag"),
    path("start-autotag", start_autotag, name="start_autotag"),
    path("stop-autotag", stop_autotag, name="stop_autotag"),
    path("get-autotag-progress",
         get_autotag_progress,
         name="get_autotag_progress"),
    
    # Similarity analysis URLs
    path("analyze-similarities",
         analyze_similarities,
         name="analyze_similarities"),
    path("start-similarity-analysis",
         start_similarity_analysis,
         name="start_similarity_analysis"),
    path("stop-similarity-analysis",
         stop_similarity_analysis,
         name="stop_similarity_analysis"),
    path("get-analysis-progress",
         get_analysis_progress,
         name="get_analysis_progress"),
    
    # Other tools
    path("create-default-relationship-types",
         create_default_relationship_types,
         name="create_default_relationship_types"),
] 