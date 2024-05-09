import os
import subprocess as sp
import re
import requests # pip install requests
import pandas as pd # pip install pandas
#Libreria adicional xlsxwriter pip install xlsxwriter
#Libreria adicional openpyxl pip install openpyxl
#pip install openpyxl xlsxwriter pandas requests

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

    if 'Source IP' in df.columns:
        last_row_ip = df['Source IP'].replace('', pd.NA).dropna().index[-1] + 2
        if last_row_ip > 1:  # Verifica que haya al menos un dato no vacío después de los encabezados
            range_to_merge = f"A2:A{last_row_ip}"
            worksheet.merge_range(range_to_merge, df.loc[0, 'Event'], merge_format)
            worksheet.merge_range(f"B2:B{last_row_ip}", df.loc[0, 'Level'], merge_format)

    for col_num, value in enumerate(df.columns):
        worksheet.write(0, col_num, value, bold_blue_format)
        column_len = max(df[value].astype(str).map(len).max(), len(value)) + 2
        worksheet.set_column(col_num, col_num, column_len) 
    
    non_empty_rows = df[df['Target'] != ''].index
    for i, index in enumerate(non_empty_rows):
        # Obtiene el valor de la celda
        value = df.loc[index, 'Target']
        
        # Encuentra el último índice de la misma fila con el mismo valor
        last_index = non_empty_rows[non_empty_rows > index].min() - 1 if index != non_empty_rows[-1] else df.index[-1]
        
        # Fusiona las celdas        
        if last_index != index:
            try:
                worksheet.merge_range(f'C{index + 2}:C{last_index + 2}', value, merge_format)
            except:
                pass  # Ignora la fusión si no es posible
        else:
            # Escribir el valor sin fusionar las celdas
            if pd.notna(value):
                worksheet.write(f'C{index + 2}', value, merge_format)
    worksheet.merge_range(f"A{last_row_ip+1}:D{last_row_ip+1}", df.loc[last_row_ip - 1, 'Event'], bold_blue_format)

    non_empty_rows = df[df['Descripcion'] != ''].index
    for i, index in enumerate(non_empty_rows):
        value = df.loc[index, 'Descripcion']

        if value == 'Detección:' or value == 'Eventos:':
            worksheet.write(f'G{index + 2}', value, merge_format)
            continue
        
        last_index = non_empty_rows[non_empty_rows > index].min() - 1 if index != non_empty_rows[-1] else df.index[-1]
    
        if last_index != index:
            try:
                worksheet.merge_range(f'G{index + 2}:G{last_index + 2}', value, merge_format)
            except:
                pass 
        else:
            if pd.notna(value):
                worksheet.write(f'G{index + 2}', value, merge_format)
    


def crear_Tabla_Reconocimiento(datos_excel, hoja, hoja_name):
    # Extraemos los datos relevantes de la hoja específica
    datos = datos_excel[hoja][["Time", "Level", "Event ID", "Event", "Tag(s)", "Event Origin", "Target", "Action By", "Manager", "Description", "IP Source"]]
    
    resumen = datos.groupby(['Event', 'Level', 'Target', 'IP Source']).agg({
        'Event ID': 'count'  # Contamos la cantidad de eventos por IP Source y Target
    }).reset_index()

    resumen.columns = ['Event', 'Level', 'Target', 'Source IP', 'Eventos']
    
    name_target_first = resumen['Target'][0]
    name_event_first = resumen['Event'][0]
    name_level_first = resumen['Level'][0]
    for i in range(1, len(resumen['Target'])):
        if name_target_first == resumen['Target'][i]:
            resumen.loc[i, 'Target'] = ""
        else:
            name_target_first = resumen['Target'][i]
        resumen.loc[i, 'Event'] = ""
        resumen.loc[i, 'Level'] = ""

    resumen.loc[0, 'Event'] = name_event_first
    resumen.loc[0, 'Level'] = name_level_first 
    resumen.loc[len(resumen), 'Event'] = "Total de Eventos"
    resumen.loc[len(resumen)-1, 'Eventos'] = resumen['Eventos'].sum()

    unicos_Target = resumen['Target'].drop_duplicates().reset_index(drop=True)
    unicos_Target = unicos_Target.dropna().reset_index(drop=True)
    unicos_Target = unicos_Target[unicos_Target != ''].reset_index(drop=True)
    unicos_IP = resumen['Source IP'].drop_duplicates().reset_index(drop=True)
    unicos_IP = unicos_IP.dropna().reset_index(drop=True)

    tam = len(unicos_Target)
    tam2 = len(unicos_IP)

    resumen.insert(loc=resumen.columns.get_loc('Eventos') + 1, column='        ', value='')
    resumen.insert(loc=resumen.columns.get_loc('Eventos') + 2, column='Descripcion', value='')
    resumen.insert(loc=resumen.columns.get_loc('Descripcion') + 1, column='Informacion', value='')

    resumen.loc[0, 'Descripcion'] = "Equipos:"
    resumen.loc[tam, 'Descripcion'] = "Source IP:"

    for i in range(tam2+tam):
        if i < tam:
            resumen.loc[i, 'Informacion'] = unicos_Target[i]
        else:
            resumen.loc[i, 'Informacion'] = unicos_IP[i-tam]

    resumen.loc[i, 'Descripcion'] = 'Detección:'
    resumen.loc[i, 'Informacion'] = name_event_first
    resumen.loc[i+1, 'Descripcion'] = 'Eventos:'
    resumen.loc[i+1, 'Informacion'] = (resumen['Eventos'].sum())/2
    
    datos_excel[hoja_name] = resumen
    print(f"Tabla {hoja_name} creada.")

    return datos_excel

def IP_Excel_Reconocimiento(datos_excel, hoja):
    ips = []
    for description in datos_excel[hoja]["Description"]:
        ip = None
        ipv4_ips = limpiar_IPV4(description)
        ipv6_ips = limpiar_IPV6(description)
        if ipv4_ips:
            ip = ipv4_ips.split('\n')[0] if ipv4_ips else None
        if not ip and ipv6_ips:
            ip = ipv6_ips.split('\n')[0] if ipv6_ips else None
        ips.append(ip)

    datos_excel[hoja]["IP Source"] = ips
    return datos_excel, ips

def encontrar_Reportes(datos_excel):
    computer_OS, network_Scan, SYNFIN_Scan = None, None, None  # Inicializa todas las variables a None

    hojas = list(datos_excel.keys())
    for hoja in hojas:
        if "Event" in datos_excel[hoja].columns:
            if "Reconnaissance Detected: Computer OS Fingerprint Probe" in datos_excel[hoja]["Event"].values:
                computer_OS = hoja
            if "Reconnaissance Detected: Network or Port Scan" in datos_excel[hoja]["Event"].values:
                network_Scan = hoja
            if "Reconnaissance Detected: TCP SYNFIN Scan" in datos_excel[hoja]["Event"].values:
                SYNFIN_Scan = hoja

    return computer_OS, network_Scan, SYNFIN_Scan

def data_Excel():
    nombre_archivo = input("Ingrese el nombre del archivo a leer: ")
    ruta_descargas = os.path.join(os.path.expanduser('~'), 'Downloads')
    ruta_archivo = os.path.join(ruta_descargas, nombre_archivo)

    #Ver extension del archivo
    if nombre_archivo.endswith('.xlsx'):
        try:
            datos_excel = pd.read_excel(ruta_archivo, sheet_name=None)
            return datos_excel
        except FileNotFoundError:
            print("El archivo de Excel no se encontró en la carpeta de descargas.\nBuscando en el directorio actual...")
        
        ruta_script = os.path.dirname(os.path.abspath(__file__))
        ruta_archivo = os.path.join(ruta_script, nombre_archivo)

        try:
            datos_excel = pd.read_excel(nombre_archivo, sheet_name=None)
            return datos_excel
        except FileNotFoundError:
            print("El archivo de Excel no se encontró en el directorio actual.\nBuscando en el escritorio...")
        
        ruta_escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
        ruta_archivo = os.path.join(ruta_escritorio, nombre_archivo) 

        try:
            datos_excel = pd.read_excel(ruta_archivo, sheet_name=None)
            return datos_excel
        except FileNotFoundError:
            print("El archivo de Excel no se encontró en el escritorio ni ruta actual del script ni en descargas.")
            print("Por favor, mueva el archivo a una de las rutas mencionadas e intente nuevamente.")
            return None
        
    elif nombre_archivo.endswith('.csv'):
        try:
            datos_excel = pd.read_csv(ruta_archivo, sheet_name=None)
            return datos_excel
        except FileNotFoundError:
            print("El archivo CSV no se encontró en la carpeta de descargas.\nBuscando en el directorio actual...")
        
        ruta_script = os.path.dirname(os.path.abspath(__file__))
        ruta_archivo = os.path.join(ruta_script, nombre_archivo)

        try:
            datos_excel = pd.read_csv(nombre_archivo, sheet_name=None)
            return datos_excel
        except FileNotFoundError:
            print("El archivo CSV no se encontró en el directorio actual.\nBuscando en el escritorio...")
        
        ruta_escritorio = os.path.join(os.path.expanduser('~'), 'Desktop')
        ruta_archivo = os.path.join(ruta_escritorio, nombre_archivo) 

        try:
            datos_excel = pd.read_csv(ruta_archivo, sheet_name=None)
            return datos_excel
        except FileNotFoundError:
            print("El archivo CSV no se encontró en el escritorio ni ruta actual del script ni en descargas.")
            print("Por favor, mueva el archivo a una de las rutas mencionadas e intente nuevamente.")
            return None
    else:
        print("El archivo no es un archivo de Excel o CSV.")
        return None

def informacion_ip(ipAddress):
    api_key_dbip = "f968cfdb294b70521393fadf0827d111859b5684"
    propertyName = "countryName,city,latitude,longitude,isp,organization,asNumber,asName"
    url = f"http://api.db-ip.com/v2/{api_key_dbip}/as/{ipAddress}/{propertyName}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error al obtener información de la IP:", response.status_code)
        return None
    
def eliminar_duplicados(text):
    unique_ips = list(set(text))
    ips_text = '\n'.join(str(ip) for ip in unique_ips)
    return ips_text

def limpiar_IPV6(text):
    patron_ipv6 = r'([0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){7}|::[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,6}|[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){1,6}::(?:[0-9a-fA-F]{1,4}(?::[0-9a-fA-F]{1,4}){0,1}){0,1})'
    ip_string = re.findall(patron_ipv6, text)
    text = "\n".join(ip_string)
    return text if text else None

def limpiar_IPV4(text):
    ip_string = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
    text = "\n".join(ip_string)
    return text if text else None

def clearConsole():
    command = "clear" if os.name in ("linux") else "cls"
    os.system(command)

def format_text(text):
    sn_dupli = text.split('\n')
    sn_dupli = list(set(sn_dupli))
    sn_dupli = "\n".join(sn_dupli)
    text = text.replace('.', '[.]').replace('@', '[@]').replace(' ', '')
    sn_dupli_fscr = sn_dupli.replace('.', '[.]').replace('@', '[@]').replace(' ', '')
    return text, sn_dupli, sn_dupli_fscr

def obtener_texto():
    print("Text:")
    text = ""
    while True:
        linea = input()
        if linea:
            text += linea + "\n"
        else:
            break
    clearConsole()
    return text

def decision(text):
    aux = text.strip()
    aux = aux.upper()

    if aux == "LIMPIAR":
        return 1
    elif aux == "PUERTOS":
        return 2
    return 0

def print_ip(text, sn_dupli_fscr, sn_dupli, aux_text):
    if text.count('\n') <= 10:
        print("Datos Ofuscados:\n")
        print(text)
        print("_____________________________________________________________________________________________________________________\n")
        print("Datos Sin Duplicar Ofuscados:\n")
        print(sn_dupli_fscr)
        print("\n_____________________________________________________________________________________________________________________\n")
        print("Datos Sin Duplicar y Sin Ofuscar:\n")
        print(sn_dupli)
        print("\n_____________________________________________________________________________________________________________________\n")
        print("Datos Originales:\n")
        print(aux_text)
        print("_____________________________________________________________________________________________________________________\n")

    else:
        with open("Datos_Script.txt", "w") as arch1:
            arch1.write("Datos Ofuscados:\n")
            arch1.write(text)
            arch1.write("_____________________________________________________________________________________________________________________\n")
            arch1.write("Datos Sin Duplicar Ofuscados:\n")
            arch1.write(sn_dupli_fscr)
            arch1.write("\n_____________________________________________________________________________________________________________________\n")
            arch1.write("Datos Sin Duplicar Sin Ofuscar:\n")
            arch1.write(sn_dupli)
            arch1.write("\n_____________________________________________________________________________________________________________________\n")
            arch1.write("Datos Originales:\n")
            arch1.write(aux_text)
            arch1.write("_____________________________________________________________________________________________________________________\n")

        sp.run(["start", "Datos_Script.txt"], shell=True)

if __name__ == "__main__":
    while True:
        text = obtener_texto()
        aux_text = text
        dec_Tree = decision(text)

        if dec_Tree == 0:
            text, sn_dupli, sn_dupli_fscr = format_text(text)
            print_ip(text, sn_dupli_fscr, sn_dupli, aux_text)
            text, sn_dupli, sn_dupli_fscr, aux_text = None, None, None, None

        elif dec_Tree == 1:
            print("Limpieza de IP's")
            text = obtener_texto()
            text = limpiar_IPV4(text)
            aux_text = text
            text, sn_dupli, sn_dupli_fscr = format_text(text)
            print_ip(text, sn_dupli_fscr, sn_dupli, aux_text)
            text, sn_dupli, sn_dupli_fscr, aux_text = None, None, None, None

        elif dec_Tree == 2:
            print("Reconocimiento de Puertos")
            df = data_Excel()

            if not df:
                continue
            
            print("Libro de Excel Cargado.")
            computer_OS, network_Scan, SYNFIN_Scan = encontrar_Reportes(df)

            if computer_OS:
                df, ip_comp = IP_Excel_Reconocimiento(df, computer_OS)
                df = crear_Tabla_Reconocimiento(df, computer_OS, "Reporte Computer OS")
            if network_Scan:
                df, ip_netw = IP_Excel_Reconocimiento(df, network_Scan)
                df = crear_Tabla_Reconocimiento(df, network_Scan, "Reporte Network")
            if SYNFIN_Scan:
                df, ip_synf = IP_Excel_Reconocimiento(df, SYNFIN_Scan)
                df = crear_Tabla_Reconocimiento(df, SYNFIN_Scan, "Reporte SYNFIN")

            ips_Total = ip_comp + ip_netw + ip_synf
            ips_Total = eliminar_duplicados(ips_Total).split('\n')

            #
            
            with pd.ExcelWriter("Reporte_AMS.xlsx", engine='xlsxwriter') as writer:
                for hoja in df.keys():
                    df[hoja].to_excel(writer, sheet_name=hoja, index=False)

                for hoja in df.keys():
                    if hoja in ["Reporte Computer OS", "Reporte Network", "Reporte SYNFIN"]:
                        estilo_Reportes(df[hoja], writer, hoja) 
                    
            if os.name == 'nt':  # Windows
                os.system(f'start "" "Reporte_AMS.xlsx"')
            elif os.name == 'posix':  # Linux o macOS
                os.system(f'open "Reporte_AMS.xlsx"')
            else:
                print("No se puede abrir el archivo automáticamente en este sistema operativo.")
            #sp.run(["start", "IPs.txt"], shell=True)

            #Variables a none
            computer_OS, network_Scan, SYNFIN_Scan = None, None, None
            df, ips_Total, ip_comp, ip_netw, ip_synf = None, None, None, None, None