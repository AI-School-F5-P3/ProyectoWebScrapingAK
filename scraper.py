import requests
import pandas as pd
from bs4 import BeautifulSoup
import csv
import openpyxl

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
    contenido_frase = frase.find('span', class_='text').get_text()
    autor = frase.find('small', class_='author').get_text()
    autor_url = frase.find('a')['href']
    autor_url = url + autor_url

    try:
        autor_response = requests.get(autor_url)
        autor_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página del autor: {e}")
        continue

    autor_soup = BeautifulSoup(autor_response.text, 'lxml')
    about_autor = autor_soup.find('div', class_='author-description').get_text()

    tags = [tag.get_text() for tag in frase.find_all('a', class_='tag')]

    temp_row = [contenido_frase, autor, about_autor, tags]
    frases.append(temp_row)
    print(temp_row)

# Crear un DataFrame de pandas con las frases
frases_df = pd.DataFrame(frases, columns=['Frase', 'Autor', 'About Autor', 'Tags'])

# # Función para truncar el contenido de las columnas al mostrar df en consola
# def truncar_contenido(contenido, longitud_maxima=30):
#     if len(contenido) > longitud_maxima:
#         return contenido[:longitud_maxima] + '...'
#     return contenido

# # Aplicar la función de truncar a cada columna
# frases_df['Frase'] = frases_df['Frase'].apply(truncar_contenido)
# frases_df['About Autor'] = frases_df['About Autor'].apply(truncar_contenido)
# frases_df['Tags'] = frases_df['Tags'].apply(lambda x: truncar_contenido(", ".join(x)))


# Inspeccionar el dataframe
print(frases_df.head(10))    


# # Guardar el DataFrame en un archivo CSV
# frases_df.to_csv('frases.csv', index=False, encoding='utf-8')

# # Guardar el DataFrame completo en un archivo Excel
# frases_df.to_excel('frases_completas.xlsx')

# Función para procesar las tags y crear un DataFrame de tags únicos
def process_tags(df):
    """
    Procesa los datos de la columna 'Tags' del DataFrame para organizar las palabras únicas en una tabla.
    
    Args:
    df (pd.DataFrame): DataFrame que contiene la columna 'Tags'.
    
    Returns:
    pd.DataFrame: DataFrame con las columnas 'tag_id' y 'tag', con una palabra por fila.
    """
    # Extraer la columna 'Tags' y concatenar todas las palabras en una sola serie
    tags = df['Tags'].dropna().explode().str.split(expand=True).stack()

    # Eliminar duplicados y restablecer el índice
    unique_tags = pd.DataFrame(tags.unique(), columns=['tag']).reset_index()
    
    # Renombrar la columna del índice a 'tag_id'
    unique_tags.rename(columns={'index': 'tag_id'}, inplace=True)
    
    # Convertir 'tag_id' a entero
    unique_tags['tag_id'] = unique_tags['tag_id'].astype(int)

    return unique_tags

# Procesar las tags
processed_tags_df = process_tags(frases_df)

# Mostrar el DataFrame de tags procesado
print(processed_tags_df)

# Guardar el DataFrame completo en un archivo Excel
frases_df.to_excel('frases_completas.xlsx', index=False)

# Guardar el DataFrame de tags procesados en un archivo Excel
processed_tags_df.to_excel('tags_procesados.xlsx', index=False)