from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from editor.views import *

urlpatterns = [
    path('register_editor/', register_editor),

    path('editor/', editor_info),

    path('update_status/', update_status),

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

    path('allot/', allot_review),

    path('get_remarks_all/', get_remarks_all),
    path('get_remarks_undo/', get_remarks_undo),
    path('get_remarks_done/', get_remarks_done),

    path('add_review/', add_review),
    path('add_writer/', add_writer),
    path('add_reader/', add_reader),

    path('del_user/', del_user),
    path('delete/', delete_article),

    path('get_category/', get_category),
    path('add_category/', add_category),
    path('del_category/', del_category),

    path('get_article_detail/', get_article_detail),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)