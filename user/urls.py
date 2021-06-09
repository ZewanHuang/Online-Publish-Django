from django.urls import path
from user.views import *

from django.conf.urls.static import static

urlpatterns = [
    path('login/', login),
    path('register/', register),
    path('logout/', logout),
    path('confirm/', user_confirm),
    path('unverified_email/', unverified_email),
    path('userinfo/', user_info),
    path('collect/', collect),
    path('get_session/', get_session_user),
    path('edit/', userinfo_edit),
    path('search_list/', search_list),
    path('search_exact/', search_exact),
    path('get_collect/', get_collect),

    path('upload_image/', upload_avatar),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
