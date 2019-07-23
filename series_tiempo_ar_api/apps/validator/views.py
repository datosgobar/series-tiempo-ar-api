#! coding: utf-8
import json
from json import JSONDecodeError

from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from series_tiempo_ar import TimeSeriesDataJson
from series_tiempo_ar.validations import get_distribution_errors

from series_tiempo_ar_api.apps.validator.custom_exceptions import \
    BadRequestError


class ValidatorView(View):

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        try:
            request_body = self.load_request_body(request)
        except BadRequestError as e:
            return HttpResponseBadRequest(str(e))

        report = self.generate_error_report(request_body)
        return JsonResponse(report, json_dumps_params={'indent': 4})

    def load_request_body(self, request):
        try:
            request_body = json.loads(request.body)
        except JSONDecodeError:
            msg = "Error leyendo la data del request"
            raise BadRequestError(msg)

        if not ('catalog_url' in request_body and
                'distribution_id' in request_body):
            msg = "catalog_url y distribution_id son parametros obligatorios"
            raise BadRequestError(msg)

        return request_body

    def generate_error_report(self, request_body):
        catalog_url = request_body.get('catalog_url')
        distribution_id = request_body.get('distribution_id')
        catalog_format = request_body.get('catalog_format')
        report = {'catalog_url': catalog_url,
                  'distribution_id': distribution_id, }
        try:
            datajson = TimeSeriesDataJson(
                catalog_url, catalog_format=catalog_format)
            error_list = get_distribution_errors(datajson, distribution_id)
            found_issues = len(error_list)
            detail = [err.args[0] for err in error_list]
        except Exception as e:
            found_issues = 1
            detail = [str(e)]
        report['found_issues'] = found_issues
        report['detail'] = detail
        return report
