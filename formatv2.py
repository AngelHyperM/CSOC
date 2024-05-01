import os
import subprocess as sp
import re
import pandas as pd
import requests
import json
import sys
#from Comparar import compararv2 as cv2

def limpiar_IP(text):
    ip_string = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
    text = "\n".join(ip_string)
    return text

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

def save_text(text):
    arch = open("text.txt", "w")
    arch.write(text)
    arch.close()

def decision(text):
    aux = text.strip()
    if aux[-1] == "l":
        return True
    return False

if __name__ == "__main__":
    while True:
        text = obtener_texto()
        aux_text = text
        if decision(text):
            text = limpiar_IP(text)
            aux_text = limpiar_IP(aux_text)
        text = format_text(text)

        if text.count('\n') < 10:
            print(text)
            print(aux_text)
        else:
            save_text(text)
            save_text(aux_text)
            sp.run(["start", "text.txt"], shell=True)
            sp.run(["start", "ip.txt"], shell=True)