import os
import subprocess as sp
import re
import requests
import pandas as pd #pip install pandas y pip install openpyxl

def data_Excel():
    nombre_archivo = input("Ingrese el nombre del archivo a leer: ")
    ruta_descargas = os.path.join(os.path.expanduser('~'), 'Downloads')
    ruta_archivo = os.path.join(ruta_descargas, nombre_archivo)

    try:
        datos_excel = pd.read_excel(ruta_archivo, sheet_name=None)
        for nombre_hoja, datos_hoja in datos_excel.items():
            print(f"Datos de la hoja '{nombre_hoja}':")
            print(datos_hoja)
        return datos_excel
    except FileNotFoundError:
        print("El archivo de Excel no se encontró en la carpeta de descargas.\nBuscando en el directorio actual...")
    
    ruta_script = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(ruta_script, nombre_archivo)

    try:
        datos_excel = pd.read_excel(nombre_archivo, sheet_name=None)
        for nombre_hoja, datos_hoja in datos_excel.items():
            print(f"Datos de la hoja '{nombre_hoja}':")
            print(datos_hoja)
        return datos_excel
    except FileNotFoundError:
        print("El archivo de Excel no se encontró en el directorio actual.")
        return None

def obtener_informacion_ip(ip):
    url = f"https://api.db-ip.com/v2/free/{ip}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error al obtener información de la IP:", response.status_code)
        return None

def limpiar_IP(text):
    ip_string = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
    text = "\n".join(ip_string)
    return text

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

    if aux and aux[-1] == "L":
        return 1
    elif aux == "AMS":
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
            text = limpiar_IP(text)
            aux_text = text
            text, sn_dupli, sn_dupli_fscr = format_text(text)
            print_ip(text, sn_dupli_fscr, aux_text)
        elif dec_Tree == 2:
            df = data_Excel()