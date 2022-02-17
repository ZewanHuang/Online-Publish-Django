import json

from django.db import models


# Create your models here.

def user_avatar_directory_path(instance, filename):
    # 文件上传到 MEDIA_ROOT/avatar/user_<id>/<filename>目录中
    return 'avatar/user_{0}/{1}'.format(instance.id, filename)


class User(models.Model):
    username = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)

    avatar = models.ImageField(upload_to=user_avatar_directory_path, blank=True)
    user_desc = models.CharField(max_length=500, blank=True)
    real_name = models.CharField(max_length=128, blank=True)
    education_exp = models.CharField(max_length=500, blank=True)
    job_unit = models.CharField(max_length=128, blank=True)

    c_time = models.DateTimeField(auto_now_add=True)
    has_confirmed = models.BooleanField(default=False)

    users_type = (
        ('reader', '读者'),
        ('author_review', '作者'),
        ('reviewer', '审稿人'),
        ('edit', '编辑')
    )
    user_type = models.CharField(max_length=32, choices=users_type, default='读者')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def able_apply_author(self):
        return self.user_desc and self.education_exp and self.job_unit

    def __str__(self):
        return self.username


class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User', on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ": " + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = verbose_name


class Collect(models.Model):
    article_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_collect'
        verbose_name = '用户收藏的文章'
        verbose_name_plural = verbose_name
