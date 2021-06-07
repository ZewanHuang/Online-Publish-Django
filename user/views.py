from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt  # 避免 csrf 错误

from author_review.models import Article
from django3.settings import *

from .form import *
from utils.response_code import *
from utils.send import *
from utils.hash import *

import re
import datetime
import pytz

utc = pytz.UTC


# views

@csrf_exempt
def login(request):
    if request.session.get('is_login', None):  # login repeatedly not allowed
        return JsonResponse({'status_code': LoginStatus.LOGIN_REPEATED})

    if request.method == 'POST':

        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            try:
                user = User.objects.get(username=username)
            except:
                return JsonResponse('status_code', LoginStatus.USERNAME_MISS)

            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['username'] = username
                request.session['type'] = user.user_type

                if not user.has_confirmed:
                    return JsonResponse({'status_code': LoginStatus.USER_NOT_CONFIRM})

                return JsonResponse({'status_code': SUCCESS, 'user_type': user.user_type})

            else:
                return JsonResponse({'status_code': LoginStatus.PASSWORD_ERROR})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def register(request):
    if request.method == 'POST':

        register_form = RegisterForm(request.POST)

        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            email = register_form.cleaned_data.get('email')

            same_name_user = User.objects.filter(username=username)
            if same_name_user:
                return JsonResponse({'status_code': RegisterStatus.USERNAME_REPEATED})

            same_email_user = User.objects.filter(email=email)
            if same_email_user:
                return JsonResponse({'status_code': RegisterStatus.EMAIL_ERROR})

            # 检测密码不符合规范：8-18，英文字母+数字
            if not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,18}$', password1):
                return JsonResponse({'status_code': RegisterStatus.PASSWORD_INVALID})

            if password1 != password2:
                return JsonResponse({'status_code': RegisterStatus.PASSWORD_CONTRAST})

            # 成功
            new_user = User()
            new_user.username = username
            new_user.password = hash_code(password1)
            new_user.email = email
            new_user.save()

            code = make_confirm_string(new_user)
            try:
                send_email_confirm(email, code)
            except:
                new_user.delete()
                return JsonResponse({'status_code': RegisterStatus.SEND_EMAIL_ERROR})

            request.session['is_login'] = True
            request.session['username'] = new_user.username

            return JsonResponse({'status_code': SUCCESS})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

    return JsonResponse({})


@csrf_exempt
def logout(request):
    if not request.session.get('is_login', None):
        return JsonResponse({'status_code': LogoutStatus.USER_NOT_LOGIN})

    request.session.flush()
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def user_confirm(request):
    if request.method == 'POST':
        code = request.POST.get('code')  # get code from url (?code=..)
        try:
            confirm = ConfirmString.objects.get(code=code)
        except:
            return JsonResponse({'status_code': ConfirmStatus.STRING_MISS})

        c_time = confirm.c_time.replace(tzinfo=utc)
        now = datetime.datetime.now().replace(tzinfo=utc)
        if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
            confirm.user.delete()
            return JsonResponse({'status_code': ConfirmStatus.CONFIRM_EXPIRED})
        else:
            confirm.user.has_confirmed = True
            confirm.user.save()
            confirm.delete()
            return JsonResponse({'status_code': SUCCESS})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def unverified_email(request):
    try:
        this_user = User.objects.get(username=request.session['username'])
    except:
        return JsonResponse({'status_code': VerifyStatus.USER_NOT_LOGIN})

    if this_user.has_confirmed:
        return JsonResponse({'status_code': VerifyStatus.CONFIRM_REPEATED})

    if request.method == 'POST':
        resend = request.POST.get('resend')
        if resend == '1':
            try:
                code = ConfirmString.objects.get(user_id=this_user.id).code
                send_email_confirm(this_user.email, code)
            except:
                return JsonResponse({'status_code': VerifyStatus.SEND_EMAIL_ERROR})
            return JsonResponse({'status_code': SUCCESS})
        elif resend != 0 or resend != 1:
            return JsonResponse({'status_code': FORM_ERROR})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def upload_avatar(request):
    if request.method == 'POST':
        upload_form = UploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            this_user = User.objects.get(username=request.session['username'])
            this_user.avatar.delete()
            this_user.avatar = request.FILES['file']
            this_user.save()
            return JsonResponse({'status_code': '2000'})
        else:
            return JsonResponse({'status_code': '4001'})
    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def user_info(request):
    if request.method == 'POST':
        that_username = request.POST.get('username')
        that_user = get_object_or_404(User, username=that_username)

        info = {
            'username': that_user.username,
            'email': that_user.email,
            'type': that_user.user_type,
            'description': that_user.user_desc,
            'real_name': that_user.real_name,
            'education': that_user.education_exp,
            'job': that_user.job_unit
        }
        if that_user.avatar:
            info['avatar'] = WEB_ROOT + that_user.avatar.url
        else:
            info['avatar'] = WEB_ROOT + '/media/avatar/user_default/' + '2.png'
        return JsonResponse({'status_code': SUCCESS, 'user': json.dumps(info, ensure_ascii=False)})


@csrf_exempt
def collect(request):
    if request.method == 'GET':
        article_id = request.GET.get('article_id')
        username = request.session.get('username')
        user = User.objects.get(username=username)
        article = Article.objects.filter(article_id=article_id)
        if article:
            new_collect = Collect()
            new_collect.user = user
            new_collect.article_id = article_id
            new_collect.save()
            return JsonResponse({'status_code': SUCCESS})
        else:
            return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})

    else:
        return JsonResponse({'status_code': DEFAULT})
