import re
import sys
import csv
import time
import base64
import folium
import logging
import requests
import numpy as np
import pandas as pd
import unicodedata
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from requests.exceptions import ConnectionError, RequestException

# Polish wikipedia page on the dwarves of Wreslaw
wikiurl = requests.get('https://pl.wikipedia.org/wiki/Wroc%C5%82awskie_krasnale').text

soup = BeautifulSoup(wikiurl, 'lxml')


# Pick the right table in the article
TableImg = soup.find_all("table", class_="wikitable sortable")
neededT = 0
for ind,T in enumerate(TableImg): 
    if T.find("span", class_="coordinates inline plainlinks"): 
        neededT = ind

# Wrapper
Wrapper = TableImg[neededT].find_all("tr")

# Dwarves coordinates
# lat and lon have the coordinates both in degrees and sexagesimal
# we need to retrieve only the coordinates in degrees.
lat = []
lon = []
indexC = []
for i in range(len(Wrapper)): 
    try: 
        lat.append(Wrapper[i].find_all("span", class_='latitude')[-1].getText())
        lon.append(Wrapper[i].find_all("span", class_='longitude')[-1].getText())
    except IndexError: 
        indexC.append(i)        

lat = np.array([lat[i].replace(',','.') for i in range(len(lat))])
lon = np.array([lon[i].replace(',','.') for i in range(len(lat))])

Wrapper = np.delete(Wrapper, indexC)

#Wraplat = soup.find_all('span', class_="latitude")                                                                                                              
#Wraplong = soup.find_all('span', class_="longitude") 

# Get images and dimesions
img = []
imgW = []
imgH = []
index = []
for i in range(len(Wrapper)): 
    try: 
        img.append(Wrapper[i].find("a", class_='image').find("img")["src"]) 
        imgW.append(Wrapper[i].find("a", class_='image').find("img")["width"])
        imgH.append(Wrapper[i].find("a", class_='image').find("img")["height"])
    except AttributeError: 
        index.append(i)        


imgW = np.array(imgW).astype(np.int)
imgH = np.array(imgH).astype(np.int)
img = np.array([img[i].replace('{}px'.format(imgW[i]),'{}px'.format(imgW[i]*2)) for i in range(len(img))])


lat_deg = np.delete(lat,np.array(index)).astype(np.float)
lon_deg = np.delete(lon,np.array(index)).astype(np.float)


iframe = []
for i,Dw in enumerate(img):
    html = '<img src="https:{}" style="width:{}px;height:{}px;">'.format
    iframe.append(folium.IFrame(html(Dw,imgW[i]*2.2, imgH[i]*2.2), 
                  width=imgW[i]*2.2+20, height=imgH[i]*2.2+20))

popup = []
for i in range(len(iframe)):
    popup.append(folium.Popup(iframe[i], max_width=2650))

# The map:
folium_map = folium.Map(location=[51.1079, 17.0385],
                        zoom_start=12,
                        tiles= "Stamen Terrain") #"CartoDB dark_matter")

# The Dwarves:
for i in range(len(lat_deg)):
    folium.CircleMarker(location=[lat_deg[i], lon_deg[i]], radius=4, 
                        color='None', fill_color='#FF4633',fill_opacity=0.5,popup=popup[i]).add_to(folium_map)


folium_map.save("wroslaw.html")

#map.arcgisimage(service='ESRI_StreetMap_World_2D', xpixels = 12000, verbose= True)

# Get the dimentions of the thumbrl image
#imgW = np.array([WrapImg[i].find("img")["width"] for i in range(len(WrapImg))]).astype(np.int)
#imgH = np.array([WrapImg[i].find("img")["height"] for i in range(len(WrapImg))]).astype(np.int)


# If image is in .jpg format
#png = 'Papa_Krasnal_(Papa_Dwarf)_Wroclaw_dwarf_03.JPG'
#encoded = base64.b64encode(open(png, 'rb').read()).decode()
#html = '<img src="data:image/jpeg;base64,{}">'.format


