from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt  # 避免 csrf 错误

from author_review.models import *
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
                return JsonResponse({'status_code': LoginStatus.USERNAME_MISS})

            if user.password == hash_code(password):
                request.session['is_login'] = True
                request.session['username'] = username

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

            request.session['is_login'] = True
            request.session['username'] = username

            code = make_confirm_string(new_user)
            try:
                send_email_confirm(email, code)
            except:
                new_user.delete()
                return JsonResponse({'status_code': RegisterStatus.SEND_EMAIL_ERROR})

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

    try:
        code = ConfirmString.objects.get(user_id=this_user.id).code
        send_email_confirm(this_user.email, code)
    except:
        this_user.delete()
        return JsonResponse({'status_code': VerifyStatus.SEND_EMAIL_ERROR})

    return JsonResponse({'status_code': SUCCESS, 'email': this_user.email, 'username': this_user.username})


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
def get_session_user(request):
    is_login = request.session.get('is_login')

    if not is_login:
        return JsonResponse({'status_code': GetSessionStatus.USER_NOT_LOGIN})

    self_username = request.session.get('username')
    self_user = get_object_or_404(User, username=self_username)

    info = {
        'is_login': is_login,
        'username': self_user.username,
        'email': self_user.email,
        'type': self_user.user_type,
        'confirmed': self_user.has_confirmed,
        'description': self_user.user_desc,
        'real_name': self_user.real_name,
        'education': self_user.education_exp,
        'job': self_user.job_unit,
    }

    if self_user.avatar:
        info['avatar'] = WEB_ROOT + self_user.avatar.url
    else:
        info['avatar'] = WEB_ROOT + '/media/avatar/user_default/' + '2.png'

    return JsonResponse({'status_code': SUCCESS, 'user': json.dumps(info, ensure_ascii=False)})


@csrf_exempt
def user_info(request):
    if request.method == 'POST':
        that_username = request.POST.get('username')
        that_user = get_object_or_404(User, username=that_username)

        info = {
            'username': that_user.username,
            'email': that_user.email,
            'description': that_user.user_desc,
        }
        if that_user.avatar:
            info['avatar'] = WEB_ROOT + that_user.avatar.url
        else:
            info['avatar'] = WEB_ROOT + '/media/avatar/user_default/' + '2.png'

        self_username = request.session.get('username')
        if self_username == that_username:
            return JsonResponse({'status_code': UserInfoStatus.USER_SELF, 'user': json.dumps(info, ensure_ascii=False)})

        return JsonResponse({'status_code': SUCCESS, 'user': json.dumps(info, ensure_ascii=False)})


@csrf_exempt
def collect(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        username = request.session.get('username')
        user = User.objects.get(username=username)
        article = Article.objects.filter(article_id=int(article_id))
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


@csrf_exempt
def user_collections(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        collections = Collect.objects.filter(user__username=username)
        if collections:
            json_list = []
            for collection in list(collections):
                aid = collection.article_id
                article = Article.objects.get(article_id=aid)
                item = {
                    'article_id': article.article_id,
                    'title': article.title,
                    'abstract': article.abstract,
                    'key': article.key,
                    'content': article.content,
                    'category': article.category.category,
                    'writer': article.writers.all()[0].writer.username,
                    'article_address': article.article_address.url,
                    'writer_email': article.writers.all()[0].writer.email,
                }
                json_list.append(item)

            return JsonResponse({'status_code': SUCCESS, 'articles': json.dumps(json_list)})
        else:
            return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def get_collect(request):
    if request.method == 'POST':
        username = request.session.get('username')
        collections = Collect.objects.filter(user__username=username)
        if collections:
            json_list = []
            for collection in list(collections):
                json_item = {"article_id": collection.article_id}
                json_list.append(json_item)
            return JsonResponse({'status_code': SUCCESS, 'collections': json.dumps(json_list)})

        return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def userinfo_edit(request):
    if request.method == 'POST':

        detail_form = DetailInfoForm(request.POST)

        if detail_form.is_valid():
            real_name = detail_form.cleaned_data.get('real_name')
            education = detail_form.cleaned_data.get('education')
            job = detail_form.cleaned_data.get('job')
            description = detail_form.cleaned_data.get('description')

            username = request.session.get('username')

            if username:
                try:
                    user = User.objects.get(username=username)
                except:
                    return JsonResponse({'status_code': EditDetailInfo.USER_NOT_EXIST})

                user.real_name = real_name
                user.education_exp = education
                user.job_unit = job
                user.user_desc = description
                user.save()

                return JsonResponse({'status_code': SUCCESS})

            else:
                return JsonResponse({'status_code': EditDetailInfo.USER_NOT_LOGIN})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def search_list(request):
    global articles
    if request.method == 'POST':
        writer_name = request.POST.get('realName')
        key = request.POST.get('key')
        category = request.POST.get('category')
        title = request.POST.get('title')

        if writer_name:
            try:
                writer = Writer.objects.get(writer__real_name=writer_name)
            except:
                return JsonResponse({'status_code': WriterStatus.USER_NOT_EXIST})
            # articles = Article.objects.filter(Q(writers__writer=writer) & Q(status=4))
            articles = Article.objects.filter(writer__real_name=writer_name)
        elif key:
            articles = Article.objects.filter(Q(Q(key__contains=key) | Q(title__contains=key)) & Q(status=4))
        elif category:
            articles = Article.objects.filter(Q(category__category=category) & Q(status=4))
        elif title:
            articles = Article.objects.filter(Q(title__contains=title) | Q(status=4))
        else:
            articles = Article.objects.filter(status=4)

        if articles:
            json_list = []
            for article in list(articles):
                if article.article_address:
                    writers_name = []
                    for writer in article.writers.all():
                        writers_name.append(writer.writer.real_name)

                    json_item = {"article_id": article.article_id,
                                 "title": article.title,
                                 "abstract": article.abstract,
                                 "key": article.key,
                                 "content": article.content,
                                 "category": article.category.category,
                                 "writer": ','.join(writers_name),
                                 "read_num": article.read_num,
                                 "download_num": article.download_num}

                    json_list.append(json_item)

            return JsonResponse({'status_code': SUCCESS, 'articles': json.dumps(json_list)})
        else:
            return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})
    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def search_exact(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        remark_id = request.POST.get('remark_id')

        if article_id:
            article = get_object_or_404(Article, article_id=int(article_id))
        elif remark_id:
            remark = get_object_or_404(ArticleRemark, id=int(remark_id))
            article = remark.article
        else:
            return JsonResponse({'status_code': '4001'})

        info = {
            'title': article.title,
            'abstract': article.abstract,
            'key': article.key,
            'content': article.content,
            'category': article.category.category,
            'writer': article.writers.all()[0].writer.real_name,
            'read_num': article.read_num,
            'download_num': article.download_num,
            'article_address': article.article_address.url
        }
        return JsonResponse({'status_code': SUCCESS, 'article': json.dumps(info, ensure_ascii=False)})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def most_popular(request):
    articles = Article.objects.filter(status=4).order_by((F('read_num') + F('download_num')).desc())
    idx = 0

    article_list = []
    for article in articles:
        if bool(article.article_address):
            writers_name = []
            for writer in article.writers.all():
                writers_name.append(writer.writer.real_name)
            info = {
                "aid": article.article_id,
                "title": article.title,
                "abstract": article.abstract,
                "key": article.key,
                "content": article.content,
                "status": article.status,
                "category": article.category.category,
                "writer": ','.join(writers_name),
                "read_num": article.read_num,
                "download_num": article.download_num,
                "article_address": article.article_address.url
            }
            article_list.append(info)

            if (++idx) >= 10:
                break

    if article_list:
        return JsonResponse({'status_code': SUCCESS, 'articles': json.dumps(article_list, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})


@csrf_exempt
def statistic(request):
    readers = User.objects.filter(user_type='读者').count()
    writers = User.objects.filter(user_type='作者').count()
    reviews = User.objects.filter(user_type='审稿人').count()
    articles = Article.objects.count()

    return JsonResponse({
        'readers': readers + writers,
        'writers': writers,
        'reviews': reviews,
        'articles': articles
    })
