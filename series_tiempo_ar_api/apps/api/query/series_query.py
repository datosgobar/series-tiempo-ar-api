import json

from iso8601 import iso8601

from series_tiempo_ar_api.apps.api.helpers import get_periodicity_human_format
from series_tiempo_ar_api.apps.api.query import constants
from series_tiempo_ar_api.apps.api.query.metadata_response import MetadataResponse
from series_tiempo_ar_api.apps.management import meta_keys


class SeriesQuery:
    """Encapsula metadatos de la consulta de una serie con un modo de representación determinado"""

    def __init__(self, field_model, rep_mode):
        self.field_model = field_model
        self.rep_mode = rep_mode
        self.metadata = json.loads(self.field_model.metadata)

    def periodicity(self):
        serie_periodicity = meta_keys.get(self.field_model, meta_keys.PERIODICITY)
        distribution_periodicity = meta_keys.get(self.field_model.distribution, meta_keys.PERIODICITY)
        return get_periodicity_human_format(serie_periodicity or distribution_periodicity)

    def get_metadata(self, flat=False, simple=True):
        response = MetadataResponse(self.field_model, flat=flat, simple=simple).get_response()

        self._add_is_percentage(response, flat)
        self._add_rep_mode(response, flat)
        return response

    def _add_is_percentage(self, response, flat):
        is_percentage = self.rep_mode in constants.PERCENT_REP_MODES
        if not flat:
            response['field']['is_percentage'] = is_percentage
        else:
            response['field_is_percentage'] = is_percentage

    def _add_rep_mode(self, response, flat):
        units = constants.VERBOSE_REP_MODES[self.rep_mode] or self.metadata.get('units')
        if not flat:
            response['field']['representation_mode'] = self.rep_mode
            response['field']['representation_mode_units'] = units
        else:
            response['field_representation_mode'] = self.rep_mode
            response['field_representation_mode_units'] = units

    def get_identifiers(self):
        return {
            'id': self.field_model.identifier,
            'distribution': self.field_model.distribution.identifier,
            'dataset': self.field_model.distribution.dataset.identifier
        }

    def title(self):
        return self.field_model.title

    def description(self):
        return self.metadata.get('description', '')

    def start_date(self):
        date_string = meta_keys.get(self.field_model, meta_keys.INDEX_START)
        if date_string is None:
            return None
        return iso8601.parse_date(date_string).date()
