# Generated by Django 2.2 on 2020-07-08 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CentBLG', '0002_userinfo_qq'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='vip_credit',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='vip_level',
            field=models.IntegerField(null=True),
        ),
    ]
