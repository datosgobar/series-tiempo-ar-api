from xlsxwriter import Workbook


class DumpWorksheet:
    MAX_ROWS_PER_SHEET = 1000000

    def __init__(self, workbook: Workbook, name: str):
        self.name = name
        self.workbook = workbook
        self.sheet_count = 0
        self.current_row = 0
        self.current_sheet = None

        self.init_worksheet()

    def write_row(self, row: list):
        self.current_sheet.write_row(self.current_row, 0, row)
        self.current_row += 1

        if self.current_row > self.MAX_ROWS_PER_SHEET:
            self.init_worksheet()

    def init_worksheet(self):
        self.sheet_count += 1
        sheet_name = f'{self.name}-{self.sheet_count}'
        self.current_sheet = self.workbook.add_worksheet(sheet_name)


class SingleWorksheet:
    def __init__(self, workbook: Workbook, name: str = None):
        self.current_row = 0
        self.current_sheet = workbook.add_worksheet(name)

    def write_row(self, row: list):
        self.current_sheet.write_row(self.current_row, 0, row)
        self.current_row += 1
