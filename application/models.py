from django.contrib.auth.hashers import make_password, check_password
from django.db import models


# Create your models here.
class User(models.Model):
    avatar = models.ImageField('用户头像', upload_to='user/', default='user/default.jpg')
    username = models.CharField('用户名', max_length=256, null=False)
    hash_password = models.CharField('密码', max_length=256, null=False)
    birthday = models.DateField('生日', null=True)
    email = models.CharField('邮箱', max_length=64, null=False)
    phone = models.CharField('手机号', max_length=16, null=False)
    location = models.CharField('所在地', max_length=256, null=True)
    signature = models.TextField('个性签名', null=True)
    register = models.DateField('注册时间', auto_now=True)

    def __str__(self):
        return self.username

    @property
    def password(self):
        raise AttributeError('没有设置密码!!!')

    @password.setter
    def password(self, password):
        self.hash_password = make_password(password)

    def verify(self, password):
        return check_password(password, self.hash_password)

    class Meta:
        db_table = 'user'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name


class Release(models.Model):
    content = models.TextField('发布内容', null=False)
    user = models.ForeignKey(User, verbose_name='发布用户', on_delete=models.CASCADE)
    datatime = models.DateTimeField('发布时间', auto_now=True)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'release'
        verbose_name = '发布管理'
        verbose_name_plural = verbose_name


class Like(models.Model):
    release = models.ForeignKey(Release, verbose_name='点赞的作品', on_delete=models.CASCADE)
    status = models.BooleanField('点赞状态', choices=((True, '点赞'), (False, '取消')), default=True)
    user = models.ForeignKey(User, verbose_name='点赞用户', on_delete=models.CASCADE)

    class Meta:
        db_table = 'like'
        verbose_name = '点赞管理'
        verbose_name_plural = verbose_name


class Comment(models.Model):
    info = models.CharField('评论的内容', max_length=2048, null=False)
    release = models.ForeignKey(Release, verbose_name='评论的作品', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='评论用户', on_delete=models.CASCADE)
    datetime = models.DateTimeField('评论时间', auto_now=True)

    class Meta:
        db_table = 'comment'
        verbose_name = '评论管理'
        verbose_name_plural = verbose_name


class Collection(models.Model):
    release = models.ForeignKey(Release, verbose_name='收藏的文章', on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)

    class Meta:
        db_table = 'collection'
        verbose_name = '收藏管理'
        verbose_name_plural = verbose_name


class Attention(models.Model):
    attention_user = models.ForeignKey(User, verbose_name='被关注的用户', on_delete=models.CASCADE, related_name='attention_user')
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.CASCADE)

    class Meta:
        db_table = 'attention'
        verbose_name = '关注管理'
        verbose_name_plural = verbose_name


class Personal(models.Model):
    info = models.CharField('发送的信息', max_length=2048, null=False)
    from_user = models.ForeignKey(User, verbose_name='发送用户', on_delete=models.CASCADE, related_name='from_user')
    to_user = models.ForeignKey(User, verbose_name='接受用户', on_delete=models.CASCADE, related_name='to_user')
    datetime = models.DateTimeField('时间', auto_now=True)

    class Meta:
        db_table = 'personal'
        verbose_name = '私信管理'
        verbose_name_plural = verbose_name
