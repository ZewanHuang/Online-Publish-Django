# Generated by Django 3.2 on 2021-06-13 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author_review', '0003_alter_article_article_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]