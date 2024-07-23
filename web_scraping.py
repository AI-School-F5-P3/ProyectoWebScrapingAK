import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv

#Variable con la dirección del sitio a hacer scraping
url = "https://quotes.toscrape.com/ "

#Realizar la petición con request y guardamos el contenido de la pagina
frases_to_scrape = requests.get(url)

#Parsear la información, mediante una instancia de beautiful soup
soup = BeautifulSoup(frases_to_scrape.text, 'lxml')
#Confirmar el tipo de dato de la "sopa" creada
type(soup)

#Imprimir con formato
print(soup.prettify())

#Apuntar a los artículos para extraerlos
frases = soup.find_all('div', attrs={'class':'quote'})
frases

# Lista temporal para guardar los frases
frases = []

#iterar los frases y obtener las variables
for frase in frases:
    contenido_frase = frase.find('span', attrs={'class':'text'}).get_text()[1:]
    # contenido_frase = frase.span.get('text')
    # about_frase = frase.img.get('src')
    # precio_frase = precio_frase_raw[1:]
    # divisa = precio_frase_raw[0]
    temp_row = [contenido_frase]
    frases.append(temp_row)
    print(temp_row)
frases_df = pd.DataFrame(frases,columns=['contenido_frase'])


# Inspeccionar el dataframe
frases_df.head(10)    

