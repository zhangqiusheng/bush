from django.conf.urls import url
from tastypie.resources import Resource
from tastypie.utils import trailing_slash

from staf_wrapper import wrapper_STAF
from models import *
from utils import *

import tasks



class ProjectStafResource(Resource):
    def __init__(self):
        Resource.__init__(self)
        self.staf_obj = wrapper_STAF.staf_obj

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/?$" % self._meta.resource_name, self.wrap_view('staf_api'), name='staf_api'),
            # following is new APIs
            url(r"^trigger_deb/(?P<mode>.+)/(?P<task_id>.+?)$", self.wrap_view('trigger_deb'), name='trigger_deb'),
            url(r"^trigger_iso/(?P<mode>.+)/(?P<task_name>.+?)$", self.wrap_view('trigger_iso'), name='trigger_iso'),
            url(r"^get_result/(?P<staf_handle_key>.+?)/(?P<machine_ip>.+?)/$", self.wrap_view('get_result'), name='get_result'),
            url(r"^query_task/(?P<suite_id>.+?)/?$", self.wrap_view('query_task'), name='query_task'),
            url(r"^query_suite/?$", self.wrap_view('query_suite'), name='query_suite'),
        ]

    def query_suite(self, request, **kwargs):
        suite_list = list()
        suites = Suite.objects.all()
        for suite in suites:
            suite_struct_dict = dict()
            suite_struct_dict['id'] = suite.id
            suite_struct_dict['name'] = suite.name
            suite_list.append(suite_struct_dict)
            # data_struct.setdefault(suite.name, dict())
            # tasks = suite.task_set.all()
            # for task in tasks:
            #     data_struct[suite.name].setdefault(task.name, list())
            #     task_cases = task.task_case_set.all()
            #     for taskcase in task_cases:
            #         data_struct[suite.name][task.name].append(taskcase.case.__dict__)
        return self.create_response(request, {"key": suite_list})

    def query_task(self, request, **kwargs):
        task_list = list()
        suite_id = kwargs['suite_id']
        tasks = Suite.objects.get(id=suite_id).task_set.all()

        for task in tasks:
            task_struct_dict = dict()
            task_struct_dict['name'] = task.name
            task_struct_dict['id'] = task.id
            task_struct_dict['suite'] = task.suite.name
            task_list.append(task_struct_dict)
            # data_struct.setdefault(task.name, list())
            # task_cases = task.task_case_set.all()
            # for taskcase in task_cases:
            #     data_struct[task.name].append(taskcase.case.__dict__)
        return self.create_response(request, {"key": task_list})


    def trigger_deb(self, request, **kwargs):
        p_task = Task.objects.get(id=int(kwargs['task_id']))
        task_name = p_task.name
        # assume the first machine is ok!
        machine_ip = p_task.suite.machine_set.all()[0].address
        task_report = Task_Report(task=p_task, machine=p_task.suite.machine_set.all()[0])
        task_report.save()
        p_task_report = Task_Report.objects.get(id=task_report.id)
        child_cases = Task_Case.objects.filter(task=p_task)
        generate_xml(p_task.name, child_cases, task_report.id)
        if kwargs['mode'] == u'non-blocking':
            exec_handle = self.staf_obj.execute(task_name, machine_ip)
            tasks.monitor.delay(self.staf_obj, exec_handle, p_task_report, machine_ip)
            return self.create_response(request, {'handle': exec_handle,
                                                  'task_name': task_name,
                                                  'machine_ip': machine_ip})
        else:
            raise

    def trigger_iso(self, request, **kwargs):
        pass

    def get_result(self, request, **kwargs):
        staf_handle_key = kwargs['staf_handle_key']
        machine_ip = kwargs['machine_ip']
        if self._query(staf_handle_key,machine_ip) == 'on-going':
            return self.create_response(request, {"key": 'on-going'})
        return self.create_response(request, self.staf_obj.result)

    def _query(self, exec_handle, machine_ip):
        if self.staf_obj.query(job_id=exec_handle, location=machine_ip) == 0:
            return 'has-done'
        else:
            return 'on-going'

    def _unregister(self):
        if self.staf_obj.unregister() == 0:
            return 'successful'
        else:
            return 'unsuccessful'

    def staf_api(self, request, **kwargs):
        staf_obj = wrapper_STAF.staf_obj
        staf_obj.execute()
        while True:
            time.sleep(5)
            # successful
            if staf_obj.query() == 0:
                print staf_obj.result
                break
            # unsuccessful
            else:
                print 'is on-going'
        staf_obj.unregister()

        return self.create_response(request, {"key": staf_obj.result})

    class Meta:
        resource_name = 'staf'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
