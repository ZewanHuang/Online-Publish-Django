
from django.http import JsonResponse

# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from audit.form import WriterForm
from audit.models import Writer
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

        return JsonResponse({'status_code': SUCCESS})
