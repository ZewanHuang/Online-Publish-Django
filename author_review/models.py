from django.core.validators import validate_comma_separated_integer_list
from django.db import models

# Create your models here.
from user.models import User


def file_directory_path(instance, filename):
    # 文件上传到 MEDIA_ROOT/avatar/user_<id>/<filename>目录中
    return 'article/article_{0}/{1}'.format(instance.article_id, filename)


class Writer(models.Model):
    writer = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tb_writers'
        verbose_name = '作者'
        verbose_name_plural = verbose_name


class Review(models.Model):
    review = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'tb_reviews'
        verbose_name = '审稿人'
        verbose_name_plural = verbose_name


class Category(models.Model):
    category_id = models.IntegerField()
    category = models.CharField(max_length=20)
    description = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'tb_categories'
        verbose_name = '文章类别'
        verbose_name_plural = verbose_name


class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=80)
    abstract = models.TextField()
    key = models.CharField(max_length=100)
    content = models.TextField()
    status = models.SmallIntegerField(choices=((0, "审核中"), (1, "已分配"), (2, "待处理")
                                               , (3, "审核不通过"), (4, "已发布")), default=0)
    read_num = models.IntegerField(default=0)
    download_num = models.IntegerField(default=0)
    category = models.ForeignKey(to="Category", on_delete=models.CASCADE)
    article_address = models.FileField(upload_to=file_directory_path, blank=True)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(null=True, blank=True)
    review_time = models.DateTimeField(null=True, blank=True)
    release_time = models.DateTimeField(null=True, blank=True)
    writers = models.ManyToManyField(Writer)
    remarks = models.ManyToManyField(Review, through='ArticleRemark')

    class Meta:
        db_table = 'tb_articles'
        verbose_name = '文章'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.article_id)


class ArticleRemark(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=((0, "未提交评论"), (1, "已提交评论")), default=0)
    remark = models.TextField(null=True, blank=True)
    create_time = models.DateField(auto_now_add=True)  # 创建审稿人和文章关系的时间

    class Meta:
        db_table = 'article-review-relation'
        verbose_name = '文章-审稿人关系表'
        verbose_name_plural = verbose_name


class ArticleNews(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    select_status = (
        (0, '修改了文章'),
        (1, '修改成功了文章'),
        (2, '提交了文章'),
        (3, '成功发布了文章'),
        (4, '审核了文章'),
        (5, '删除了文章'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.SmallIntegerField(choices=select_status, default=2)
    create_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tb_news'
        verbose_name = '文章动态表'
        verbose_name_plural = verbose_name