from django.db import models
from django.contrib.auth.models import AbstractUser
from django.http import request

class UserInfo(AbstractUser):
	"""
	User Information
	"""
	nid = models.AutoField(primary_key=True)
	telephone = models.CharField(max_length=11, null=True, unique=True)
	avatar = models.FileField(upload_to='avatars/', default='/avatars/default_head_img.png')
	create_time = models.DateTimeField(verbose_name='createTime', auto_now_add=True)
	
	level = models.IntegerField(null=True, default=1)
	ps_credit = models.IntegerField(null=True, default=0)
	ps_motto = models.TextField(max_length=150, null=True, default='')
	is_vip = models.BooleanField(null=True, default=False)
	vip_level = models.IntegerField(null=True, default=0)
	vip_credit = models.IntegerField(null=True, default=0)
	is_certified = models.IntegerField(null=True, default=0)
	qq = models.CharField(max_length=15, null=True)
	
	today_comments = models.IntegerField(default=0)
	today_lookup = models.IntegerField(default=0)
	today_release = models.IntegerField(default=0)
	
	
	blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)
	def __str__(self):
		return self.username
	
	
class Blog(models.Model):
	"""
	Blogs Information (Sites table)
	"""
	nid = models.AutoField(primary_key=True)
	title = models.CharField(verbose_name='BlogTitle', max_length=64)
	site_name = models.CharField(verbose_name='BlogTitleName', max_length=64)
	theme = models.CharField(verbose_name='BlogTheme', max_length=32)
	
	def __str__(self):
		return self.title
	

class Category(models.Model):
	"""
	Master's personal articles table
	"""
	nid = models.AutoField(primary_key=True)
	title = models.CharField(verbose_name='categoryTitle', max_length=32)
	blog = models.ForeignKey(verbose_name='BelongsToBlog', to='Blog', to_field='nid', on_delete=models.CASCADE)
	def __str__(self):
		return self.title


class Tag(models.Model):
	"""
	Tag table
	"""
	nid = models.AutoField(primary_key=True)
	title = models.CharField(verbose_name='TagName', max_length=32)
	blog = models.ForeignKey(verbose_name='BelongsToBlog', to='Blog', to_field='nid', on_delete=models.CASCADE)
	
	def __str__(self):
		return self.title


class Article(models.Model):
	nid = models.AutoField(primary_key=True)
	title = models.CharField(max_length=50, verbose_name='ArticleTopic')
	desc = models.CharField(max_length=255, verbose_name='ArticleDescription')
	create_time = models.DateTimeField(verbose_name='releaseTime', auto_now_add=True)
	content = models.TextField()
	
	comment_count = models.IntegerField(default=0)
	up_count = models.IntegerField(default=0)
	down_count = models.IntegerField(default=0)
	views = models.IntegerField(default=0, null=True)
	
	user = models.ForeignKey(verbose_name='Author', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
	category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
	tags = models.ManyToManyField(
		to='Tag',
		through='Article2Tag',
		through_fields=('article', 'tag'),
	)
	
	def __str__(self):
		return self.title


class Article2Tag(models.Model):
	nid = models.AutoField(primary_key=True)
	article = models.ForeignKey(verbose_name='Article', to='Article', to_field='nid', on_delete=models.CASCADE)
	tag = models.ForeignKey(verbose_name='Tag', to='Tag', to_field='nid', on_delete=models.CASCADE)
	
	class Meta:
		unique_together = [
			('article', 'tag'),
		]
	
	def __str__(self):
		return self.article.title + " --- " + self.tag.title


class ArticleUpDown(models.Model):
	"""
	Support table
	"""
	nid = models.AutoField(primary_key=True)
	user = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE)
	article = models.ForeignKey('Article', null=True, on_delete=models.CASCADE)
	is_up = models.BooleanField(default=True)
	
	class Meta:
		unique_together = [
			('article', 'user'),
		]


class Comment(models.Model):
	nid = models.AutoField(primary_key=True)
	user = models.ForeignKey(verbose_name='Commenter', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
	article = models.ForeignKey(verbose_name='CommentArticle', to='Article', to_field='nid', on_delete=models.CASCADE)
	create_time = models.DateTimeField(verbose_name='releaseTime', auto_now_add=True)
	content = models.CharField(verbose_name='CommentContent', max_length=255)
	parent_comment = models.ForeignKey("Comment", null=True, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.content

