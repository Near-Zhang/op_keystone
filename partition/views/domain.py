from utils.viewmixin import BaseViewMixin
from django.views import View
from ..models import Domain
from django.http import QueryDict


class DomainsView(BaseViewMixin, View):
    """
    域的增、删、改、查
    """
    def get(self, request):
        domain_obj_qs = Domain.objects.all()
        domain_dict_list = []
        for i in domain_obj_qs:
            domain_dict_list.append(i.serialize())
        date = {
            'total': len(domain_dict_list),
            'date': domain_dict_list
        }

        return self.base_json_response(date)

    def post(self, request):
        opts = request.POST.get('opts')
        domain_field = {}

        necessary_opts_list = [
            'name', 'company'
        ]
        additional_opts_list = [
            'enable', 'comment'
        ]
        respond, necessary_opts, additional_opts = self.extract_opts_or_400(opts, necessary_opts_list,
                                                                            additional_opts_list)
        if respond:
            return respond

        domain_field.update(necessary_opts)
        domain_field.update(additional_opts)

        try:
            domain = Domain(**domain_field)
            domain.save()
        except:
            message = 'DatabaseError:failed to save domain'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(domain.serialize())

    def put(self, request):
        put_params = QueryDict(request.body)
        opts = put_params.get('opts')

        necessary_opts_list = ['uuid']
        additional_opts_list = [
            'name', 'purpose', 'enable', 'comment', 'created_by'
        ]
        respond, necessary_opts, additional_opts = self.extract_opts_or_400(opts, necessary_opts_list,
                                                                            additional_opts_list)
        if respond:
            return respond

        try:
            domain = Domain.objects.get(**necessary_opts)
        except:
            message = 'ParamsError:failed to find domain which uuid is %s' % necessary_opts['uuid']
            return self.base_json_response(code=500, message=message)

        for i in additional_opts:
            setattr(domain, i, additional_opts[i])

        try:
            domain.save()
        except:
            message = 'DatabaseError:failed to update domain'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(domain.serialize())

    def delete(self, request):
        delete_params = QueryDict(request.body)
        opts = delete_params.get('opts')

        necessary_opts_list = ['uuid']
        respond, necessary_opts, additional_opts = self.extract_opts_or_400(opts, necessary_opts_list, [])
        if respond:
            return respond

        try:
            domain = Domain.objects.get(**necessary_opts)
        except:
            message = 'ParamsError:failed to find domain which uuid is %s' % necessary_opts['uuid']
            return self.base_json_response(code=500, message=message)

        try:
            domain.delete()
        except:
            message = 'DatabaseError:failed to delete domain'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(domain.serialize())