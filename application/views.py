import re
from functools import wraps

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .models import User, Release, Like, Comment, Collection, Attention, Personal
from .user import UserMethod


def get_pages(totalpage=1, current_page=1):
    WEB_DISPLAY_PAGE = 8
    front_offset = int(WEB_DISPLAY_PAGE / 2)
    if WEB_DISPLAY_PAGE % 2 == 1:
        behind_offset = front_offset
    else:
        behind_offset = front_offset - 1
    if totalpage < WEB_DISPLAY_PAGE:
        return list(range(1, totalpage + 1))
    elif current_page <= front_offset:
        return list(range(1, WEB_DISPLAY_PAGE + 1))
    elif current_page >= totalpage - behind_offset:
        start_page = totalpage - WEB_DISPLAY_PAGE + 1
        return list(range(start_page, totalpage + 1))
    else:
        start_page = current_page - front_offset
        end_page = current_page + behind_offset
        return list(range(start_page, end_page + 1))


def message(mes):
    return {'message': mes}


def login_required(f):
    @wraps(f)
    def decorated_function(request, *args, **kwargs):
        thisuser = UserMethod(request)
        userinfo = thisuser.getUserInfo()
        if userinfo['islogin'] is False:
            return HttpResponseRedirect('/login/')
        return f(request, *args, **kwargs)

    return decorated_function


# 登录
@require_http_methods(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == '' and password == '':
            return render(request, 'login.html', message('不能为空!!'))
        user = User.objects.filter(Q(username=username) | Q(email=username) | Q(phone=username))
        if len(user) == 0:
            return render(request, 'login.html', message('你所登录用户不存在!!!'))
        if not user[0].verify(password):
            return render(request, 'login.html', message('密码错误!!!'))
        request.session['user'] = {
            'islogin': True,
            'username': user[0].username,
            'userid': user[0].id,
        }
        request.session['history'] = []
        return redirect('/')
    this_user = UserMethod(request)
    userinfo = this_user.getUserInfo()
    if userinfo['islogin']:
        return HttpResponseRedirect("/index/")
    return render(request, 'login.html')


# 注册
@require_http_methods(['GET', 'POST'])
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    if username == '' or password == '' or email == '' or phone == '':
        return render(request, 'register.html', message('不能为空!!!'))
    if re.match(r'[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}', email) is None:
        return render(request, 'register.html', message('邮箱格式错误!!!'))
    if re.match(r'^1([38][0-9]|4[579]|5[0-3,5-9]|6[6]|7[0135678]|9[89])\d{8}$', phone) is None:
        return render(request, 'register.html', message('手机号格式错误!!!'))
    user = User.objects.filter(username=username)
    if len(user) != 0:
        return render(request, 'register.html', message('用户名已处在!!!'))
    user = User.objects.filter(email=email)
    if len(user) != 0:
        return render(request, 'register.html', message('邮箱已处在!!!'))
    user = User.objects.filter(phone=phone)
    if len(user) != 0:
        return render(request, 'register.html', message('手机号已处在!!!'))
    User(username=username, password=password, email=email, phone=phone).save()
    return redirect('/login/')


# 退出
@require_http_methods(['GET'])
def quit_(request):
    thisuser = UserMethod(request)
    userinfo = thisuser.getUserInfo()
    if userinfo['islogin'] is True:
        del request.session["user"]
    return HttpResponseRedirect("/")


# 首页
@require_http_methods(['GET'])
def index(request):
    release = Release.objects.all().order_by('-datatime')
    paginator = Paginator(release, 20)
    page = request.GET.get('page', 1)
    pagi = paginator.page(page)
    total_page_number = paginator.num_pages
    page_list = get_pages(int(total_page_number), int(page))
    return render(request, 'index.html', locals())


# 个人中心
@login_required
@require_http_methods(['GET', 'POST'])
def center(request):
    user = User.objects.get(id=UserMethod(request).getUserInfo()['userid'])
    birthday = str(user.birthday)
    if request.method == 'GET':
        return render(request, 'center.html', locals())
    avatar = request.FILES.get('avatar')
    birthday = request.POST.get('birthday')
    print(avatar)
    if avatar is not None and avatar != '':
        user.avatar = avatar
    if birthday != '' and birthday is not None:
        user.birthday = birthday
    user.signature = request.POST.get('signature')
    user.location = request.POST.get('location')
    user.save()
    return redirect('/center/')


# 发布消息
@login_required
@require_http_methods(['GET', 'POST'])
def release(request):
    if request.method == 'GET':
        return render(request, 'release.html')
    content = request.POST.get('content')
    if content == '':
        return render(request, 'release.html', message('不能为空!!!'))
    Release(content=content, user_id=UserMethod(request).getUserInfo()['userid']).save()
    return redirect('/')


# 关注 和 取消关注
@login_required
@require_http_methods(['POST'])
def attention(request):
    author_id = request.POST.get('id')
    user_id = UserMethod(request).getUserInfo()['userid']
    attente = Attention.objects.filter(attention_user_id=author_id, user_id=user_id)
    if len(attente) == 0:
        Attention(attention_user_id=author_id, user_id=user_id).save()
        return HttpResponse('关注成功!!!')
    attente[0].delete()
    return HttpResponse('取消关注!!!')


# 关注列表
@login_required
@require_http_methods(['GET'])
def attention_list(request):
    attention = Attention.objects.filter(user_id=UserMethod(request).getUserInfo()['userid'])
    return render(request, 'attentionList.html', locals())


# 作者空间
@require_http_methods(['GET'])
def author(request):
    author_id = int(request.GET.get('author_id'))
    attention = 0
    if 'user' in request.session:
        user_id = UserMethod(request).getUserInfo()['userid']
        if user_id == author_id:
            return redirect('/center/')
        attention = len(Attention.objects.filter(attention_user_id=author_id, user_id=user_id))
    author_ = User.objects.get(id=author_id)
    return render(request, 'author.html', locals())


# 发布详情
@require_http_methods(['GET'])
def release_info(request):
    release_id = request.GET.get('release_id')
    release = Release.objects.get(id=release_id)
    collection = 0
    like = None
    lenLike = 0
    if 'user' in request.session:
        collection = len(Collection.objects.filter(release_id=release_id, user_id=UserMethod(request).getUserInfo()['userid']))
        like = Like.objects.filter(release_id=release_id, user_id=UserMethod(request).getUserInfo()['userid'])
        lenLike = len(like)
        history = request.session['history']
        history.append(release_id)
        request.session['history'] = history
    comment = Comment.objects.filter(release_id=release_id)
    paginator = Paginator(comment, 10)
    page = request.GET.get('page', 1)
    pagi = paginator.page(page)
    total_page_number = paginator.num_pages
    page_list = get_pages(int(total_page_number), int(page))
    return render(request, 'releaseInfo.html', locals())


# 评论
@login_required
@require_http_methods(['POST'])
def comment(request):
    Comment(info=request.POST.get('info'), release_id=request.POST.get('release_id'), user_id=UserMethod(request).getUserInfo()['userid']).save()
    return HttpResponse('评论成功!!!')


# 收藏
@login_required
@require_http_methods(['POST'])
def collection(request):
    release_id = request.POST.get('release_id')
    user_id = UserMethod(request).getUserInfo()['userid']
    collection = Collection.objects.filter(release_id=release_id, user_id=user_id)
    if len(collection) == 0:
        Collection(release_id=release_id, user_id=user_id).save()
        return HttpResponse('收藏成功!!!')
    collection[0].delete()
    return HttpResponse('取消收藏!!!')


# 收藏列表
@login_required
@require_http_methods(['GET'])
def collection_list(request):
    collection = Collection.objects.filter(user_id=UserMethod(request).getUserInfo()['userid'])
    paginator = Paginator(collection, 10)
    page = request.GET.get('page', 1)
    pagi = paginator.page(page)
    total_page_number = paginator.num_pages
    page_list = get_pages(int(total_page_number), int(page))
    return render(request, 'collection_list.html', locals())


# 点赞
@login_required
@require_http_methods(['POST'])
def like(request):
    release_id = request.POST.get('release_id')
    user_id = UserMethod(request).getUserInfo()['userid']
    like = Like.objects.filter(release_id=release_id, user_id=user_id)
    if len(like) == 0:
        Like(release_id=release_id, status=True, user_id=user_id).save()
    else:
        if like[0].status is True:
            like[0].status = False
        elif like[0].status is False:
            like[0].status = True
        like[0].save()
    return HttpResponse()


# 私信
@login_required
@require_http_methods(['GET'])
def private(request):
    to_user_id = request.GET.get('to_user_id')
    author = User.objects.get(id=to_user_id)
    personal = Personal.objects.filter(
        Q(from_user_id=UserMethod(request).getUserInfo()['userid'], to_user_id=to_user_id) | Q(to_user_id=UserMethod(request).getUserInfo()['userid'],
                                                                                               from_user_id=to_user_id)).order_by('datetime')
    print(personal)
    return render(request, 'pricate.html', locals())


# 私信发送
@login_required
@require_http_methods(['POST'])
def send_private(request):
    info = request.POST.get('info')
    to_user_id = request.POST.get('to_user_id')
    if info == '':
        return HttpResponse('信息不能为空!!')
    Personal(info=info, from_user_id=UserMethod(request).getUserInfo()['userid'], to_user_id=to_user_id).save()
    return HttpResponse('发送成功')


# 私信列表
@login_required
@require_http_methods(['GET'])
def private_list(request):
    lit = []
    private = []
    personal = Personal.objects.filter(to_user_id=UserMethod(request).getUserInfo()['userid'])
    for x in personal:
        if x.from_user_id not in lit:
            lit.append(x.from_user_id)
    for y in lit:
        private.append(User.objects.get(id=y))
    return render(request, 'private_list.html', locals())


# 回复页面
@login_required
@require_http_methods(['GET'])
def reply(request):
    from_user_id = request.GET.get('from_user_id')
    author = User.objects.get(id=from_user_id)
    personal = Personal.objects.filter(
        Q(from_user_id=UserMethod(request).getUserInfo()['userid'], to_user_id=from_user_id) | Q(to_user_id=UserMethod(request).getUserInfo()['userid'],
                                                                                                 from_user_id=from_user_id)).order_by('datetime')
    return render(request, 'reply.html', locals())


# 历史
@login_required
@require_http_methods(['GET'])
def history(request):
    hist_ = []
    print(request.session['history'])
    for x in request.session['history']:
        hist_.append(Release.objects.get(id=x))
    return render(request, 'history.html', locals())


# 我的发布
@login_required
@require_http_methods(['GET'])
def my_release(request):
    release = Release.objects.filter(user_id=UserMethod(request).getUserInfo()['userid'])
    paginator = Paginator(release, 10)
    page = request.GET.get('page', 1)
    pagi = paginator.page(page)
    total_page_number = paginator.num_pages
    page_list = get_pages(int(total_page_number), int(page))
    return render(request, 'my_release.html', locals())
