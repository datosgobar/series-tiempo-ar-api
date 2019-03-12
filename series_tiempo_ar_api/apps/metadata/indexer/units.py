import json

from series_tiempo_ar_api.apps.metadata.models import SeriesUnits
from series_tiempo_ar_api.libs.datajsonar_repositories.series_repository import SeriesRepository


def update_units():
    series_units = get_all_available_series_units()
    current_units = set(SeriesUnits.objects.values_list('name', flat=True))
    new_units = series_units - current_units
    SeriesUnits.objects.bulk_create([SeriesUnits(name=units) for units in new_units])


def get_all_available_series_units() -> set:
    series_metadata = SeriesRepository.get_available_series() \
        .values_list('metadata', flat=True)

    catalog_units = set()
    for metadata in series_metadata:
        metadata = json.loads(metadata)
        units = metadata.get('units')
        if units:
            catalog_units.add(units)
    return catalog_units
