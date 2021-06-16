import json

from django.db.models import F
from django.http import JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from message.models import Message
from user.models import User
from utils.response_code import *


@csrf_exempt
def finish(request):
    this_id = request.POST.get('mid')
    try:
        this_message = Message.objects.get(id=this_id)
    except:
        return JsonResponse({'status_code': FinishMesStatus.MES_NOT_FOUND})

    this_message.message_type = '已读'
    this_message.save()
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def save(request):
    this_id = request.POST.get('mid')
    try:
        this_message = Message.objects.get(id=this_id)
    except:
        return JsonResponse({'status_code': FinishMesStatus.MES_NOT_FOUND})

    this_message.message_type = '收藏'
    this_message.save()
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def unfinish(request):
    this_id = request.POST.get('mid')
    try:
        this_message = Message.objects.get(id=this_id)
    except:
        return JsonResponse({'status_code': FinishMesStatus.MES_NOT_FOUND})

    this_message.message_type = '未读'
    this_message.save()
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def delete(request):
    this_id = request.POST.get('mid')
    try:
        this_message = Message.objects.get(id=this_id)
    except:
        return JsonResponse({'status_code': FinishMesStatus.MES_NOT_FOUND})

    this_message.delete()
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def getDoneMes(request):
    this_login = request.session.get('is_login')
    if this_login:
        try:
            this_username = request.session.get('username')
            this_user = User.objects.get(username=this_username)
        except:
            return JsonResponse({'status_code': MesStatus.USER_NOT_EXISTS})

        done_messages = Message.objects.filter(user=this_user, message_type='已读')

        mesList = []
        for message in done_messages:
            info = {
                'title': message.title,
                'content': message.content,
                'type': message.message_type,
                'time': message.c_time.strftime("%Y/%m/%d %H:%M:%S")
            }
            mesList.append(info)

        return JsonResponse({'status_code': SUCCESS, 'messages': json.dumps(mesList, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': MesStatus.USER_NOT_LOGIN})


@csrf_exempt
def getSave(request):
    this_login = request.session.get('is_login')
    if this_login:
        try:
            this_username = request.session.get('username')
            this_user = User.objects.get(username=this_username)
        except:
            return JsonResponse({'status_code': MesStatus.USER_NOT_EXISTS})

        done_messages = Message.objects.filter(user=this_user, message_type='收藏')

        mesList = []
        for message in done_messages:
            info = {
                'title': message.title,
                'content': message.content,
                'type': message.message_type,
                'time': message.c_time
            }
            mesList.append(info)

        return JsonResponse({'status_code': SUCCESS, 'messages': json.dumps(mesList, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': MesStatus.USER_NOT_LOGIN})


@csrf_exempt
def getUnread(request):
    this_login = request.session.get('is_login')
    if this_login:
        try:
            this_username = request.session.get('username')
            this_user = User.objects.get(username=this_username)
        except:
            return JsonResponse({'status_code': MesStatus.USER_NOT_EXISTS})

        messages = Message.objects.filter(user=this_user, message_type='未读')
        mesCount = messages.count()

        mesList = []
        for message in messages:
            info = {
                'tag': message.title,
                'content': message.content,
                'state': '1',
                'time': message.c_time.strftime("%Y/%m/%d %H:%M:%S"),
                'mid': message.id,
            }
            mesList.append(info)

        return JsonResponse({
            'status_code': SUCCESS,
            'msgCount': mesCount,
            'messages': json.dumps(mesList, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': MesStatus.USER_NOT_LOGIN})


@csrf_exempt
def getAll(request):
    this_login = request.session.get('is_login')
    if this_login:
        try:
            this_username = request.session.get('username')
            this_user = User.objects.get(username=this_username)
        except:
            return JsonResponse({'status_code': MesStatus.USER_NOT_EXISTS})

        messages = Message.objects.filter(user=this_user).order_by((F('c_time').desc()))

        mesList = []
        for message in messages:
            if message.message_type == '未读':
                state = '1'
            elif message.message_type == '已读':
                state = '2'
            else:
                state = '3'

            info = {
                'tag': message.title,
                'content': message.content,
                'state': state,
                'time': message.c_time.strftime("%Y/%m/%d %H:%M:%S"),
                'mid': message.id,
            }
            mesList.append(info)

        return JsonResponse({'status_code': SUCCESS, 'messages': json.dumps(mesList, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': MesStatus.USER_NOT_LOGIN})

