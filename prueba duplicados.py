import re

def format_text(text):
    unique_ips = text.split('\n')
    unique_ips = list(set(unique_ips))
    unique_ips = "\n".join(unique_ips)
    text = text.replace('.', '[.]').replace('@', '[@]').replace(' ', '')
    unique_ips = unique_ips.replace('.', '[.]').replace('@', '[@]').replace(' ', '')
    return text, unique_ips

def obtener_texto():
    print("Text:")
    text = ""
    while True:
        linea = input()
        if linea:
            text += linea + "\n"
        else:
            break
    #clearConsole()
    return text

def extraer_ipv6(texto):
    patron_ipv6 = r'([0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){7}|::[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,6}|[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){1,6}::(?:[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,1}){0,1})'
    ipv6_encontradas = re.findall(patron_ipv6, texto)
    return "\n".join(ipv6_encontradas)

import pandas as pd

def crear_Tabla_Reconocimiento(datos_excel, hoja, hoja_name):
    if hoja not in datos_excel:
        print(f"Error: La hoja '{hoja}' no existe en el documento.")
        return datos_excel  # Salimos de la función devolviendo el DataFrame original sin cambios
    
    datos = datos_excel[hoja][["Time", "Level", "Event ID", "Event", "Tag(s)", "Event Origin", "Target", "Action By", "Manager", "Description", "IP Source"]]
    
    resumen = datos.groupby(['Event', 'Target']).agg({
        'IP Source': lambda x: '\n'.join(set(x.dropna())),  # Concatenamos IPs únicas con salto de línea
        'Event ID': 'count'  # Contamos la cantidad de eventos por Target
    }).reset_index()

    resumen.columns = ['Event', 'Target', 'Source IP', 'Eventos']
    
    datos_excel[hoja_name] = resumen

    # Guardar todos los cambios en el archivo de excel
    with pd.ExcelWriter("Reporte AMS.xlsx", engine='xlsxwriter') as writer:
        for hoja in datos_excel.keys():
            datos_excel[hoja].to_excel(writer, sheet_name=hoja, index=False)
            workbook  = writer.book
            worksheet = writer.sheets[hoja]
            
            # Aplicar formato de ajuste de texto a la columna de 'Source IP'
            wrap_format = workbook.add_format({'text_wrap': True})
            worksheet.set_column('C:C', None, wrap_format)  # Asumiendo que 'Source IP' es la columna C

    print(f"Todas las hojas, incluyendo la 'Hoja Creada', han sido guardadas en 'Reporte AMS.xlsx'.")


def crear_Tabla_Reconocimiento(datos_excel, hoja, hoja_name):
    # Extraemos los datos relevantes de la hoja específica
    datos = datos_excel[hoja][["Time", "Level", "Event ID", "Event", "Tag(s)", "Event Origin", "Target", "Action By", "Manager", "Description", "IP Source"]]
    
    resumen = datos.groupby(['Event', 'Target']).agg({
        'IP Source': lambda x: '\n'.join(set(x.dropna())),  # Concatenamos IPs únicas, eliminando NaN
        'Event ID': 'count'  # Contamos la cantidad de eventos por Target
    }).reset_index()

    resumen.columns = ['Event', 'Target', 'Source IP', 'Eventos']
    
    datos_excel[hoja_name] = resumen

    print(f"Tabla reporte {hoja_name} creada.")

    return datos_excel

def crear_Tabla_Reconocimiento(datos_excel, hoja, hoja_name):#Mejo
    # Extraemos los datos relevantes de la hoja específica
    datos = datos_excel[hoja][["Time", "Level", "Event ID", "Event", "Tag(s)", "Event Origin", "Target", "Action By", "Manager", "Description", "IP Source"]]
    
    resumen = datos.groupby(['Event', 'Target', 'IP Source']).agg({
        'Event ID': 'count'  # Contamos la cantidad de eventos por IP Source y Target
    }).reset_index()

    resumen.columns = ['Event', 'Target', 'Source IP', 'Eventos']
    
    datos_excel[hoja_name] = resumen

    print(f"Tabla reporte {hoja_name} creada.")

    return datos_excel

texto = obtener_texto()
print(extraer_ipv6(texto))


def estilo_Reportes(df, writer, hoja):
    workbook = writer.book
    worksheet = writer.sheets[hoja]

    bold_blue_format = workbook.add_format({
        'bold': True,
        'bg_color': '#3498db',
        'font_color': '#000000',
        'border': 1        
    })
    merge_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })

    # Pre-cálculo de valores repetidos
    source_ip_index = df[df['Source IP'] != ''].index
    descripcion_index = df[df['Descripcion'] != ''].index
    informacion_index = df[df['Informacion'] != ''].index

    last_row_ip = df['Source IP'].replace('', pd.NA).dropna().index[-1] + 2
    last_row_index = df.index[-1]

    if last_row_ip > 1:
        range_to_merge = f"A2:A{last_row_ip}"
        worksheet.merge_range(range_to_merge, df.loc[0, 'Event'], merge_format)
        worksheet.merge_range(f"B2:B{last_row_ip}", df.loc[0, 'Level'], merge_format)

    # Escribir encabezados y ajustar columnas
    for col_num, value in enumerate(df.columns):
        worksheet.write(0, col_num, value, bold_blue_format)
        column_len = max(df[value].astype(str).map(len).max(), len(value)) + 2
        worksheet.set_column(col_num, col_num, column_len) 

    # Escribir valores en columnas D y E
    for index in source_ip_index:
        valores_IP = df.loc[index, "Source IP"]
        valores_Evento = df.loc[index, "Eventos"]
        worksheet.write(f'D{index + 2}', valores_IP, merge_format)
        worksheet.write(f'E{index + 2}', valores_Evento, merge_format)

    # Escribir valores en columnas H
    for index in informacion_index:
        valores_Info = df.loc[index, "Informacion"]
        worksheet.write(f'H{index + 2}', valores_Info, merge_format)

    # Fusionar celdas en columna C
    for i, index in enumerate(source_ip_index):
        value = df.loc[index, 'Target']
        last_index = source_ip_index[i + 1] - 1 if i + 1 < len(source_ip_index) else last_row_index
        if last_index != index:
            worksheet.merge_range(f'C{index + 2}:C{last_index + 2}', value, merge_format)
        else:
            if pd.notna(value):
                worksheet.write(f'C{index + 2}', value, merge_format)

    # Fusionar celdas en columna G
    for i, index in enumerate(descripcion_index):
        value = df.loc[index, 'Descripcion']
        if value == 'Detección:' or value == 'Eventos:':
            worksheet.write(f'G{index + 2}', value, merge_format)
            continue
        last_index = descripcion_index[i + 1] - 1 if i + 1 < len(descripcion_index) else last_row_index
        if last_index != index:
            worksheet.merge_range(f'G{index + 2}:G{last_index + 2}', value, merge_format)
        else:
            if pd.notna(value):
                worksheet.write(f'G{index + 2}', value, merge_format)

    # Escribir en última fila
    worksheet.merge_range(f"A{last_row_ip+1}:D{last_row_ip+1}", df.loc[last_row_ip - 1, 'Event'], bold_blue_format)
    worksheet.write(f'E{last_row_ip+1}', df.loc[last_row_ip - 1, 'Eventos'], bold_blue_format)
