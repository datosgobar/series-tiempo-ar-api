#! coding: utf-8

from series_tiempo_ar_api.apps.api.query import constants


class SeriesIdsParser:

    def __init__(self, series_rep_modes, series_ids):
        self.series_rep_modes = series_rep_modes
        self.series_ids = series_ids

    def parse(self, header):
        new_series_ids = self.series_ids
        rep_modes = constants.REP_MODE_SELECTOR[header]
        joiner = constants.REP_MODE_JOINERS[header]

        for rep_mode in self.series_rep_modes:
            if rep_mode != constants.VALUE:
                prefix = new_series_ids[self.series_rep_modes.index(rep_mode)]
                suffix = rep_modes[rep_mode] if rep_modes else rep_mode
                new_series_ids[self.series_rep_modes.index(rep_mode)] = f'{prefix}{joiner}{suffix}'
        return new_series_ids
