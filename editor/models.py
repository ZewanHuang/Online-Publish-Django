from django.db import models

# Create your models here.
from user.models import User


class Editor(models.Model):
    editor = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tb_editors'
        verbose_name = '编辑'
        verbose_name_plural = verbose_name