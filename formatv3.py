import os
import subprocess as sp
import re
import requests # pip install requests
import pandas as pd # pip install pandas
#Librerias adiciones openpyxl pip install xlsxwriter

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

def informacion_ip(ips):
    api_key_dbip = "f968cfdb294b70521393fadf0827d111859b5684"
    url = f"https://api.db-ip.com/v2/{api_key_dbip}/{ips}"
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
    unique_ips = text.split('\n')
    unique_ips = list(set(unique_ips))
    unique_ips = "\n".join(unique_ips)
    text = text.replace('.', '[.]').replace('@', '[@]').replace(' ', '')
    unique_ips_fscr = unique_ips.replace('.', '[.]').replace('@', '[@]').replace(' ', '')
    return text, unique_ips, unique_ips_fscr

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
    elif aux == "RECONOCIMIENTO":
        return 2
    return 0

def print_ip(text, sn_dupli_fscr, aux_text):
    if text.count('\n') <= 8:
        print("IP's Sin Duplicar Ofuscadas:\n")
        print(text)
        print("\n_____________________________________________________________________________________________________________________\n\n")
        print("IP's Originales Sin Duplicar:\n")
        print(sn_dupli_fscr)
        print("\n_____________________________________________________________________________________________________________________\n\n")
        print("IP's Originales:\n")
        print(aux_text)
    else:
        with open("Datos Script.txt", "w") as arch1:
            arch1.write("Datos Ofuscados:\n")
            arch1.write(text)
            arch1.write("\n_____________________________________________________________________________________________________________________\n\n")
            arch1.write("Datos Sin Duplicar Ofuscados:\n")
            arch1.write(sn_dupli_fscr)
            arch1.write("\n_____________________________________________________________________________________________________________________\n\n")
            arch1.write("Datos Originales:\n")
            arch1.write(aux_text)
            arch1.write("\n_____________________________________________________________________________________________________________________\n\n")

        sp.run(["start", "IPs.txt"], shell=True)

if __name__ == "__main__":
    while True:
        text = obtener_texto()
        aux_text = text
        dec_Tree = decision(text)

        if dec_Tree == 0:
            text, sn_dupli, sn_dupli_fscr = format_text(text)
            print_ip(text, sn_dupli_fscr, aux_text)
        elif dec_Tree == 1:
            print("Limpieza de IP's")
            text = obtener_texto()
            text = limpiar_IPV4(text)
            aux_text = text
            text, sn_dupli, sn_dupli_fscr = format_text(text)
            print_ip(text, sn_dupli_fscr, aux_text)
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
            ips_Total = eliminar_duplicados(ips_Total)
            with open("IPs.txt", "w") as arch1:
                arch1.write(ips_Total)
            #Se guardaran todos los cambios en el archivo de excel
            with pd.ExcelWriter("Reporte AMS.xlsx", engine='xlsxwriter') as writer:
                for hoja in df.keys():
                    df[hoja].to_excel(writer, sheet_name=hoja, index=False)
                    workbook  = writer.book
                    worksheet = writer.sheets[hoja]
                    
                    # Aplicar formato de ajuste de texto a la columna de 'Source IP'
                    wrap_format = workbook.add_format({'text_wrap': True})
                    worksheet.set_column('C:C', None, wrap_format)  # Asumiendo que 'Source IP' es la columna C
