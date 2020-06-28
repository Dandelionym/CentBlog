from django.db import models
from django.contrib.auth.models import AbstractUser
from django.http import request

class UserInfo(AbstractUser):
	"""
	User Information
	"""
	nid = models.AutoField(primary_key=True)
	telephone = models.CharField(max_length=11, null=True, unique=True)
	avater = models.FileField(upload_to='avatars/', default='/avaters/default.png')
	
	create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
	
	blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)
	def __str__(self):
		return self.username
	
	
class Blog(models.Model):
	"""
	Blogs Information (Sites table)
	"""
	nid = models.AutoField(primary_key=True)
	title = models.CharField(verbose_name='个人博客标题', max_length=64)
	site_name = models.CharField(verbose_name='站点名称', max_length=64)
	theme = models.CharField(verbose_name='博客主题', max_length=32)
	
	def __str__(self):
		return self.title
	

class Category(models.Model):
	"""
	Master's personal articles table
	"""
	nid = models.AutoField(primary_key=True)
	title = models.CharField(verbose_name='分类标题', max_length=32)
	blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)
	def __str__(self):
		return self.title


class Tag(models.Model):
	"""
	Tag table
	"""
	nid = models.AutoField(primary_key=True)
	title = models.CharField(verbose_name='标签名称', max_length=32)
	blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)
	
	def __str__(self):
		return self.title


class Article(models.Model):
	nid = models.AutoField(primary_key=True)
	title = models.CharField(max_length=50, verbose_name='文章标题')
	desc = models.CharField(max_length=255, verbose_name='文章描述')
	create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
	
	user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
	category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
	tags = models.ManyToManyField(
		to='Tag',
		through='Article2Tag',
		through_fields=('article', 'tag'),
	)
	content = models.TextField()
	
	def __str__(self):
		return self.title


class Article2Tag(models.Model):
	nid = models.AutoField(primary_key=True)
	article = models.ForeignKey(verbose_name='文章', to='Article', to_field='nid', on_delete=models.CASCADE)
	tag = models.ForeignKey(verbose_name='标签', to='Tag', to_field='nid', on_delete=models.CASCADE)
	
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
	user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
	article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', on_delete=models.CASCADE)
	create_time = models.DateTimeField(verbose_name='发表时间', auto_now_add=True)
	content = models.CharField(verbose_name='评论内容', max_length=255)
	parent_comment = models.ForeignKey("Comment", null=True, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.content














