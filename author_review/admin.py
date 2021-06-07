from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Writer)
admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Reviewer)
admin.site.register(ArticleWriter)
admin.site.register(ArticleReview)