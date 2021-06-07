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
    path('self-userinfo/', self_user_info),
    path('collect/', collect),

    path('upload_image/', upload_avatar),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
