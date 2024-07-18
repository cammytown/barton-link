"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    #@TODO directing both the root and /excerpts/ to the same view until we decide
    # if there will be another module for barton link other than excerpts.
    # probably make that decision soon; hope this doesn't come back to bite us
    path('', include('excerpts.urls')),
    path('excerpts/', include('excerpts.urls')),

    path('admin/', admin.site.urls),
]
