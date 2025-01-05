import requests
import json
import pandas
import csv

filePath = str(input('Coloque el nombre del archivo: '))
IP_CSV = pandas.read_csv(filePath)

ip = IP_CSV['IP'].tolist()

API_KEY = '9b328ba222bfc432a36d0aff7a90ae9880f63dc56cbd4b7621551fb5dad1d3229383ccbc37f9e9b6'
url = 'https://api.abuseipdb.com/api/v2/check'

csvColumns = ['ipAddress','isPublic','ipVersion','isWhitelisted','abuseConfidenceScore','countryCode','usageType','isp','domain','hostnames','totalReports','numDistinctUsers','lastReportedAt','isTor']

headers = {
    'Accept':'application/json',
    'Key':API_KEY
}

with open('IP_results.csv',"w",newline='') as filecsv:
    writer = csv.DictWriter(filecsv, fieldnames=csvColumns)
    writer.writeheader()

for i in ip:
    parameters = {
        'ipAddress' : i,
        'maxAgeInDays': '90'
    }

    response = requests.get(url = url, headers = headers, params= parameters)
    json_Data = json.loads(response.content)
    json_main = json_Data["data"]
    with open ("IP_results.csv","a", newline='') as filecsv:
        writer = csv.DictWriter(filecsv, fieldnames=csvColumns)
        writer.writerow(json_main)