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

        writer_form = WriterForm(request.POST)

        if writer_form.is_valid():
            username = writer_form.cleaned_data.get('username')
            password = writer_form.cleaned_data.get('password')
            user_desc = writer_form.cleaned_data.get('user_desc')
            real_name = writer_form.cleaned_data.get('real_name')
            education_exp = writer_form.cleaned_data.get('education_exp')
            job_unit = writer_form.cleaned_data.get('job_unit')

            try:
                user = User.objects.get(username=username, password=hash_code(password))
            except:
                return JsonResponse({'status_code': WriterStatus.USERNAME_MISS})

            # 成功
            new_writer = Writer()
            user.user_type = 'author'
            user.user_desc = user_desc
            user.real_name = real_name
            user.education_exp = education_exp
            user.job_unit = job_unit
            new_writer.writer = user
            try:
                new_writer.save()
            except:
                return JsonResponse({'status_code': WriterStatus.APPLY_FAILURE})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

        return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def upload(request):
    if request.method == 'POST':

        article_form = ArticleForm(request.POST)

        if article_form.is_valid():
            username = article_form.cleaned_data.get('username')
            title = article_form.cleaned_data.get('title')
            abstract = article_form.cleaned_data.get('abstract')
            key = article_form.cleaned_data.get('key')
            content = article_form.cleaned_data.get('content')
            str_category = article_form.cleaned_data.get('category')
            article_address = article_form.cleaned_data.get('article_address')
            str_writer = article_form.cleaned_data.get('writers')

            if request.session.get('is_login') and username == request.session.get('username'):
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
                    w = ArticleWriter(writer=same_writer, article=new_article)

            else:
                return JsonResponse({'status_code': LogoutStatus.USER_NOT_LOGIN})

        else:
            return JsonResponse({'status_code': FORM_ERROR})

        return JsonResponse({'status_code': SUCCESS})


@csrf_exempt
def review(request):
    if request.method == 'POST':

        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            reviewer_id = review_form.cleaned_data.get('reviewer_id')
            article_id = review_form.cleaned_data.get('article_id')
            new_review = review_form.cleaned_data.get('review')

            reviewer = Reviewer.objects.get(id=reviewer_id)
            article = Article.objects.get(article_id=article_id)

            if reviewer and article:
                same_review = ArticleReview.objects.get(reviewer_id=reviewer_id, article_id=article_id)
                if same_review:
                    if same_review.status == 0:
                        same_review.review = new_review
                        same_review.status = 1
                        same_review.save()
                    else:
                        return JsonResponse({'status_code': ReviewStatus.REVIEW_EXIST})
                else:
                    return JsonResponse({'status_code': ReviewStatus.REVIEW_NOT_MATCH})
            else:
                return JsonResponse({'status_code': ReviewStatus.AR_NOT_EXIST})

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
