# Generated by Django 2.2 on 2020-07-05 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CentBLG', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='comment_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='article',
            name='down_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='article',
            name='up_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='avater',
            field=models.FileField(default='/avaters/default.png', upload_to='avatars/'),
        ),
    ]
