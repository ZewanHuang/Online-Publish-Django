from django.http import JsonResponse
import json

# Create your views here.
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from audit.form import *
from audit.models import *
from django3.settings import WEB_ROOT
from user.models import User
from utils.hash import hash_code
from utils.response_code import *


@csrf_exempt
def apply_writer(request):
    if request.method == 'POST':
        username = request.session.get('username')
        user = User.objects.get(username=username)
        if user.has_confirmed:
            if len(user.real_name) == 0 or len(user.education_exp) == 0 or len(user.job_unit) == 0 :
                return JsonResponse({'status_code': WriterStatus.MESSAGE_NOT_EXIST})
            if user.user_type == '作者':
                return JsonResponse({'status_code': WriterStatus.WRITER_EXIST})
            else:
                user.user_type = '作者'
                user.save()
                writer = Writer()
                writer.writer = user
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


@csrf_exempt
def remark(request):
    if request.method == 'POST':

        remark_form = RemarkForm(request.POST)

        if remark_form.is_valid():
            review_name = remark_form.cleaned_data.get('review_name')
            article_id = remark_form.cleaned_data.get('article_id')
            new_remark = remark_form.cleaned_data.get('remark')

            try:
                review = Review.objects.get(review__username=review_name)
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


@csrf_exempt
def writing(request):
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
