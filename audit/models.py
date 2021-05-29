from django.db import models

# Create your models here.
from user.models import User


class Writer(models.Model):
    writer = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tb_writers'
        verbose_name = '作者'
        verbose_name_plural = verbose_name
