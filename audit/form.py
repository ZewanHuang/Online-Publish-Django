from django import forms

from audit.models import *


class ArticleForm(forms.Form):
    title = forms.CharField(label="题目", max_length=80, widget=forms.TextInput(attrs={'class': 'form-control'}))
    abstract = forms.CharField(label="摘要", widget=forms.Textarea)
    key = forms.CharField(label="关键词", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(label="主题", widget=forms.Textarea)
    category = forms.CharField(label="类别", widget=forms.TextInput(attrs={'class': 'form-control'}))
    article_address = forms.FileField(label="文章的文件地址")
    writers = forms.CharField(label="作者", widget=forms.TextInput(attrs={'class': 'form-control'}))


class RemarkForm(forms.Form):
    review_name = forms.CharField(label="审稿人用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    article_id = forms.IntegerField(label="作者ID", widget=forms.TextInput(attrs={'class': 'form-control'}))
    remark = forms.CharField(label="评论", widget=forms.Textarea)
