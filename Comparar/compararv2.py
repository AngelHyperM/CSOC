import pandas as pd
import requests
import json
import csv


#IP PATH
file_path = str(input('Coloque el nombre del archivo: '))
IP_CSV= pd.read_csv(file_path)
#AUXV = pd.read_csv(file_path)
ip = IP_CSV['IP'].tolist()

#BLACK PATH
IP_Blck = pd.read_csv("Blacklist.csv")
blck_ip = IP_Blck['IP'].tolist()

#Valores para consulta
url_reports = 'https://api.abuseipdb.com/api/v2/reports'
url = 'https://api.abuseipdb.com/api/v2/check'
API_KEY = '9b328ba222bfc432a36d0aff7a90ae9880f63dc56cbd4b7621551fb5dad1d3229383ccbc37f9e9b6'

block = False
pos = 0
#Columnas_Cotejo
csv_columns = ['ipAddress','Estatus']
#Columnas_Consulta
cons_columns = ['ipAddress','isPublic','ipVersion','isWhitelisted','abuseConfidenceScore','countryCode','usageType','isp','domain','hostnames','totalReports','numDistinctUsers','lastReportedAt','isTor','categories','description']
#Json_Cotejo
data = {}
data['data'] = []
#list_Consulta
cons = []

#Categorias de consulta
categorias = {1:['DNS Compromise','Altering DNS records resulting in improper redirection.'],
            2:['DNS Poisoning','Falsifying domain server cache (cache poisoning).'],
            3:['Fraud Orders' , 'Fraudulent orders'],
            4:['DDoS Attack' , 'Participating in distributed denial-of-service (usually part of botnet).'],
            5:['FTP Brute Force' , 'Trying to gain acces by an FTP Brute Force Attack'],
            6:['Ping of Death', 'Oversized IP packet.'],
            7:['Phishing','Phishing websites and/or email.'],
            8:['Fraud VoIP','Fraud VoIP'],
            9:['Open Proxy','Open proxy, open relay, or Tor exit node'],
            10:['Web Spam','Comment/forum spam, HTTP referer spam, or other CMS spam.'],
            11:['Email Spam','Spam email content, infected attachments, and phishing emails.'],
            12:['Blog Spam','CMS blog comment spam.'],
            13:['VPN IP','Conjunctive category.'],
            14:['Port Scan','Scanning for open ports and vulnerable services.'],
            15:['Hacking','Hacking'],
            16:['SQL Injection','Attempts at SQL injection'],
            17:['Spoofing','Email sender spoofing.'],
            18:['Brute-Force','Credential brute-force attacks on webpage logins and services like SSH, FTP, SIP, SMTP, RDP, etc.'],
            19:['Bad Web Bot','Webpage scraping (for email addresses, content, etc) and crawlers that do not honor robots.txt.'],
            20:['Exploited Host','Host is likely infected with malware and being used for other attacks or to host malicious content. The host owner may not be aware of the compromise'],
            21:['Web App Attack','Attempts to probe for or exploit installed web applications such as a CMS like WordPress/Drupal, e-commerce solutions, forum software, phpMyAdmin and various other software plugins/solutions.'],
            22:['SSH','Secure Shell (SSH) abuse.'],
            23:['IoT Targeted','Abuse was targeted at an "Internet of Things" type device.']
            }

#Headers de consulta
headers = {
    'Accept':'application/json',
    'Key':API_KEY
}
#Creación del archivo de salida
with open('results_IP.csv',"w",newline='') as filecsv:
    writer = csv.DictWriter(filecsv, fieldnames=csv_columns)
    writer.writeheader()

print("Generando el reporte...")
for i in ip:
    #print("La IP es:",i)
    for j in blck_ip:
        i = i.rstrip()
        i = i.lstrip()

        #Bloqueada
        if(i == j):
            estatus = "Bloqueada"
            block = True
            break
        pos+=1
    #No_Bloqueada
    if((pos == len(blck_ip)) and (block == False)): 
        estatus = "No bloqueada"
        cons.append(i)

    data['data'].append({
        'ipAddress' : i,
        'Estatus' : estatus
    })

    block = False
    pos = 0

#Escritura del nuevo archivo
with open ("results_IP.csv","a", newline='') as filecsv:
        writer = csv.DictWriter(filecsv, fieldnames=csv_columns)
        for element in data['data']:
            writer.writerow(element)

#Salida del programa 
if(len(cons) == 0):
    exit()

with open ("results_IP.csv","a", newline='') as filecsv:
        writer = csv.writer(filecsv)
        writer.writerow({'':''})
        writer.writerow({'RESULTADOS DE LA CONSULTA'})

with open ("results_IP.csv","a", newline='') as filecsv:
        writer = csv.DictWriter(filecsv, fieldnames=cons_columns)
        writer.writeheader()

#Ejecución de la consulta
for i in cons:
    querystring = {
    'ipAddress': i,
    'maxAgeInDays': '30',
    'page': '1',
    'perPage':'1'
    }
    
    parameters = {
        'ipAddress' : i,
        'maxAgeInDays': '90'
    }

    #Respuesta de los reportes
    r_response = requests.request(method='GET', url=url_reports, headers=headers, params=querystring)
    json_rData = json.loads(r_response.content)
    if(len(json_rData["data"]["results"]) == 0):
        json_ctg = "No report" 
        json_dsp = "La IP no se encuentra catalogada como maliciosa"

    else:
        value = json_rData["data"]["results"][0]["categories"][0]
        json_ctg = categorias[value][0]
        json_dsp = categorias[value][1]

    #Respuesta de la consulta de la IP
    response = requests.get(url = url, headers = headers, params= parameters)
    json_Data = json.loads(response.content)
    json_main = json_Data["data"]
    json_main['categories'] = json_ctg
    json_main['description'] = json_dsp
    with open ("results_IP.csv","a", newline='') as filecsv:
        writer = csv.DictWriter(filecsv, fieldnames=cons_columns)
        writer.writerow(json_main)