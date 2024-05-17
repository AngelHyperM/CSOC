import pandas as pd
import socket
import struct

def comparar_IPs(IPs):
    ruta = r"Blacklist.csv"
    ruta2 = r"Num_Rows.txt"
    df = pd.read_csv(ruta)
    num_rows_Black = df.shape[0]
    num_rows = open(ruta2, "r").read()
    num_rows = int(num_rows)

    if num_rows != num_rows_Black:
        file = open(ruta2, "w")
        file.write(str(num_rows_Black))
        file.close()
        merge_ip()
        print("El archivo Blacklist_Merge.csv se ha actualizado")

    ruta, ruta2, df, num_rows_Black, num_rows = None, None, None, None, None

    return busqueda_binaria(IPs)

def busqueda_binaria(IPs):
    ruta = r"Blacklist_Merge.csv"
    df = pd.read_csv(ruta)
    ip_Status = []
    
    for ip in IPs:
        ip_int = ip_to_int(ip)
        if ip_int is not None:
            # Búsqueda binaria
            left = 0
            right = df.shape[0] - 1
            while left <= right:
                mid = (left + right) // 2
                if df['ip_int'][mid] == ip_int:
                    ip_Status.append(f'La dirección IP {ip} está en la lista negra')
                    break
                elif df['ip_int'][mid] < ip_int:
                    left = mid + 1
                else:
                    right = mid - 1
        else:
            print(f'La dirección IP {ip} no está en la lista negra')

def ip_to_int(ip):
    try:
        return struct.unpack("!I", socket.inet_aton(ip))[0]
    except socket.error:
        return None  # Si hay una excepción al convertir la IP, devuelve None

def merge_ip():
    ruta = r"Blacklist.csv"

    # Lee el archivo CSV
    df = pd.read_csv(ruta, dtype={'IP': str})

    # Convierte las direcciones IP en enteros y crea una nueva columna
    df['ip_int'] = df['IP'].apply(lambda x: ip_to_int(x) if pd.notna(x) else None)
    df_sorted = df.dropna().sort_values('ip_int')  # Elimina filas con valores nulos antes de ordenar

    # Guarda el DataFrame con las direcciones IP ordenadas en un nuevo archivo CSV
    df_sorted.to_csv('Blacklist_Merge.csv', index=False)