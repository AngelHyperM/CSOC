import requests

def obtener_informacion_ip(ip):
    url = f"https://api.db-ip.com/v2/free/{ip}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Error al obtener información de la IP:", response.status_code)
        return None

# Ejemplo de uso
ip = "187.190.146.238"  # IP de ejemplo (puedes cambiarla)
informacion = obtener_informacion_ip(ip)
if informacion:
    print("Información de la IP:", informacion)
