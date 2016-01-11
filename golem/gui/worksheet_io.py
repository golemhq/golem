from werkzeug import secure_filename

from test_case_list import TestCaseList

import os

import xlrd

def process_import_file(file):

    rows = []

    filename = secure_filename(file.filename)

    extension = filename.split('.')[-1]

    base_dir = os.path.dirname(os.path.realpath(__file__))

    full_path = os.path.join(base_dir, 'temp', 'temp')

    file.save(full_path)

    if extension == 'xls':
        rows = read_xls_worksheet(full_path)

    return rows





def read_xls_worksheet(workbook_path):
    rows = list()

    workbook = xlrd.open_workbook(workbook_path)

    worksheet = workbook.sheet_by_index(0)

    for rowIndex in range(worksheet.nrows):
        row = worksheet.row(rowIndex)
        first_cell = row[0].value
        row_parsed = [cell.value for cell in row]
        
        rows.append(row_parsed)

    return rows

