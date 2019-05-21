class UserMethod(object):
    def __init__(self, request):
        self.request = request
        self.uinfo = self.getUserInfo()

    def getUserInfo(self):
        if 'user' in self.request.session:
            return self.request.session['user']
        else:
            return {'islogin': False}
