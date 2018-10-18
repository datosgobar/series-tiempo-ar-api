from xlsxwriter import Workbook

from series_tiempo_ar_api.apps.dump.generator.xlsx.worksheet import DumpWorksheet, SingleWorksheet


class DumpWorkbook:
    frequency_col_name = 'indice_tiempo_frecuencia'

    def __init__(self, filename: str, header_row: list, split_by_frequency=False):
        self.workbook = Workbook(filename, {'constant_memory': True})
        self.split_by_frequency = split_by_frequency

        self.header_row = header_row
        for i, col_name in enumerate(self.header_row):
            if col_name == self.frequency_col_name:
                self.frequency_column_index = i
                break

        self.sheets = {}
        self.single_sheet = None

    def add_worksheet(self, sheet_name, frequency):
        self.sheets[frequency] = DumpWorksheet(self.workbook, sheet_name)
        self.sheets[frequency].write_row(self.header_row)

    def write_row(self, row):
        if self.split_by_frequency:
            frequency = row[self.frequency_column_index]
            if frequency not in self.sheets:
                self.init_worksheet(frequency)
            self.sheets[frequency].write_row(row)
            return

        if not self.single_sheet:
            self.single_sheet = SingleWorksheet(self.workbook)
            self.single_sheet.write_row(self.header_row)

        self.single_sheet.write_row(row)

    def close(self):
        self.workbook.close()

    def init_worksheet(self, frequency: str):
        names = {
            'R/P1Y': 'anual',
            'R/P6M': 'semestral',
            'R/P3M': 'trimestral',
            'R/P1M': 'mensual',
            'R/P1D': 'diaria',
        }
        sheet_name = names[frequency]
        self.add_worksheet(sheet_name, frequency)
