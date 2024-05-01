import os
import subprocess
import re

def limpiar_IP(text):
    ip_string = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
    text = "\n".join(ip_string)
    return text

def Dupli_IP(text):
    ip_string = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
    unique_ips = list(set(ip_string))
    return "\n".join(unique_ips)

def format_text(text):
    os.system('cls')  
    return text.replace('.', '[.]').replace('@', '[@]').replace(' ', '')

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

def decision(text):
    aux = text.strip()
    if aux and aux[-1] == "l":
        return True
    return False

if __name__ == "__main__":
    while True:
        text = obtener_texto()
        aux_text = text
        
        if decision(text):
            text = limpiar_IP(text)
            aux_text = text
        dupli_text = Dupli_IP(text)
        text = format_text(text)

        if text.count('\n') < 10:
            print(text)
            print(aux_text)
            #print(dupli_text)
        else:
            with open("ip_Ofucadas.txt", "w") as arch1:
                arch1.write(text)

            with open("ip_Originales.txt", "w") as arch2:
                arch2.write(aux_text)

            with open("ip_Dupli.txt", "w") as arch3:
                arch3.write(dupli_text)

            subprocess.run(["start", "ip_Ofucadas.txt"], shell=True)
            subprocess.run(["start", "ip_Originales.txt"], shell=True)
            subprocess.run(["start", "ip_Dupli.txt"], shell=True)