import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv

#Variable con la dirección del sitio a hacer scraping
url = "https://quotes.toscrape.com/"

try:
    # Realizar la petición con request y guardar el contenido de la pagina
    frases_to_scrape = requests.get(url)
    frases_to_scrape.raise_for_status()  # Para manejar errores HTTP
except requests.exceptions.RequestException as e:
    print(f"Error al realizar la petición: {e}")
    exit()

#Parsear la información, mediante una instancia de beautiful soup
soup = BeautifulSoup(frases_to_scrape.text, 'lxml')
#Confirmar el tipo de dato de la "sopa" creada
print(type(soup))

#Imprimir con formato
print(soup.prettify())

#Apuntar a los artículos para extraerlos
frases_html = soup.find_all('div', attrs={'class':'quote'})


# Lista temporal para guardar los frases
frases = []

#iterar los frases y obtener las variables
for frase in frases_html:
    contenido_frase = frase.find('span', attrs={'class': 'text'}).get_text()
    autor_frase = frase.find('small', attrs={'class': 'author'}).get_text()
    tags_frase = [tag.get_text() for tag in frase.find_all('a', attrs={'class': 'tag'})]
    
    temp_row = [contenido_frase, autor_frase, tags_frase]
    frases.append(temp_row)
    print(temp_row)

# Crear un DataFrame de pandas con las frases
frases_df = pd.DataFrame(frases, columns=['Contenido', 'Autor', 'Tags'])



# Inspeccionar el dataframe
print(frases_df.head(10))    

