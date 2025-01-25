import os
import subprocess as sp
import re
import requests
import pandas as pd
from Code.Blacklist import compararv3 as cmpv3
#pip install openpyxl xlsxwriter pandas requests //Librerias adicionales    

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
    worksheet.write(f'E{last_row_ip+1}', df.loc[last_row_ip - 1, 'Eventos'], bold_blue_format)

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

    for index in df[df['Source IP'] != ''].index:
        try:
            valores_IP = df.loc[index, "Source IP"]
            valores_Evento = df.loc[index, "Eventos"]
            worksheet.write(f'D{index + 2}', valores_IP, merge_format)
            worksheet.write(f'E{index + 2}', valores_Evento, merge_format)
        except:
            continue

    for index in df[df['Informacion'] != ''].index:
        try:
            valores_Info = df.loc[index, "Informacion"]
            worksheet.write(f'H{index + 2}', valores_Info, merge_format)
        except:
            continue

def crear_Tabla_IPs(datos_excel, ips_Total_Data, ips_Total):
    ips_Total = ips_Total.split(',')
    ips_Total_Data = pd.DataFrame(ips_Total_Data).T
    # Crear una hoja nueva en el archivo de Excel
    datos_excel["Reporte IPs"] = pd.DataFrame(columns='')
    
    # Iterar sobre las columnas de ips_Total_Data y agregar cada columna al DataFrame datos_excel["Reporte IPs"]
    for column_name, column_data in ips_Total_Data.items():
        # Agregar la columna al DataFrame datos_excel["Reporte IPs"]
        datos_excel["Reporte IPs"][column_name] = column_data

    datos_excel["Reporte IPs"] = datos_excel["Reporte IPs"][['', 'countryName', 'stateProv', 'district', 'isp', 'threatLevel', 'threatDetails', 'isCrawler', 'isProxy']].reset_index(drop=True)
    #datos_excel["Reporte IPs"]["ipAddress"] = ips_Total_Data.keys()
    #print("Tabla Reporte IPs creada.")
    print(ips_Total_Data.keys())

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

    resumen.loc[i+1, 'Descripcion'] = 'Detección:'
    resumen.loc[i+1, 'Informacion'] = name_event_first
    resumen.loc[i+2, 'Descripcion'] = 'Eventos:'
    resumen.loc[i+2, 'Informacion'] = (resumen['Eventos'].sum())/2
    
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

    # Ver extensión del archivo
    if nombre_archivo.endswith('.xlsx'):
        try:
            datos_excel = pd.read_excel(ruta_archivo, sheet_name=None)
            return datos_excel
        except FileNotFoundError:
            print("El archivo de Excel no se encontró en la carpeta de descargas.\nBuscando en otras ubicaciones...")
        
    elif nombre_archivo.endswith('.csv'):
        try:
            datos_csv = pd.read_csv(ruta_archivo)
            return {"Hoja1": datos_csv}  # Devuelve un diccionario con una hoja llamada "Hoja1" para mantener la consistencia
        except FileNotFoundError:
            print("El archivo CSV no se encontró en la carpeta de descargas.\nBuscando en otras ubicaciones...")

    # Si no es un archivo Excel ni un archivo CSV o no se encontró en las ubicaciones habituales, se realiza una búsqueda más exhaustiva.
    rutas_busqueda = [os.path.dirname(os.path.abspath(__file__)), os.path.join(os.path.expanduser('~'), 'Desktop')]
    for ruta in rutas_busqueda:
        ruta_archivo = os.path.join(ruta, nombre_archivo)
        if nombre_archivo.endswith('.xlsx'):
            try:
                datos_excel = pd.read_excel(ruta_archivo, sheet_name=None)
                return datos_excel
            except FileNotFoundError:
                print(f"El archivo de Excel no se encontró en {ruta}.")
        elif nombre_archivo.endswith('.csv'):
            try:
                datos_csv = pd.read_csv(ruta_archivo)
                return {"Hoja1": datos_csv}  # Devuelve un diccionario con una hoja llamada "Hoja1" para mantener la consistencia
            except FileNotFoundError:
                print(f"El archivo CSV no se encontró en {ruta}.")

    print(f"No se encontró el archivo {nombre_archivo} en las ubicaciones habituales.")
    print("Por favor, mueva el archivo a una de las rutas mencionadas e intente nuevamente.")
    return None

def IPs_Bloqueadas(text):
    print("Hola")

def filtrar_IPs(text):
    ips = text.split(',')
    ips = [ip.strip() for ip in ips]
    subredes_privadas = ['192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.', '127.']

    ips = [ip for ip in ips if not any(ip.startswith(subred) for subred in subredes_privadas)]
    
    return ','.join(ips)

def informacion_ip(ipAddress):
    api_key_dbip = "f968cfdb294b70521393fadf0827d111859b5684"
    url = f"http://api.db-ip.com/v2/{api_key_dbip}/{ipAddress}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("Información de las IP's obtenida.")
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

            if df is None:
                continue

            print("Libro de Excel Cargado.")
            computer_OS, network_Scan, SYNFIN_Scan = encontrar_Reportes(df)

            ip_comp, ip_netw, ip_synf = [], [], []
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
            ips_Total = filtrar_IPs(','.join(ips_Total))
            #ips_Bloqueadas, ips_NO_Bloqueadas = cmpv3.comparar_IPs(ips_Total)
            #print("IP's Bloqueadas:", ips_Bloqueadas)
            #print("IP's NO Bloqueadas:", ips_NO_Bloqueadas)
            #ips_Total_Data = informacion_ip(ips_Total)
            ips_Total_Data = None

            if ips_Total_Data is not None:
                crear_Tabla_IPs(df, ips_Total_Data, ips_Total)

            print("Aplicando Estilo...")
            with pd.ExcelWriter("Reporte_Puertos.xlsx", engine='xlsxwriter') as writer:
                for hoja in df.keys():
                    df[hoja].to_excel(writer, sheet_name=hoja, index=False)
                for hoja in writer.sheets:
                    if hoja == "Reporte Computer OS" or hoja == "Reporte Network" or hoja == "Reporte SYNFIN":
                        estilo_Reportes(df[hoja], writer, hoja)

            if os.name == 'nt':  # Windows
                os.system(f'start "" "Reporte_Puertos.xlsx"')
            elif os.name == 'posix':  # Linux o macOS
                os.system(f'open "Reporte_AMS.xlsx"')
            else:
                print("No se puede abrir el archivo automáticamente en este sistema operativo.")
            #sp.run(["start", "IPs.txt"], shell=True)

            #Variables a none
            computer_OS, network_Scan, SYNFIN_Scan = None, None, None
            df, ips_Total, ip_comp, ip_netw, ip_synf = None, None, None, None, None