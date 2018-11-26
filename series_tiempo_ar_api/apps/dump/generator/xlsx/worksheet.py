from xlsxwriter import Workbook


class DumpWorksheet:
    MAX_ROWS_PER_SHEET = 1000000

    def __init__(self, workbook: Workbook, header_row: list, name: str, formats: dict):
        self.name = name
        self.header_row = header_row
        self.workbook = workbook
        self.sheet_count = 0
        self.current_row = 0
        self.current_sheet = None
        self.formats = formats
        self.init_worksheet()

    def write_row(self, row: list, cell_format=None):
        for j, val in enumerate(row):
            val = self.formats[j](val) if j in self.formats else val
            self.current_sheet.write(self.current_row, j, val, cell_format)

        self.current_row += 1

        if self.current_row > self.MAX_ROWS_PER_SHEET:
            self.init_worksheet()

    def write_header_row(self, cell_format=None):
        self.current_sheet.write_row(self.current_row, 0, self.header_row, cell_format)
        self.current_row += 1

    def init_worksheet(self):
        self.sheet_count += 1
        sheet_name = f'{self.name}-{self.sheet_count}'
        self.current_sheet = self.workbook.add_worksheet(sheet_name)
        self.current_row = 0
        self.write_header_row(self.workbook.add_format({'bold': True}))


class SingleWorksheet:
    def __init__(self, workbook: Workbook, formats: dict, name: str = None):
        self.current_row = 0
        self.current_sheet = workbook.add_worksheet(name)
        self.formats = formats

    def write_row(self, row: list, cell_format=None):
        for j, val in enumerate(row):
            val = self.formats[j](val) if j in self.formats else val
            self.current_sheet.write(self.current_row, j, val, cell_format)

        self.current_row += 1

    def write_header_row(self, row: list, cell_format=None):
        self.current_sheet.write_row(self.current_row, 0, row, cell_format)
        self.current_row += 1
