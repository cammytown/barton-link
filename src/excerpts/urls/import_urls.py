from django.urls import path

from ..views.imports.import_views import (
    import_excerpts, import_file, import_text,
    import_gdocs, import_excerpts_confirm
)
from ..views.imports.gdocs_handler import gdocs_test

urlpatterns = [
    path("import", import_excerpts, name="import"),
    path("import/file-upload", import_file, name="import_file_upload"),
    path("import/text-paste", import_text, name="import_text_paste"),
    path("import/gdocs", import_gdocs, name="import_gdocs"),
    path("confirm-import", import_excerpts_confirm, name="import_confirm"),
    path("gdocs-test", gdocs_test, name="test"),
] 