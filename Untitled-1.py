import requests
import json
import pandas as pd
import re
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

def obtener_texto():
    print("Text:")
    text = ""
    while True:
        linea = input()
        if linea:
            text += linea + "\n"
        else:
            break
    return text

def limpiar_IPV4(text):
    ip_string = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
    text = ",".join(ip_string)
    return text if text else None

def filtrar_IPs(text):
    ips = text.split(',')
    ips = [ip.strip() for ip in ips]
    subredes_privadas = ['192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.', '127.']

    ips = [ip for ip in ips if not any(ip.startswith(subred) for subred in subredes_privadas)]
    
    return ','.join(ips)

def main():
    text = obtener_texto()
    ips = limpiar_IPV4(text)
    ips = filtrar_IPs(text)
    ips = ips.split(',')

    print(ips)
    """data = []
    for ip in ips:
        data.append(informacion_ip(ip))
    df = pd.DataFrame(data)
    df.to_csv('ip_info.csv', index=False)"""

main()