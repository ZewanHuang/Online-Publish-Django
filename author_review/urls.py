from django.conf import settings
from django.urls import path
from author_review.views import *

from django.conf.urls.static import static

urlpatterns = [
    path('apply/', apply_writer),
    path('upload/', upload),
    path('author_review/', remark),
    path('writing/', writing_info),
    path('review/', review_info),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
