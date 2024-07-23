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



# Inspeccionar el dataframe
print(frases_df.head(10))    



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

#AUTORES

# Primero, creamos un diccionario para almacenar los datos de los autores
autores_dict = {}

# Iterar sobre las frases para extraer información de los autores
for frase in frases_html:
    autor = frase.find('small', class_='author').get_text()
    autor_url = frase.find('a')['href']
    autor_url = url + autor_url

    # Solo extraemos la información si no está ya en el diccionario
    if autor_url not in autores_dict:
        try:
            autor_response = requests.get(autor_url)
            autor_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener la página del autor: {e}")
            continue
        
        autor_soup = BeautifulSoup(autor_response.text, 'lxml')
        autor_nombre_completo = autor_soup.find('h3', class_='author-title').get_text().strip()
        nombres = autor_nombre_completo.split()
        nombre = nombres[0]
        apellido = " ".join(nombres[1:]) if len(nombres) > 1 else ""

        # Almacenamos el autor en el diccionario
        autores_dict[autor_url] = {'nombre': nombre, 'apellido': apellido}

# Convertimos el diccionario en un DataFrame
autores_df = pd.DataFrame.from_dict(autores_dict, orient='index').reset_index()
autores_df.rename(columns={'index': 'autor_id'}, inplace=True)
autores_df['tag_id'] = autores_df['autor_id'].astype(int)

# Inspeccionar el DataFrame de autores
print(autores_df.head(10))

# Guardar el DataFrame de autores en un archivo Excel
autores_df.to_excel('autores.xlsx', index=False)

#Detalles de autores
# Función para extraer información detallada del autor
def get_author_details(autor_url):
    """
    Extrae la fecha de nacimiento, ubicación de nacimiento y descripción del autor desde su página.
    
    Args:
    autor_url (str): URL del autor.
    
    Returns:
    dict: Diccionario con 'author-born-date', 'author-born-location' y 'author-description'.
    """
    try:
        autor_response = requests.get(autor_url)
        autor_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la página del autor: {e}")
        return None
    
    autor_soup = BeautifulSoup(autor_response.text, 'lxml')
    
    born_date = autor_soup.find('span', class_='author-born-date')
    born_location = autor_soup.find('span', class_='author-born-location')
    description = autor_soup.find('div', class_='author-description')
    
    # Extraer el texto o establecer como vacío si no se encuentra
    return {
        'author-born-date': born_date.get_text() if born_date else '',
        'author-born-location': born_location.get_text() if born_location else '',
        'author-description': description.get_text() if description else ''
    }

# Actualizar el DataFrame de autores con información adicional
autores_details_list = []

for index, row in autores_df.iterrows():
    autor_url = row['autor_id']
    details = get_author_details(autor_url)
    if details:
        # Actualizar la fila del DataFrame con los detalles obtenidos
        autor_details = {**row.to_dict(), **details}
        autores_details_list.append(autor_details)

# Convertir la lista de detalles en un DataFrame
autores_details_df = pd.DataFrame(autores_details_list)

# Inspeccionar el DataFrame de autores con detalles adicionales
print(autores_details_df.head(10))

# Guardar el DataFrame final en un archivo Excel
autores_details_df.to_excel('autores_detalles.xlsx', index=False)


#Fin detalles de autores

#DESCARGAR DF´s

# Guardar el DataFrame completo en un archivo Excel
frases_df.to_excel('frases_completas.xlsx', index=False)

# Guardar el DataFrame de tags procesados en un archivo Excel
processed_tags_df.to_excel('tags_procesados.xlsx', index=False)

