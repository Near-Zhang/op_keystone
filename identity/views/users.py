from utils.baseview import BaseView
from ..models import User
from django.http import QueryDict


class Users(BaseView):
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
        user_opts = {}

        necessary_opts_list = ['user_name', 'real_name', 'department',
                               'email', 'phone_number']
        ok, necessary_opts = self.get_necessary_opts(request.POST, necessary_opts_list)
        if not ok:
            return necessary_opts
        user_opts.update(necessary_opts)

        additional_opts_list = ['company_qq', 'comment', 'created_by', 'enable']
        additional_opts = self.get_additional_opts(request.POST, additional_opts_list)
        user_opts.update(additional_opts)
        user = User(**user_opts)

        try:
            user.save()
        except:
            message = 'DatabaseError:failed to save object'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(user.serialize())

    def put(self, request):
        put_params = QueryDict(request.body)

        necessary_opts_list = ['id']
        ok, necessary_opts = self.get_necessary_opts(put_params, necessary_opts_list)
        if not ok:
            return necessary_opts

        try:
            user = User.objects.get(**necessary_opts)
        except:
            message = 'ParamsError:failed to find user which id is %s' %necessary_opts['id']
            return self.base_json_response(code=500, message=message)

        additional_opts_list = ['user_name', 'real_name', 'department',
                                'email', 'phone_number', 'company_qq',
                                'comment', 'created_by', 'enable']
        additional_opts = self.get_additional_opts(put_params, additional_opts_list)
        for i in additional_opts:
            setattr(user, i, additional_opts[i])

        try:
            user.save()
        except:
            message = 'DatabaseError:failed to update object'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(user.serialize())

    def delete(self, request):
        delete_params = QueryDict(request.body)

        necessary_opts_list = ['id']
        ok, necessary_opts = self.get_necessary_opts(delete_params, necessary_opts_list)
        if not ok:
            return necessary_opts

        try:
            user = User.objects.get(**necessary_opts)
        except:
            message = 'ParamsError:failed to find user which id is %s' % necessary_opts['id']
            return self.base_json_response(code=500, message=message)

        try:
            user.delete()
        except:
            message = 'DatabaseError:failed to delete object'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(user.serialize())

