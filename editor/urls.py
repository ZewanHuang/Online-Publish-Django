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

    path('count_person/', count_person),
    path('count_article/', count_article),
    path('count_remark/', count_remark),
    path('count/', count),

    path('get_authors/', get_authors),
    path('get_readers/', get_readers),
    path('get_reviews/', get_reviews),
    path('get_reviews_name/', get_reviews_name),

    path('get_articles_0/', get_articles_0),
    path('get_articles_1/', get_articles_1),
    path('get_articles_2/', get_articles_2),
    path('get_articles_4/', get_articles_4),

    path('get_remarks_all/', get_remarks_all),
    path('get_remarks_undo/', get_remarks_undo),
    path('get_remarks_done/', get_remarks_done),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)