from django import forms


class WriterForm(forms.Form):
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    user_desc = forms.CharField(label='自我介绍', max_length=500, widget=forms.TextInput(attrs={'class': 'form-control'}))
    real_name = forms.CharField(label='真实姓名', max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    education_exp = forms.CharField(label='教育经历', max_length=500, widget=forms.TextInput(attrs={'class': 'form-control'}))
    job_unit = forms.CharField(label='工作单位', max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
