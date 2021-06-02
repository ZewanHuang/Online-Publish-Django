from django.http import JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from audit.form import *
from audit.models import *
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
            else:
                user.user_type = '作者'
                user.save()
        else:
            return JsonResponse({'status_code': WriterStatus.EMAIL_NOT_CONFIRMED})
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
            reviewer_name = review_form.cleaned_data.get('reviewer_name')
            article_id = review_form.cleaned_data.get('article_id')
            new_review = review_form.cleaned_data.get('review')

            try:
                reviewer = Reviewer.objects.get(reviewer__username=reviewer_name)
                article = Article.objects.get(article_id=article_id)
                try:
                    same_review = ArticleReview.objects.get(reviewer=reviewer, article=article)
                    if same_review.status == 0:
                        same_review.review = new_review
                        same_review.status = 1
                        same_review.save()
                    else:
                        return JsonResponse({'status_code': ReviewStatus.REVIEW_EXIST})
                except:
                    return JsonResponse({'status_code': ReviewStatus.REVIEW_NOT_MATCH})
            except:
                return JsonResponse({'status_code': ReviewStatus.AR_NOT_EXIST})
        else:
            return JsonResponse({'status_code': FORM_ERROR})

        return JsonResponse({'status_code': SUCCESS})
