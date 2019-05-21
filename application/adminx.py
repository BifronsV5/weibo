import xadmin
from xadmin import views
from .models import User, Release, Like, Comment, Collection, Attention, Personal


# Register your models here.
class WeiboSetting(object):
    site_title = 'Elphan后台'
    site_footer = '我的系统'


class UserAdmin(object):
    list_display = ['avatar', 'username', 'hash_password', 'birthday', 'email', 'phone', 'location', 'register']


class ReleaseAdmin(object):
    list_display = ['content', 'user', 'datatime']


class LikeAdmin(object):
    list_display = ['status', 'user']


class CommentAdmin(object):
    list_display = ['info', 'user', 'datetime']


class CollectionAdmin(object):
    list_display = ['release', 'user']


class AttentionAdmin(object):
    list_display = ['attention_user', 'user']


class PersonalAdmin(object):
    list_display = ['info', 'from_user', 'to_user', 'datetime']


xadmin.site.register(views.CommAdminView, WeiboSetting)
xadmin.site.register(User, UserAdmin)
xadmin.site.register(Release, ReleaseAdmin)
xadmin.site.register(Like, LikeAdmin)
xadmin.site.register(Comment, CommentAdmin)
xadmin.site.register(Collection, CollectionAdmin)
xadmin.site.register(Attention, AttentionAdmin)
xadmin.site.register(Personal, PersonalAdmin)
