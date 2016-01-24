import os
#import xlrd


def read_xls_worksheet(workbook_path, worksheet_id):
    rows = list()

    #workbook = xlrd.open_workbook(workbook_path)

    if type(worksheet_id) == str or type(worksheet_id) == unicode:
        worksheet = workbook.sheet_by_name(worksheet_id)
    elif type(worksheet_id) == int:
        worksheet = workbook.sheet_by_index(worksheet_id)

    for rowIndex in range(worksheet.nrows):
        row = worksheet.row(rowIndex)
        first_cell = row[0].value
        row_parsed = [cell.value for cell in row]
        
        rows.append(row_parsed)
    return rows


def get_datos_values(workspace, project, canal, tc_name, planilla):
    #path = os.path.join(
    #    workspace, project, 'src', 'test', 'integration', path, po_name)
    
    path = os.path.join(workspace, project, 'src', 'test', 'resources', planilla)

    rows = read_xls_worksheet(path, canal)

    fila_caso = []

    for row in rows:
        if tc_name[:-5] in row[0]:
            fila_caso = row

    print fila_caso
    valores = fila_caso[2].split(',')
    values_dict_list = []
    for valor in valores:
        values_dict_list.append({
            'name': valor.split('=')[0],
            'value': valor.split('=')[1]
            })

    return values_dict_list