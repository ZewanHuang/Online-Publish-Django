from django import forms

from user.models import User


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=128)
    password = forms.CharField(label='密码', max_length=256, widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))


class DetailInfoForm(forms.Form):
    real_name = forms.CharField(label="真实姓名", max_length=20)
    education = forms.CharField(label="教育经历", max_length=200)
    job = forms.CharField(label="职业经历", max_length=200)
    description = forms.CharField(label="个人简介", max_length=200)


class UploadForm(forms.Form):
    class Meta:
        model = User
        fields = 'avatar'
