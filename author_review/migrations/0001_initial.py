# Generated by Django 3.2 on 2021-06-09 16:51

import author_review.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('article_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=80)),
                ('abstract', models.TextField()),
                ('key', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('status', models.SmallIntegerField(choices=[(0, '审核中'), (1, '审核通过'), (2, '审核不通过'), (3, '未发布'), (4, '已发布')], default=0)),
                ('read_num', models.IntegerField(default=0)),
                ('download_num', models.IntegerField(default=0)),
                ('article_address', models.FileField(upload_to=author_review.models.file_directory_path)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(blank=True, null=True)),
                ('review_time', models.DateTimeField(blank=True, null=True)),
                ('release_time', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': '文章',
                'verbose_name_plural': '文章',
                'db_table': 'tb_articles',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': '文章类别',
                'verbose_name_plural': '文章类别',
                'db_table': 'tb_categories',
            },
        ),
        migrations.CreateModel(
            name='Writer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('writer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'verbose_name': '作者',
                'verbose_name_plural': '作者',
                'db_table': 'tb_writers',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='user.user')),
            ],
            options={
                'verbose_name': '审稿人',
                'verbose_name_plural': '审稿人',
                'db_table': 'tb_reviews',
            },
        ),
        migrations.CreateModel(
            name='ArticleRemark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.SmallIntegerField(choices=[(0, '未提交评论'), (1, '已提交评论')], default=0)),
                ('remark', models.TextField(blank=True, null=True)),
                ('create_time', models.DateField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='author_review.article')),
                ('review', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='author_review.review')),
            ],
            options={
                'verbose_name': '文章-审稿人关系表',
                'verbose_name_plural': '文章-审稿人关系表',
                'db_table': 'article-review-relation',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='author_review.category'),
        ),
        migrations.AddField(
            model_name='article',
            name='remarks',
            field=models.ManyToManyField(through='author_review.ArticleRemark', to='author_review.Review'),
        ),
        migrations.AddField(
            model_name='article',
            name='writers',
            field=models.ManyToManyField(to='author_review.Writer'),
        ),
    ]