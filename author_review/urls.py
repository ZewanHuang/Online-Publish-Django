from django.conf import settings
from django.urls import path
from author_review.views import *

from django.conf.urls.static import static

urlpatterns = [
    path('apply/', apply_writer),
    path('upload/', upload),
    path('author_review/', write_remark),
    path('writing/', writing_info),
    path('review/', review_info),
    path('popular/', popular_article),
    path('get_article/', search_article),

    path('get_remark/', search_remark_list),
    path('self_remarks_undo/', self_remarks_undo),
    path('self_remarks_done/', self_remarks_done),

    path('article_remark/', search_article_remark),
    path('review_remark/', search_review_remark),
    path('upload_article/', upload_article),
    path('news/', news),

    path('add_read_times/', add_read_times),
    path('add_download_times/', add_download_times),

    path('self_popular/', self_popular),
    path('self_latest/', self_latest),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
