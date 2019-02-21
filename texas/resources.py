from tastypie.resources import Resource
from django.conf.urls import url
from src import service
import json


class TexasResource(Resource):
    class Meta:
        resource_name = 'texas'
        # always_return_data = True
        # include_resource_uri = False

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/join/(?P<name>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('join'), name="api_join"),
            url(r"^(?P<resource_name>%s)/heartbeat/(?P<pos>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('heartbeat'), name="api_heartbeat"),
            url(r"^(?P<resource_name>%s)/start/(?P<pos>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('start'), name="api_start"),
            url(r"^(?P<resource_name>%s)/check/(?P<pos>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('check'), name="api_check"),
            url(r"^(?P<resource_name>%s)/call/(?P<pos>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('call'), name="api_call"),
            url(r"^(?P<resource_name>%s)/raise/(?P<pos>[\w\d_.-]+)/(?P<amount>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('raise_bet'), name="api_raise_bet"),
            url(r"^(?P<resource_name>%s)/fold/(?P<pos>[\w\d_.-]+)/$" % self._meta.resource_name,
                self.wrap_view('fold'), name="api_fold"),
            url(r"^(?P<resource_name>%s)/info/$" % self._meta.resource_name,
                self.wrap_view('info'), name="api_info"),
        ]

    def join(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        name = kwargs['name']
        dummy_data = {}
        try:
            pos, host = service.add_player(name)
            dummy_data["pos"] = pos
            dummy_data["data"] = self._game_info_response()
            dummy_data["status"] = 1
        except Exception, e:
            dummy_data["status"] = 0
            dummy_data["err_info"] = str(e)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, bundle)
        return resp

    def start(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        pos = kwargs['pos']
        dummy_data = {}
        try:
            print "######start:", pos
            service.start_game(int(pos))
            dummy_data["data"] = self._game_info_response()
            dummy_data["status"] = 1
        except Exception, e:
            dummy_data["status"] = 0
            dummy_data["err_info"] = str(e)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, bundle)
        return resp

    def check(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        pos = kwargs['pos']
        dummy_data = {}
        try:
            service.player_action(int(pos), 'check')
            dummy_data["data"] = self._game_info_response()
            dummy_data["status"] = 1
        except Exception, e:
            dummy_data["status"] = 0
            dummy_data["err_info"] = str(e)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, bundle)
        return resp

    def call(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        pos = kwargs['pos']
        dummy_data = {}
        try:
            service.player_action(int(pos), 'call')
            dummy_data["data"] = self._game_info_response()
            dummy_data["status"] = 1
        except Exception, e:
            dummy_data["status"] = 0
            dummy_data["err_info"] = str(e)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, bundle)
        return resp

    def raise_bet(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        print "#######raise:", kwargs
        amount = kwargs.get('amount')
        pos = kwargs.get('pos')
        dummy_data = {}
        try:
            service.player_action(int(pos), 'raise', int(amount))
            dummy_data["data"] = self._game_info_response()
            dummy_data["status"] = 1
        except Exception, e:
            dummy_data["status"] = 0
            dummy_data["err_info"] = str(e)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, bundle)
        return resp

    def fold(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        pos = kwargs['pos']
        dummy_data = {}
        try:
            service.player_action(int(pos), 'fold')
            dummy_data["data"] = self._game_info_response()
            dummy_data["status"] = 1
        except Exception, e:
            dummy_data["status"] = 0
            dummy_data["err_info"] = str(e)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, bundle)
        return resp

    def info(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        dummy_data = {}
        try:
            dummy_data["data"] = self._game_info_response()
            dummy_data["status"] = 1
        except Exception, e:
            dummy_data["status"] = 0
            dummy_data["err_info"] = str(e)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, bundle)
        return resp

    def heartbeat(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        pos = kwargs['pos']
        dummy_data = {}
        try:
            service.heartbeat(int(pos))
            dummy_data["data"] = self._game_info_response()
            dummy_data["status"] = 1
        except Exception, e:
            dummy_data["status"] = 0
            dummy_data["err_info"] = str(e)
        bundle = self.build_bundle(obj=dummy_data, data=dummy_data, request=request)
        resp = self.create_response(request, bundle)
        return resp

    @staticmethod
    def _game_info_response():
        # response_json = json.dumps(service.game_info())
        response_json = service.game_info()
        return response_json