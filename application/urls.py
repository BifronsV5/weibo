from django.urls import path, re_path

from .uploads import upload_image
from .views import index, login, register, quit_, center, release, attention, attention_list, author, like, comment, release_info, collection, collection_list, \
    private, send_private, require_http_methods, private_list, reply, history, my_release

urlpatterns = [
    path('', index, name='index'),
    path('login/', login, name='login'),
    path('accounts/login/', login),
    path('register/', register, name='register'),
    path('quit/', quit_, name='quit'),
    path('center/', center, name='center'),
    path('author/', author, name='author'),
    path('release/', release, name='release'),
    path('release_info', release_info, name='release_info'),
    path('attention', attention, name='attention'),
    path('attention_list', attention_list, name='attention_list'),
    path('collection/', collection, name='collection'),
    path('collection_list/', collection_list, name='collection_list'),
    path('like/', like, name='like'),
    path('comment/', comment, name='comment'),
    path('private', private, name='private'),
    path('send_private', send_private, name='send_private'),
    path('require_http_methods', require_http_methods, name='require_http_methods'),
    path('private_list', private_list, name='private_list'),
    path('reply', reply, name='reply'),
    path('history', history, name='history'),
    path('my_release', my_release, name='my_release'),
    re_path(r'^upload/(?P<dir_name>.*)$', upload_image, name='upload_image'),
]
