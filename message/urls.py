from django.urls import path

from message.views import *


urlpatterns = [
    path('finish/', finish_message),
    path('done/', done_mes),
    path('unread/', unread_mes),
    path('save/', save_mes),
]
