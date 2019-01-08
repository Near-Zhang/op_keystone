from django.views import View
from utils.viewmixin import BaseViewMixin, LoginRequireMixin
from ..models import User
from partition.models import Domain
from credence.models import Token
from utils.tools import (
    generate_mapping_uuid, datetime_convert, get_datetime_with_tz
)
from pytz import timezone
from datetime import datetime, timedelta


class LoginView(BaseViewMixin, View):

    def post(self, request):
        opts = request.POST.get('opts')
        necessary_opts_list = ['type']

        failed, necessary_opts, omit = self.extract_opts_or_400(opts, necessary_opts_list, [])
        if failed:
            return failed

        login_type = necessary_opts['type']
        if login_type == 'phone':
            necessary_opts_list = ['phone', 'password']
        elif login_type == 'email':
            necessary_opts_list = ['email', 'password']
        else:
            necessary_opts_list = ['domain', 'username', 'password']

        failed, necessary_opts, omit = self.extract_opts_or_400(opts, necessary_opts_list, [])
        if failed:
            return failed

        if necessary_opts.get('domain'):
            domain_name = necessary_opts.pop('domain')
            respond, domain = self.get_object_or_404(Domain, name=domain_name)
            if domain:
                necessary_opts['domain'] = domain.uuid
            else:
                return respond

        password = necessary_opts.pop('password')
        respond, user = self.get_object_or_404(User, **necessary_opts)
        if user:
            if user.check_password(password):
                now = get_datetime_with_tz()
                token = generate_mapping_uuid(user.domain, user.username + datetime_convert(now))
                data = {
                    "uuid": user.uuid,
                    "token": token,
                    "name": user.name
                }
                user.last_time = now
                user.save()
                _, token_ins = self.get_object_or_404(Token, user=user.uuid)
                expire_date = get_datetime_with_tz(minutes=+50)
                if token_ins:
                    token_ins.token = token
                    token_ins.expire_date = expire_date
                else:
                    token_ins = Token(user=user.uuid, token=token, expire_date=expire_date)
                token_ins.save()

                return self.base_json_response(data)

        message = "LoginError:user does not exist or password error"
        return self.base_json_response(code=403, message=message)


class LogoutView(BaseViewMixin, View):

    def post(self, request):
        user = request.user
        response, token = self.get_object_or_404(Token, user=user.uuid)
        if token:
            token.expire_date = get_datetime_with_tz()
            token.save()
        return self.base_json_response('user %s succeed to logout' % user.name)