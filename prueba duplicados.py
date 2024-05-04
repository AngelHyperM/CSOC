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

texto = obtener_texto()
print(extraer_ipv6(texto))
