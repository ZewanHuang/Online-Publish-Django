from django.conf import settings
from django.urls import path

from django.conf.urls.static import static

from editor.views import *

urlpatterns = [
    path('register_editor/', register_editor),
    path('add_review/', add_review),
    path('editor/', editor_info),
    path('allot/', allot_review),
    path('status/', update_status),
    path('delete/', delete_article),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)