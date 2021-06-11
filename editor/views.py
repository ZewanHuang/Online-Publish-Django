import json
import random
import re
from django.db.models import Q, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from author_review.models import *
from django3.settings import WEB_ROOT
from editor.form import *
from editor.models import *
from user.models import User
from utils.hash import hash_code
from utils.response_code import *
from utils.send import make_confirm_string, send_email_confirm


@csrf_exempt
def register_editor(request):
    is_login = request.session.get('is_login')

    if is_login:
        username = request.session.get('username')
    else:
        return JsonResponse({'status_code': EditorStatus.USER_NOT_LOGIN})

    try:
        user = User.objects.get(username=username)
    except:
        return JsonResponse({'status_code': EditorStatus.USER_NOT_EXIST})

    if user.has_confirmed:
        if user.real_name:
            if user.user_type == '编辑':
                return JsonResponse({'status_code': EditorStatus.Editor_EXIST})
            else:
                user.user_type = '编辑'
                user.save()
                editor = Editor()
                editor.editor = user
                editor.save()
        else:
            return JsonResponse({'status_code': EditorStatus.MESSAGE_NOT_EXIST})

    else:
        return JsonResponse({'status_code': EditorStatus.EMAIL_NOT_CONFIRMED})
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def add_review(request):
    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            username = review_form.cleaned_data.get('username')
            password = review_form.cleaned_data.get('password')
            email = review_form.cleaned_data.get('email')
            real_name = review_form.cleaned_data.get('real_name')

            same_name_review = Review.objects.filter(review__username=username)
            if same_name_review:
                return JsonResponse({'status_code': RegisterStatus.USERNAME_REPEATED})

            same_email_user = User.objects.filter(email=email)
            if same_email_user:
                return JsonResponse({'status_code': RegisterStatus.EMAIL_ERROR})

            # 检测密码不符合规范：8-18，英文字母+数字
            if not re.match('^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,18}$', password):
                return JsonResponse({'status_code': RegisterStatus.PASSWORD_INVALID})

            # 成功
            new_user = User()
            new_user.username = username
            new_user.password = hash_code(password)
            new_user.email = email
            new_user.real_name = real_name
            new_user.user_type = '审稿人'
            new_user.save()

            new_review = Review()
            new_review.review = new_user
            new_review.save()

            code = make_confirm_string(new_user)
            try:
                send_email_confirm(email, code)
            except:
                new_user.delete()
                return JsonResponse({'status_code': RegisterStatus.SEND_EMAIL_ERROR})

            return JsonResponse({'status_code': SUCCESS})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def editor_info(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if request.session.get('is_login') and username == request.session.get('username'):
            that_user = get_object_or_404(User, username=username)
            if that_user.user_type == '编辑':
                info = {
                    'username': that_user.username,
                    'real_name': that_user.real_name,
                }
                if that_user.avatar:
                    info['avatar'] = WEB_ROOT + that_user.avatar.url
                else:
                    info['avatar'] = WEB_ROOT + '/media/avatar/user_default/' + '2.png'
                return JsonResponse({'status_code': SUCCESS, 'user': json.dumps(info, ensure_ascii=False)})

            else:
                return JsonResponse({'status_code': WritingPageStatus.USER_NOT_EDITOR})

        else:
            return JsonResponse({'status_code': WritingPageStatus.USER_NOT_LOGIN})


@csrf_exempt
def allot_review(request):
    if request.method == 'POST':
        article_id = request.POST.get('aid')
        reviews_name = request.POST.get('reviews')

        try:
            article = Article.objects.get(article_id=article_id)
            # 指定审稿人姓名
            if reviews_name and reviews_name != '':
                try:
                    reviews = reviews_name.split(',')
                    for review_name in reviews:
                        review = Review.objects.get(review__real_name=review_name)
                        article_review = ArticleRemark()
                        article_review.article = article
                        article_review.review = review
                        article_review.save()

                    article.status = 1
                    article.save()

                    return JsonResponse({'status_code': SUCCESS})
                except:
                    return JsonResponse({'status_code': WriterStatus.USER_NOT_EXIST})

            # 未指定审稿人-随机分配
            else:
                review_obj = Review.objects.last()
                rand_id = random.sample(range(review_obj.id), 1)
                review = Review.objects.get(review_id=rand_id)
                try:
                    article_review = ArticleRemark()
                    article_review.article = article
                    article_review.review = review
                    article_review.save()
                    return JsonResponse({'status_code': '2001'})
                except:
                    return JsonResponse({'status_code': EditorStatus.ADD_REVIEW_ERROR})

        except:
            return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})
    return JsonResponse({'status_code': '3000'})


@csrf_exempt
def update_status(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        str_status = request.POST.get('status')
        try:
            article = Article.objects.get(article_id=article_id)
            if "审核通过" == str_status:
                article.status = 1
            elif "审核不通过" == str_status:
                article.status = 2
            elif "已发布" == str_status:
                article.status = 4
                new_message = ArticleNews()
                new_message.article = article
                new_message.user = User.objects.get(username=request.session.get('username'))
                new_message.status = 3
                new_message.save()
            article.save()
            return JsonResponse({'status_code': SUCCESS})
        except:
            return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def delete_article(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        try:
            article = Article.objects.get(article_id=article_id)
            article.delete()
            new_message = ArticleNews()
            new_message.article = article
            new_message.user = User.objects.get(username=request.session.get('username'))
            new_message.status = 5
            new_message.save()
            return JsonResponse({'status_code': SUCCESS})
        except:
            return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def count_person(request):
    readers = User.objects.filter(user_type='读者').count()
    writers = User.objects.filter(user_type='作者').count()
    reviews = User.objects.filter(user_type='审稿人').count()

    info = {
        'reader': readers,
        'writer': writers,
        'review': reviews,
    }
    return JsonResponse({'status_code': SUCCESS, 'user': json.dumps(info, ensure_ascii=False)})


@csrf_exempt
def count_article(request):
    article_count = [0 for x in range(0, 5)]

    articles = Article.objects.all()
    for article in articles:
        if bool(article.article_address):
            article_count[article.status] += 1

    # 0 审核中 1 已分配 2 待处理 3 审核不通过 4 已发布
    info = {
        'testing': article_count[0],
        'contribute': article_count[1],
        'toDeal': article_count[2],
        'fail': article_count[3],
        'done': article_count[4],
    }
    return JsonResponse({'status_code': SUCCESS, 'article': json.dumps(info, ensure_ascii=False)})


@csrf_exempt
def get_articles_0(request):
    articles = Article.objects.filter(status=0).order_by((F('create_time').desc()))
    article_list = []
    for article in articles:
        if article.article_address:
            writers_name = []
            for writer in article.writers.all():
                writers_name.append(writer.writer.real_name)

            article_list.append({
                'realName': ','.join(writers_name),
                'type': article.category.category,
                'title': article.title,
                'key': article.key,
                'abstract': article.abstract,
                'aid': article.article_id,
                'time': article.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

    return JsonResponse({'status_code': SUCCESS, 'info': json.dumps(article_list, ensure_ascii=False)})


@csrf_exempt
def get_articles_1(request):
    articles = Article.objects.filter(status=1).order_by((F('create_time').desc()))
    article_list = []
    for article in articles:
        if article.article_address:
            writers_name = []
            for writer in article.writers.all():
                writers_name.append(writer.writer.real_name)

            article_list.append({
                'realName': ','.join(writers_name),
                'type': article.category.category,
                'title': article.title,
                'key': article.key,
                'abstract': article.abstract,
                'aid': article.article_id,
                'time': article.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

    return JsonResponse({'status_code': SUCCESS, 'info': json.dumps(article_list, ensure_ascii=False)})


@csrf_exempt
def get_articles_2(request):
    articles = Article.objects.filter(status=2).order_by((F('create_time').desc()))
    article_list = []
    for article in articles:
        if article.article_address:
            writers_name = []
            for writer in article.writers.all():
                writers_name.append(writer.writer.real_name)

            article_list.append({
                'realName': ','.join(writers_name),
                'type': article.category.category,
                'title': article.title,
                'key': article.key,
                'abstract': article.abstract,
                'aid': article.article_id,
                'time': article.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

    return JsonResponse({'status_code': SUCCESS, 'info': json.dumps(article_list, ensure_ascii=False)})


@csrf_exempt
def get_articles_4(request):
    articles = Article.objects.filter(status=4).order_by((F('create_time').desc()))
    article_list = []
    for article in articles:
        if article.article_address:
            writers_name = []
            for writer in article.writers.all():
                writers_name.append(writer.writer.real_name)

            article_list.append({
                'realName': ','.join(writers_name),
                'type': article.category.category,
                'title': article.title,
                'key': article.key,
                'abstract': article.abstract,
                'aid': article.article_id,
                'time': article.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

    return JsonResponse({'status_code': SUCCESS, 'info': json.dumps(article_list, ensure_ascii=False)})


@csrf_exempt
def count_remark(request):
    remark_count = ArticleRemark.objects.count()
    return JsonResponse({'status_code': SUCCESS, 'remarkCount': remark_count})


@csrf_exempt
def count(request):
    readers = User.objects.filter(user_type='读者').count()
    writers = User.objects.filter(user_type='作者').count()
    reviews = User.objects.filter(user_type='审稿人').count()

    user = {
        'reader': readers,
        'writer': writers,
        'review': reviews,
    }

    article_count = [0 for x in range(0, 5)]
    article_all = 0

    articles = Article.objects.all()
    for article in articles:
        if bool(article.article_address):
            article_count[article.status] += 1
            article_all += 1

    # 0 审核中 1 已分配 2 待处理 3 审核不通过 4 已发布
    article = {
        'testing': article_count[0],
        'contribute': article_count[1],
        'toDeal': article_count[2],
        'fail': article_count[3],
        'done': article_count[4],
    }

    remark_count = ArticleRemark.objects.count()

    return JsonResponse({
        'status_code': SUCCESS,
        'user': json.dumps(user, ensure_ascii=False),
        'article': json.dumps(article, ensure_ascii=False),
        'remarkCount': remark_count,
        'articleCount': article_all,
    })


@csrf_exempt
def get_readers(request):
    users = User.objects.filter(user_type='读者').order_by((F('c_time')).desc())
    user_list = []
    for user in users:
        info = {
            'username': user.username,
            'email': user.email,
            'time': str(user.c_time)
        }
        user_list.append(info)

    return JsonResponse({'status_code': SUCCESS, 'readers': json.dumps(user_list, ensure_ascii=False)})


@csrf_exempt
def get_authors(request):
    users = User.objects.filter(user_type='作者').order_by((F('c_time')).desc())
    user_list = []
    for user in users:
        if bool(user.has_confirmed):
            info = {
                'username': user.username,
                'email': user.email,
                'realName': user.real_name,
                'education': user.education_exp,
                'job': user.job_unit,
            }
            user_list.append(info)

    return JsonResponse({'status_code': SUCCESS, 'authors': json.dumps(user_list, ensure_ascii=False)})


@csrf_exempt
def get_reviews(request):
    users = User.objects.filter(user_type='审稿人').order_by((F('c_time')).desc())
    user_list = []
    for user in users:
        if bool(user.has_confirmed):
            info = {
                'username': user.username,
                'email': user.email,
                'realName': user.real_name,
            }
            user_list.append(info)

    return JsonResponse({'status_code': SUCCESS, 'reviews': json.dumps(user_list, ensure_ascii=False)})


@csrf_exempt
def get_reviews_name(request):
    users = User.objects.filter(user_type='审稿人').order_by((F('c_time')).desc())
    user_list = []
    for user in users:
        if bool(user.has_confirmed):
            user_list.append({'name': user.real_name})

    return JsonResponse({'status_code': SUCCESS, 'reviews': json.dumps(user_list, ensure_ascii=False)})


@csrf_exempt
def get_remarks_all(request):
    remarks = ArticleRemark.objects.all()
    remark_list = []
    for remark in remarks:
        article = remark.article
        writers_name = []
        for writer in article.writers.all():
            writers_name.append(writer.writer.real_name)

        info = {
            'author': ','.join(writers_name),
            'review': remark.review.review.real_name,
            'content': remark.remark,
            'aid': article.article_id,
            'status': remark.status,
            'rid': remark.id,
            'time': remark.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        remark_list.append(info)

    return JsonResponse({'status_code': SUCCESS, 'remarks': json.dumps(remark_list, ensure_ascii=False)})


@csrf_exempt
def get_remarks_undo(request):
    remarks = ArticleRemark.objects.filter(status=0)
    remark_list = []
    for remark in remarks:
        article = remark.article
        writers_name = []
        for writer in article.writers.all():
            writers_name.append(writer.writer.real_name)

        info = {
            'author': ','.join(writers_name),
            'review': remark.review.review.real_name,
            'content': remark.remark,
            'aid': article.article_id,
            'status': remark.status,
            'rid': remark.id,
            'time': remark.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        remark_list.append(info)

    return JsonResponse({'status_code': SUCCESS, 'remarks': json.dumps(remark_list, ensure_ascii=False)})


@csrf_exempt
def get_remarks_done(request):
    remarks = ArticleRemark.objects.filter(status=1)
    remark_list = []
    for remark in remarks:
        article = remark.article
        writers_name = []
        for writer in article.writers.all():
            writers_name.append(writer.writer.real_name)

        info = {
            'author': ','.join(writers_name),
            'review': remark.review.review.real_name,
            'content': remark.remark,
            'aid': article.article_id,
            'status': remark.status,
            'rid': remark.id,
            'time': remark.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        remark_list.append(info)

    return JsonResponse({'status_code': SUCCESS, 'remarks': json.dumps(remark_list, ensure_ascii=False)})
