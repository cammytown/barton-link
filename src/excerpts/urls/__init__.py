"""
URL configuration for the excerpts app.

This package contains URL patterns for different functional areas of the app.
"""
from django.urls import path, include

# Import URL patterns from separate modules
from .excerpt_urls import urlpatterns as excerpt_urlpatterns
from .entity_urls import urlpatterns as entity_urlpatterns
from .relationship_urls import urlpatterns as relationship_urlpatterns
from .tag_urls import urlpatterns as tag_urlpatterns
from .tool_urls import urlpatterns as tool_urlpatterns
from .import_urls import urlpatterns as import_urlpatterns

# Combine all URL patterns
urlpatterns = []
urlpatterns.extend(excerpt_urlpatterns)
urlpatterns.extend(entity_urlpatterns)
urlpatterns.extend(relationship_urlpatterns)
urlpatterns.extend(tag_urlpatterns)
urlpatterns.extend(tool_urlpatterns)
urlpatterns.extend(import_urlpatterns) 