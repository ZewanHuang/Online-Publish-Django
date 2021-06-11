import json

from django.http import JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from message.models import Message
from user.models import User
from utils.response_code import *


@csrf_exempt
def finish_message(request):
    this_id = request.POST.get('message_id')
    try:
        this_message = Message.objects.get(id=this_id)
    except:
        return JsonResponse({'status_code': FinishMesStatus.MES_NOT_FOUND})

    this_message.message_type = '已读'
    this_message.save()
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def done_mes(request):
    this_login = request.session.get('is_login')
    if this_login:
        try:
            this_username = request.session.get('username')
            this_user = User.objects.get(username=this_username)
        except:
            return JsonResponse({'status_code': MesStatus.USER_NOT_EXISTS})

        done_messages = Message.objects.filter(user=this_user, message_type='已读')
        return JsonResponse({'status_code': SUCCESS, 'messages': json.dumps(done_messages, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': MesStatus.USER_NOT_LOGIN})


@csrf_exempt
def save_mes(request):
    this_login = request.session.get('is_login')
    if this_login:
        try:
            this_username = request.session.get('username')
            this_user = User.objects.get(username=this_username)
        except:
            return JsonResponse({'status_code': MesStatus.USER_NOT_EXISTS})

        done_messages = Message.objects.filter(user=this_user, message_type='收藏')
        return JsonResponse({'status_code': SUCCESS, 'messages': json.dumps(done_messages, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': MesStatus.USER_NOT_LOGIN})


@csrf_exempt
def unread_mes(request):
    this_login = request.session.get('is_login')
    if this_login:
        try:
            this_username = request.session.get('username')
            this_user = User.objects.get(username=this_username)
        except:
            return JsonResponse({'status_code': MesStatus.USER_NOT_EXISTS})

        done_messages = Message.objects.filter(user=this_user, message_type='未读')
        return JsonResponse({'status_code': SUCCESS, 'messages': json.dumps(done_messages, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': MesStatus.USER_NOT_LOGIN})
