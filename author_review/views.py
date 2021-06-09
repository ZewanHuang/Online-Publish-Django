from django.db.models import Q, F
from django.http import JsonResponse
import json

# Create your views here.
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .form import *
from .models import *
from django3.settings import WEB_ROOT
from user.models import User
from utils.response_code import *


@csrf_exempt
def apply_writer(request):
    is_login = request.session.get('is_login')

    if is_login:
        username = request.session.get('username')
    else:
        return JsonResponse({'status_code': WriterStatus.USER_NOT_LOGIN})

    try:
        user = User.objects.get(username=username)
    except:
        return JsonResponse({'status_code': WriterStatus.USER_NOT_EXIST})

    if user.has_confirmed:
        if user.real_name and user.education_exp and user.job_unit:
            if user.user_type == '作者':
                return JsonResponse({'status_code': WriterStatus.WRITER_EXIST})
            else:
                user.user_type = '作者'
                user.save()
                writer = Writer()
                writer.writer = user
        else:
            return JsonResponse({'status_code': WriterStatus.MESSAGE_NOT_EXIST})

    else:
        return JsonResponse({'status_code': WriterStatus.EMAIL_NOT_CONFIRMED})
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def upload(request):
    if request.method == 'POST':

        article_form = ArticleForm(request.POST)

        if article_form.is_valid():
            title = article_form.cleaned_data.get('title')
            abstract = article_form.cleaned_data.get('abstract')
            key = article_form.cleaned_data.get('key')
            content = article_form.cleaned_data.get('content')
            str_category = article_form.cleaned_data.get('category')
            article_address = article_form.cleaned_data.get('article_address')
            str_writer = article_form.cleaned_data.get('writers')

            if request.session.get('is_login'):
                new_article = Article()
                new_article.title = title
                new_article.abstract = abstract
                new_article.key = key
                new_article.content = content
                new_article.article_address = article_address

                same_category = Category.objects.get(category=str_category)
                new_article.category = same_category
                new_article.save()

                writers = str_writer.split(',')
                for writer in writers:
                    same_writer = Writer.objects.get(username=writer)
                    new_article.writers.add(same_writer)

            else:
                return JsonResponse({'status_code': LogoutStatus.USER_NOT_LOGIN})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

        return JsonResponse({'status_code': SUCCESS})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def remark(request):
    if request.method == 'POST':

        remark_form = RemarkForm(request.POST)

        if remark_form.is_valid():
            reviewer_name = remark_form.cleaned_data.get('review_name')
            article_id = remark_form.cleaned_data.get('article_id')
            new_remark = remark_form.cleaned_data.get('author_review')

            try:
                review = Review.objects.get(review__username=reviewer_name)
                article = Article.objects.get(article_id=article_id)
                try:
                    same_remark = ArticleRemark.objects.get(review=review, article=article)
                    if same_remark.status == 0:
                        same_remark.remark = new_remark
                        same_remark.status = 1
                        same_remark.save()
                    else:
                        return JsonResponse({'status_code': RemarkStatus.REMARK_EXIST})
                except:
                    return JsonResponse({'status_code': RemarkStatus.REVIEW_NOT_MATCH})
            except:
                return JsonResponse({'status_code': RemarkStatus.AR_NOT_EXIST})
        else:
            return JsonResponse({'status_code': FORM_ERROR})

        return JsonResponse({'status_code': SUCCESS})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def writing_info(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if request.session.get('is_login') and username == request.session.get('username'):
            that_user = get_object_or_404(User, username=username)
            if that_user.user_type == '作者':
                info = {
                    'username': that_user.username,
                    'real_name': that_user.real_name,
                    # 'education': that_user.education_exp,
                    # 'job': that_user.job_unit
                }
                if that_user.avatar:
                    info['avatar'] = WEB_ROOT + that_user.avatar.url
                else:
                    info['avatar'] = WEB_ROOT + '/media/avatar/user_default/' + '2.png'
                return JsonResponse({'status_code': SUCCESS, 'user': json.dumps(info, ensure_ascii=False)})

            else:
                return JsonResponse({'status_code': WritingPageStatus.USER_NOT_AUTHOR})

        else:
            return JsonResponse({'status_code': WritingPageStatus.USER_NOT_LOGIN})


@csrf_exempt
def review_info(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        if request.session.get('is_login') and username == request.session.get('username'):
            that_user = get_object_or_404(User, username=username)
            if that_user.user_type == '审稿人':
                info = {
                    'username': that_user.username,
                    'real_name': that_user.real_name,
                    # 'education': that_user.education_exp,
                    # 'job': that_user.job_unit
                }
                if that_user.avatar:
                    info['avatar'] = WEB_ROOT + that_user.avatar.url
                else:
                    info['avatar'] = WEB_ROOT + '/media/avatar/user_default/' + '1.png'
                return JsonResponse({'status_code': SUCCESS, 'user': json.dumps(info, ensure_ascii=False)})

            else:
                return JsonResponse({'status_code': WritingPageStatus.USER_NOT_AUTHOR})

        else:
            return JsonResponse({'status_code': WritingPageStatus.USER_NOT_LOGIN})


@csrf_exempt
def popular_article(request):
    if request.method == 'POST':
        username = request.session.get('username')
        articles = Article.objects.filter(writers__writer__username=username) \
            .order_by((F('read_num') + F('download_num')).desc())
        json_list = []
        if articles:
            for article in articles:
                json_item = {"article_id": article.article_id, "title": article.title,
                             "abstract": article.abstract, "key": article.key,
                             "content": article.content, "category": article.category.category,
                             "writer": article.writers.all()[0].writer.username, "read_num": article.read_num,
                             "download_num": article.download_num, "article_address": article.article_address.url}
                json_list.append(json_item)
                if len(json_list) == 4: break
            return JsonResponse({'status_code': SUCCESS, 'data': json.dumps(json_list)})

        return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def search_article(request):
    global articles
    if request.method == 'POST':
        username = request.session.get('username')
        key = request.POST.get('key')
        category = request.POST.get('category')
        title = request.POST.get('title')

        if key:
            articles = Article.objects.filter(Q(writers__writer__username=username) &
                                              (Q(key__contains=key) or Q(title__contains=key)))
        elif category:
            articles = Article.objects.filter(Q(writers__writer__username=username) & Q(category__category=category))
        elif title:
            articles = Article.objects.filter(Q(writers__writer__username=username) & Q(title__contains=title))
        else:
            articles = Article.objects.filter(writers__writer__username=username)

        if articles:
            json_list = []
            for article in articles:
                json_item = {"article_id": article.article_id, "title": article.title,
                             "abstract": article.abstract, "key": article.key,
                             "content": article.content, "category": article.category.category,
                             "writer": article.writers.all()[0].writer.username, "read_num": article.read_num,
                             "download_num": article.download_num, "article_address": article.article_address.url}

                json_list.append(json_item)

            return JsonResponse({'status_code': SUCCESS, 'data': json.dumps(json_list)})
        else:
            return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})
    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def search_remark_list(request):
    if request.method == 'POST':

        username = request.session.get('username')
        writer = Writer.objects.get(writer__username=username)
        key = request.POST.get('key')
        category = request.POST.get('category')
        title = request.POST.get('title')

        search_remark_list = ArticleRemark.objects.filter(Q(article__writers__writer_id=writer.id) & Q(status=1))
        json_list = {}
        if key:
            for search_remark in list(search_remark_list):
                if key in search_remark.article.key:
                    json_item = {"article_id", search_remark.article.article_id,
                                 "title", search_remark.article.title,
                                 "remark", search_remark.remark,
                                 "review", search_remark.review.username,
                                 "update_time", search_remark.create_time}
                    json_list.append(json_item)
        elif category:
            for search_remark in list(search_remark_list):
                if category == search_remark.article.category.category:
                    json_item = {"article_id", search_remark.article.article_id,
                                 "title", search_remark.article.title,
                                 "remark", search_remark.remark,
                                 "review", search_remark.review.username,
                                 "update_time", search_remark.create_time}
                    json_list.append(json_item)
        elif title:
            for search_remark in list(search_remark_list):
                if title in search_remark.article.title:
                    json_item = {"article_id", search_remark.article.article_id,
                                 "title", search_remark.article.title,
                                 "remark", search_remark.remark,
                                 "review", search_remark.review.username,
                                 "update_time", search_remark.create_time}
                    json_list.append(json_item)
        else:
            for search_remark in list(search_remark_list):
                json_item = {"article_id", search_remark.article.article_id,
                             "title", search_remark.article.title,
                             "remark", search_remark.remark,
                             "review", search_remark.review.username,
                             "update_time", search_remark.create_time}
                json_list.append(json_item)

        return JsonResponse({'status_code': SUCCESS, 'data': json.dumps(json_list)})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def search_article_remark(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')

        remarks = ArticleRemark.objects.filter(article__article_id__exact=article_id)

        if remarks:
            json_list = []
            for this_remark in remarks:
                json_item = {"remark": this_remark.remark,
                             "review": this_remark.review.review.username,
                             "update_time": this_remark.create_time.strftime("%Y-%m-%d %H:%M:%S")}
                json_list.append(json_item)
            return JsonResponse({'status_code': SUCCESS, 'data': json.dumps(json_list)})

        return JsonResponse({'status_code': RemarkStatus.AR_NOT_EXIST})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def search_review_remark(request):
    if request.method == 'POST':
        username = request.session.get('username')
        remarks = ArticleRemark.objects.filter(review__review__username=username)
        if remarks:
            json_list = []
            for this_remark in remarks:
                json_item = {"article_id": this_remark.article.article_id,
                             "title": this_remark.article.title,
                             "status": this_remark.status,
                             "remark": this_remark.remark,
                             "update_time": this_remark.create_time.strftime("%Y-%m-%d %H:%M:%S")}
                json_list.append(json_item)
            return JsonResponse({'status_code': SUCCESS, 'data': json.dumps(json_list)})

        return JsonResponse({'status_code': RemarkStatus.AR_NOT_EXIST})

    return JsonResponse({'status_code': DEFAULT})
