from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Writer)
admin.site.register(Category)
admin.site.register(Article)
admin.site.register(Review)
admin.site.register(ArticleRemark)
# admin.site.register(ArticleNews)
admin.site.register(ActActivity)
