from utils.baseview import BaseView
from ..models import User
from django.http import QueryDict
from utils.tools import password_hash


class UsersView(BaseView):
    """
    用户的增、删、改、查
    """
    def get(self, request):
        user_obj_qs = User.objects.all()
        user_dict_list = []
        for i in user_obj_qs:
            user_dict_list.append(i.serialize())
        date = {
            'total': len(user_dict_list),
            'date': user_dict_list
        }

        return self.base_json_response(date)

    def post(self, request):
        opts = request.POST.get('opts')
        user_fields = {}

        necessary_opts_list = [
            'user_name', 'password', 'real_name', 'department', 'email',
            'phone_number'
        ]
        additional_opts_list = [
            'company_qq', 'comment', 'enable'
        ]
        respond, necessary_opts, additional_opts= self.extract_opts(opts, necessary_opts_list, additional_opts_list)
        if respond:
            return respond
        necessary_opts['password'] = password_hash(necessary_opts['password'])
        user_fields.update(necessary_opts)
        user_fields.update(additional_opts)
        user = User(**user_fields)

        try:
            user.save()
        except:
            message = 'DatabaseError:failed to save user'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(user.serialize())

    def put(self, request):
        put_params = QueryDict(request.body)
        opts = put_params.get('opts')

        necessary_opts_list = ['id']
        additional_opts_list = [
            'user_name', 'password', 'real_name', 'department', 'email',
            'phone_number', 'company_qq', 'comment', 'enable'
        ]
        respond, necessary_opts, additional_opts = self.extract_opts(opts, necessary_opts_list, additional_opts_list)
        if respond:
            return respond

        try:
            user = User.objects.get(**necessary_opts)
        except:
            message = 'ParamsError:failed to find user which id is %s' % necessary_opts['id']
            return self.base_json_response(code=500, message=message)

        for i in additional_opts:
            if i == 'password':
                additional_opts[i] = password_hash(additional_opts[i])
            setattr(user, i, additional_opts[i])

        try:
            user.save()
        except:
            message = 'DatabaseError:failed to update user'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(user.serialize())

    def delete(self, request):
        delete_params = QueryDict(request.body)
        opts = delete_params.get('opts')

        necessary_opts_list = ['id']
        respond, necessary_opts, additional_opts = self.extract_opts(opts, necessary_opts_list, [])
        if respond:
            return respond

        try:
            user = User.objects.get(**necessary_opts)
        except:
            message = 'ParamsError:failed to find user which id is %s' % necessary_opts['id']
            return self.base_json_response(code=500, message=message)

        try:
            user.delete()
        except:
            message = 'DatabaseError:failed to delete user'
            return self.base_json_response(code=500, message=message)

        related_user_obj_qs = User.objects.filter(created_by=necessary_opts['id'])
        for i in related_user_obj_qs:
            i.created_by = 1
            i.save()

        return self.base_json_response(user.serialize())

