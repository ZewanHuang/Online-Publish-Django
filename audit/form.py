from django import forms

from audit.models import *


class WriterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    user_desc = forms.CharField(label='自我介绍', max_length=500, widget=forms.TextInput(attrs={'class': 'form-control'}))
    real_name = forms.CharField(label='真实姓名', max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    education_exp = forms.CharField(label='教育经历', max_length=500,
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    job_unit = forms.CharField(label='工作单位', max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))


class ArticleForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    title = forms.CharField(label="题目", max_length=80, widget=forms.TextInput(attrs={'class': 'form-control'}))
    abstract = forms.CharField(label="摘要", widget=forms.Textarea)
    key = forms.CharField(label="关键词", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(label="主题", widget=forms.Textarea)
    category = forms.CharField(label="类别", widget=forms.TextInput(attrs={'class': 'form-control'}) )
    article_address = forms.FileField(label="文章的文件地址")
    writers = forms.CharField(label="作者", widget=forms.TextInput(attrs={'class': 'form-control'}) )


class ReviewForm(forms.Form):
    reviewer_id = forms.IntegerField(label="审稿人ID", widget=forms.TextInput(attrs={'class': 'form-control'}))
    article_id = forms.IntegerField(label="作者ID", widget=forms.TextInput(attrs={'class': 'form-control'}))
    review = forms.CharField(label="评论", widget=forms.Textarea)
