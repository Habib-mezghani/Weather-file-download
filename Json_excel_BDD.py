import os
import pandas as pd
import re

filename = "master.geojson.txt"
with open(filename) as f:
    line = f.readlines()

# Show the file contents line by line.
Country_ID=[]
city=[]
ewp=[]
X=[]
Y=[]
i=8 # first line for the city and country name
j=9 # first line for the EPW file
k=15 # first line for the X_coord and Y_coord

while i<len(line):
    a=line[i].split(":")[1].split("\n")[0][2:-3].split(".")[0].split("_")

    if len(a)>2:
        a[1]=a[1]+" "+a[2]
        a.remove(a[2])

    if len(a)>1:
        Country_ID.append(a[0])
        city.append(a[1])
        ewp.append('https://'+line[j].split(":")[2][2:-29])
        X.append(float(line[k].split(":")[1].split("\n")[0][1:][1:-1].split(",")[0]))
        Y.append(float(line[k].split(":")[1].split("\n")[0][1:][1:-1].split(",")[1]))
    i=i+15 #next location
    j=j+15 #next location
    k=k+15 #next location

data_E_PLUS=pd.DataFrame({'Country_ID':Country_ID,'city':city, 'EWP':ewp,'coorX':X,'coordY':Y})

country_data=pd.read_csv('country-and-continent-codes-list-csv_csv.csv',sep=',')[['Continent_Name','Country_Name','Three_Letter_Country_Code']]
country_data.columns=['Continent_Name','Country_Name','Country_ID']

result = pd.merge(data_E_PLUS, country_data, on=['Country_ID'])
result.to_csv('EWP_data_base.csv', sep=';')