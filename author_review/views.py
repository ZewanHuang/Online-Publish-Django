from django.db.models import Q, F
from django.http import JsonResponse
import json

# Create your views here.
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from message.models import Message
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
                writer.save()

                # message
                message = Message()
                message.message_type = '未读'
                message.title = '作者申请'
                message.user = user
                message.content = '欢迎注册本平台的作者，期待您的投稿！'
                message.save()

                # message to editor
                editor = User.objects.get(username='editor01')
                message_to_editor = Message()
                message_to_editor.message_type = '未读'
                message_to_editor.title = '作者申请'
                message_to_editor.user = editor
                message_to_editor.content = '真实姓名为' + user.real_name + '的用户' + user.username + '已成功申请成为作者，您可以在工作空间查看！'
                message_to_editor.save()

        else:
            return JsonResponse({'status_code': WriterStatus.MESSAGE_NOT_EXIST})

    else:
        return JsonResponse({'status_code': WriterStatus.EMAIL_NOT_CONFIRMED})
    return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def upload_article_info(request):
    if request.method == 'POST':

        article_form = ArticleForm(request.POST)

        if article_form.is_valid():
            title = article_form.cleaned_data.get('title')
            abstract = article_form.cleaned_data.get('abstract')
            key = article_form.cleaned_data.get('key')
            content = article_form.cleaned_data.get('content')
            str_category = article_form.cleaned_data.get('category')
            # article_address = article_form.cleaned_data.get('article_address')
            str_writer = article_form.cleaned_data.get('writers')

            if request.session.get('is_login'):
                new_article = Article()
                new_article.title = title
                new_article.abstract = abstract
                new_article.key = key
                new_article.content = content

                same_category = Category.objects.get(category=str_category)
                new_article.category = same_category
                new_article.save()

                try:
                    writers = str_writer.split(',')
                    for writer in writers:
                        same_writer = Writer.objects.get(writer__real_name=writer)
                        new_article.writers.add(same_writer)
                    new_article.save()

                except:
                    new_article.delete()
                    return JsonResponse({'status_code': '4002'})

            else:
                return JsonResponse({'status_code': LogoutStatus.USER_NOT_LOGIN})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

        return JsonResponse({'status_code': SUCCESS, 'articleID': new_article.article_id})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def edit_article(request):
    if request.method == 'POST':

        aid = request.POST.get('aid')
        article_form = ArticleForm(request.POST)

        if article_form.is_valid():
            title = article_form.cleaned_data.get('title')
            abstract = article_form.cleaned_data.get('abstract')
            key = article_form.cleaned_data.get('key')
            content = article_form.cleaned_data.get('content')
            str_category = article_form.cleaned_data.get('category')
            str_writer = article_form.cleaned_data.get('writers')

            if request.session.get('is_login'):
                new_article = Article.objects.get(article_id=aid)
                new_article.title = title
                new_article.abstract = abstract
                new_article.key = key
                new_article.content = content

                same_category = Category.objects.get(category=str_category)
                new_article.category = same_category

                writers = str_writer.split(',')
                print(writers)
                for writer in writers:
                    try:
                        same_writer = Writer.objects.get(writer__real_name=writer)
                        new_article.writers.add(same_writer)
                    except:
                        return JsonResponse({'status_code': '4002'})

                    act = ActActivity()
                    act.status = 0
                    act.article = new_article
                    act.user = same_writer.writer
                    act.save()

                new_article.save()

            else:
                return JsonResponse({'status_code': LogoutStatus.USER_NOT_LOGIN})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

        return JsonResponse({'status_code': SUCCESS, 'articleID': new_article.article_id})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def upload_article(request):

    this_article_id = request.POST.get('articleID')
    upload_article_form = UploadArticleForm(request.POST, request.FILES)
    if upload_article_form.is_valid():
        try:
            this_article = Article.objects.get(article_id=this_article_id)
            this_article.article_address.delete()
            this_article.article_address = request.FILES.getlist('file')[-1]
            this_article.save()

            return JsonResponse({'status_code': '2000'})

        except:
            return JsonResponse({'status_code': '4001'})
    else:
        return JsonResponse({'status_code': '4002'})


@csrf_exempt
def confirm_article(request):
    if request.method == 'POST':
        this_article_id = request.POST.get('articleID')
        try:
            this_article = Article.objects.get(article_id=this_article_id)
        except:
            return JsonResponse({'status_code': '4001'})

        if this_article.article_address:

            # send message
            users = User.objects.filter(writer__article__article_id=this_article_id)
            for user in users:
                message = Message()
                message.message_type = '未读'
                message.title = '上传文章'
                message.content = '感谢投稿本平台，您的文章《' + this_article.title + '》已上传成功，请耐心等待审核！'
                message.user = user
                message.save()

                # message to editor
                editor = User.objects.get(username='editor01')
                message_to_editor = Message()
                message_to_editor.message_type = '未读'
                message_to_editor.title = '文章上传'
                message_to_editor.user = editor
                message_to_editor.content = '用户已投稿上传文章《' + this_article.title + '》，请及时安排审稿人进行审核！'
                message_to_editor.save()

                # activity
                act = ActActivity()
                act.article = this_article
                act.status = 2
                act.user = user
                act.save()

            return JsonResponse({'status_code': SUCCESS})
        return JsonResponse({'status_code': '4002'})
    return JsonResponse({'status_code': '4003'})


@csrf_exempt
def write_remark(request):
    if request.method == 'POST':

        rid = request.POST.get('rid')

        remark = ArticleRemark.objects.get(id=rid)
        reviewer_name = remark.review.review.username
        article_id = remark.article.article_id
        new_remark = request.POST.get('content')

        try:
            review = Review.objects.get(review__username=reviewer_name)
            article = Article.objects.get(article_id=article_id)

            self_username = request.session.get('username')

            if self_username == review.review.username:
                same_remark = ArticleRemark.objects.get(review=review, article=article)
                # if same_remark.status == 0:
                same_remark.remark = new_remark
                same_remark.status = 1
                same_remark.save()

                # message to editor
                editor = User.objects.get(username='editor01')
                message_to_editor = Message()
                message_to_editor.message_type = '未读'
                message_to_editor.title = '评论上传'
                message_to_editor.user = editor
                message_to_editor.content = '审稿人' + review.review.real_name + '已提交了《' + article.title + '》的评论，请及时查看与处理！'
                message_to_editor.save()

                articleRemarks = ArticleRemark.objects.filter(article=article)
                ableToSave = True
                for ar in articleRemarks:
                    if ar.status == 0:
                        ableToSave = False
                if ableToSave:
                    article.status = 2
                    article.save()

                    # message to editor
                    editor = User.objects.get(username='editor01')
                    message_to_editor = Message()
                    message_to_editor.message_type = '未读'
                    message_to_editor.title = '审稿完成'
                    message_to_editor.user = editor
                    message_to_editor.content = '文章《' + article.title + '》的评论已全部提交完毕，请及时查看与发布！'
                    message_to_editor.save()

                # activity
                act = ActActivity()
                act.status = 4
                act.article = article
                act.user = review.review
                act.save()

            else:
                return JsonResponse({'status_code': RemarkStatus.REVIEW_NOT_MATCH})
        except:
            return JsonResponse({'status_code': RemarkStatus.AR_NOT_EXIST})

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
                    info['avatar'] = WEB_ROOT + '/media/avatar/user_default/' + '2.png'
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
def self_remarks_undo(request):
    try:
        username = request.session.get('username')
    except:
        return JsonResponse({'status_code': '4001'})

    remarks = ArticleRemark.objects.filter(status=0, review__review__username=username)
    remark_list = []
    for remark in remarks:
        article = remark.article
        writers_name = []
        for writer in article.writers.all():
            writers_name.append(writer.writer.real_name)

        info = {
            'writer': ','.join(writers_name),
            'review': remark.review.review.real_name,
            'content': remark.remark,
            'aid': article.article_id,
            'title': article.title,
            'status': remark.status,
            'rid': remark.id,
            'key': article.key,
            'time': remark.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'abstract': article.abstract,
        }
        remark_list.append(info)

    if remark_list:
        return JsonResponse({'status_code': SUCCESS, 'remarks': json.dumps(remark_list, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': '4002'})

@csrf_exempt
def self_remarks_done(request):
    try:
        username = request.session.get('username')
    except:
        return JsonResponse({'status_code': '4001'})

    remarks = ArticleRemark.objects.filter(status=1, review__review__username=username)
    remark_list = []
    for remark in remarks:
        article = remark.article
        writers_name = []
        for writer in article.writers.all():
            writers_name.append(writer.writer.real_name)

        info = {
            'writer': ','.join(writers_name),
            'review': remark.review.review.real_name,
            'content': remark.remark,
            'aid': article.article_id,
            'title': article.title,
            'status': remark.status,
            'rid': remark.id,
            'key': article.key,
            'time': remark.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            'abstract': article.abstract,
        }
        remark_list.append(info)

    return JsonResponse({'status_code': SUCCESS, 'remarks': json.dumps(remark_list, ensure_ascii=False)})


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
                if article.article_address:
                    json_item = {"article_id": article.article_id,
                                 "title": article.title,
                                 "abstract": article.abstract,
                                 "key": article.key,
                                 "content": article.content,
                                 "category": article.category.category,
                                 "writer": article.writers.all()[0].writer.username,
                                 "read_num": article.read_num,
                                 "download_num": article.download_num,
                                 "article_address": article.article_address.url}

                    json_list.append(json_item)

            return JsonResponse({'status_code': SUCCESS, 'articles': json.dumps(json_list)})
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
        aid = request.POST.get('aid')

        search_remark_list = ArticleRemark.objects.filter(Q(article__writers__writer=writer.writer) & Q(status=1))
        print(search_remark_list[0].article.article_id)
        json_list = []
        if aid:
            for search_remark in search_remark_list:
                if int(aid) == int(search_remark.article.article_id):
                    if search_remark.review.review.avatar:
                        avatar = WEB_ROOT + search_remark.review.review.avatar.url
                    else:
                        avatar = WEB_ROOT + '/media/avatar/user_default/' + '2.png'

                    json_item = {"article_id": search_remark.article.article_id,
                                 "title": search_remark.article.title,
                                 "content": search_remark.remark,
                                 "review": search_remark.review.review.username,
                                 'reviewer': search_remark.review.review.real_name,
                                 'avatar': avatar,
                                 'email': search_remark.review.review.email,
                                 "time": search_remark.create_time.strftime("%Y-%m-%d %H:%M:%S")
                                 }
                    json_list.append(json_item)
        elif key:
            for search_remark in list(search_remark_list):
                if key in search_remark.article.key:
                    json_item = {"article_id": search_remark.article.article_id,
                                 "title": search_remark.article.title,
                                 "content": search_remark.remark,
                                 "review": search_remark.review.username,
                                 'reviewer': search_remark.review.real_name,
                                 "time": search_remark.create_time}
                    json_list.append(json_item)
        elif category:
            for search_remark in list(search_remark_list):
                if category == search_remark.article.category.category:
                    json_item = {"article_id": search_remark.article.article_id,
                                 "title": search_remark.article.title,
                                 "content": search_remark.remark,
                                 "review": search_remark.review.username,
                                 'reviewer': search_remark.review.real_name,
                                 "time": search_remark.create_time}
                    json_list.append(json_item)
        elif title:
            for search_remark in list(search_remark_list):
                if title in search_remark.article.title:
                    json_item = {"article_id": search_remark.article.article_id,
                                 "title": search_remark.article.title,
                                 "content": search_remark.remark,
                                 "review": search_remark.review.username,
                                 'reviewer': search_remark.review.real_name,
                                 "time": search_remark.create_time}
                    json_list.append(json_item)
        else:
            for search_remark in list(search_remark_list):
                json_item = {"article_id": search_remark.article.article_id,
                             "title": search_remark.article.title,
                             "content": search_remark.remark,
                             "review": search_remark.review.username,
                             'reviewer': search_remark.review.real_name,
                             "time": search_remark.create_time}
                json_list.append(json_item)

        if json_list:
            return JsonResponse({'status_code': SUCCESS, 'data': json.dumps(json_list, ensure_ascii=False)})
        else:
            return JsonResponse({'status_code': '4001'})
    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def search_article_remark(request):
    if request.method == 'POST':
        rid = request.POST.get('rid')
        remark = get_object_or_404(ArticleRemark, id=int(rid))
        article_id = remark.article.article_id

        remarks = ArticleRemark.objects.filter(article__article_id__exact=article_id, status=1)

        if remarks:
            json_list = []
            for this_remark in remarks:
                if this_remark.review.review.avatar:
                    avatar = WEB_ROOT + this_remark.review.review.avatar.url
                else:
                    avatar = WEB_ROOT + '/media/avatar/user_default/' + '2.png'

                json_item = {"content": this_remark.remark,
                             "review": this_remark.review.review.username,
                             'reviewer': this_remark.review.review.real_name,
                             'email': this_remark.review.review.email,
                             'avatar': avatar,
                             "time": this_remark.create_time.strftime("%Y-%m-%d")}

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


@csrf_exempt
def add_read_times(request):
    if request.method == 'POST':
        aid = request.POST.get('aid')
        try:
            article = Article.objects.get(article_id=int(aid))
            article.read_num += 1
            article.save()
        except:
            return JsonResponse({'status_code': '4001'})

        return JsonResponse({'status_code': '2000'})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def add_download_times(request):
    if request.method == 'POST':
        aid = request.POST.get('aid')
        try:
            article = Article.objects.get(article_id=int(aid))
            article.download_num += 1
            article.save()
        except:
            return JsonResponse({'status_code': '4001'})

        return JsonResponse({'status_code': '2000'})

    return JsonResponse({'status_code': DEFAULT})


@csrf_exempt
def self_popular(request):
    try:
        username = request.session.get('username')
    except:
        return JsonResponse({'status_code': '4001'})

    articles = Article.objects.filter(status=4, writers__writer__username=username).order_by((F('read_num') + F('download_num')).desc())
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

            if (++idx) >= 4:
                break

    if article_list:
        return JsonResponse({'status_code': SUCCESS, 'articles': json.dumps(article_list, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})


@csrf_exempt
def self_latest(request):
    try:
        username = request.session.get('username')
    except:
        return JsonResponse({'status_code': '4001'})

    article_remarks = ArticleRemark.objects.filter(status=1, review__review__username=username).order_by((F('create_time')).desc())
    idx = 0
    article_list = []
    for article_remark in article_remarks:
        article = article_remark.article
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

            if (++idx) >= 4:
                break

    if article_list:
        return JsonResponse({'status_code': SUCCESS, 'articles': json.dumps(article_list, ensure_ascii=False)})
    else:
        return JsonResponse({'status_code': ArticleStatus.ARTICLE_NOT_EXIST})


@csrf_exempt
def get_activity(request):
    self_username = request.session.get('username')
    self_user = User.objects.get(username=self_username)
    all_acts = ActActivity.objects.filter(user=self_user)

    if all_acts:
        act_list = []
        for act in all_acts:
            act_item = {
                'status': int(act.status),
                'title': act.article.title,
                'aid': act.article.article_id,
                'date': act.time.strftime('%Y/%m/%d')
            }
            act_list.append(act_item)
        print(act_list)
        return JsonResponse({'status_code': SUCCESS, 'acts': json.dumps(act_list, ensure_ascii=False)})

    return JsonResponse({'status_code': '4001'})