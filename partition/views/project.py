from utils.viewmixin import BaseViewMixin
from django.views import View
from ..models import Project
from django.http import QueryDict


class ProjectsView(BaseViewMixin, View):
    """
    项目的增、删、改、查
    """
    def get(self, request):
        project_obj_qs = Project.objects.all()
        project_dict_list = []
        for i in project_obj_qs:
            project_dict_list.append(i.serialize())
        date = {
            'total': len(project_dict_list),
            'date': project_dict_list
        }

        return self.base_json_response(date)

    def post(self, request):
        opts = request.POST.get('opts')
        project_field = {}

        necessary_opts_list = [
            'project_name', 'purpose'
        ]
        additional_opts_list = [
            'enable', 'comment'
        ]
        respond, necessary_opts, additional_opts = self.extract_opts_or_400(opts, necessary_opts_list,
                                                                            additional_opts_list)
        if respond:
            return respond

        project_field.update(necessary_opts)
        project_field.update(additional_opts)
        project = Project(**project_field)

        try:
            project.save()
        except:
            message = 'DatabaseError:failed to save project'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(project.serialize())

    def put(self, request):
        put_params = QueryDict(request.body)
        opts = put_params.get('opts')

        necessary_opts_list = ['uuid']
        additional_opts_list = [
            'project_name', 'purpose', 'enable', 'comment'
        ]
        respond, necessary_opts, additional_opts = self.extract_opts_or_400(opts, necessary_opts_list,
                                                                            additional_opts_list)
        if respond:
            return respond

        try:
            project = Project.objects.get(**necessary_opts)
        except:
            message = 'ParamsError:failed to find project which uuid is %s' % necessary_opts['uuid']
            return self.base_json_response(code=500, message=message)

        for i in additional_opts:
            setattr(project, i, additional_opts[i])

        try:
            project.save()
        except:
            message = 'DatabaseError:failed to update project'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(project.serialize())

    def delete(self, request):
        delete_params = QueryDict(request.body)
        opts = delete_params.get('opts')

        necessary_opts_list = ['uuid']
        respond, necessary_opts, additional_opts = self.extract_opts_or_400(opts, necessary_opts_list, [])
        if respond:
            return respond

        try:
            project = Project.objects.get(**necessary_opts)
        except:
            message = 'ParamsError:failed to find project which uuid is %s' % necessary_opts['uuid']
            return self.base_json_response(code=500, message=message)

        try:
            project.delete()
        except:
            message = 'DatabaseError:failed to delete project'
            return self.base_json_response(code=500, message=message)

        return self.base_json_response(project.serialize())