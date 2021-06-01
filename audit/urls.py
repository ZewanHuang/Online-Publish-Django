from django.conf import settings
from django.urls import path
from audit.views import *

from django.conf.urls.static import static

urlpatterns = [
    path('apply/', apply_writer),
    path('upload/', upload),
    path('review/', review),
    path('writing/', writing),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
