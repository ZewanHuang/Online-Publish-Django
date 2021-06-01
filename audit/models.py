from django.core.validators import validate_comma_separated_integer_list
from django.db import models

# Create your models here.
from user.models import User


def file_directory_path(instance, filename):
    # 文件上传到 MEDIA_ROOT/avatar/user_<id>/<filename>目录中
    return 'file/{0}'.format(filename)


class Writer(models.Model):
    writer = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tb_writers'
        verbose_name = '作者'
        verbose_name_plural = verbose_name


class Reviewer(models.Model):
    reviewer = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tb_reviewers'
        verbose_name = '审稿人'
        verbose_name_plural = verbose_name


class Category(models.Model):
    category = models.CharField(max_length=20)

    class Meta:
        db_table = 'tb_categories'
        verbose_name = '文章类别'
        verbose_name_plural = verbose_name


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=80)
    abstract = models.TextField()
    key = models.CharField(validators=[validate_comma_separated_integer_list], max_length=100)
    content = models.TextField()
    status = models.SmallIntegerField(choices=((0, "审核中"), (1, "审核通过"), (2, "审核不通过")), default=0)
    category = models.ForeignKey(to="Category", on_delete=models.CASCADE)
    article_address = models.FileField(upload_to=file_directory_path)
    writers = models.ManyToManyField(Writer, through='ArticleWriter')
    reviews = models.ManyToManyField(Reviewer, through='ArticleReview')

    class Meta:
        db_table = 'tb_articles'
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.article_id


class ArticleWriter(models.Model):
    writer = models.ForeignKey(Writer, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        db_table = 'article-writer-relation'
        verbose_name = '文章-作者关系表'
        verbose_name_plural = verbose_name


class ArticleReview(models.Model):
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=((0, "未提交评论"), (1, "已提交评论")), default=0)
    review = models.TextField(null=True, blank=True)
    create_time = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'article-reviewer-relation'
        verbose_name = '文章-审稿人关系表'
        verbose_name_plural = verbose_name
