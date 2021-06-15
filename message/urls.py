from django.urls import path

from message.views import *


urlpatterns = [
    path('finish/', finish),
    path('save/', save),
    path('delete/', delete),
    path('unfinish/', unfinish),

    path('getDone/', getDoneMes),
    path('getUnread/', getUnread),
    path('getSave/', getSave),

    path('getAll/', getAll),
]
