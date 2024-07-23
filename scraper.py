import requests
import pandas as pd
from bs4 import BeautifulSoup

# Variable con la dirección del sitio a hacer scraping
url = "https://quotes.toscrape.com/"

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
    
    return {
        'author-born-date': born_date.get_text() if born_date else '',
        'author-born-location': born_location.get_text() if born_location else '',
        'author-description': description.get_text() if description else ''
    }

def scrape_quotes(url):
    """
    Realiza el scraping de frases, autores y etiquetas desde la página especificada.
    
    Args:
    url (str): URL del sitio a hacer scraping.
    
    Returns:
    pd.DataFrame: DataFrame con la información de frases, autores y etiquetas.
    """
    try:
        # Realizar la petición con requests y guardar el contenido de la página
        frases_to_scrape = requests.get(url)
        frases_to_scrape.raise_for_status()  # Para manejar errores HTTP
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la petición: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
    
    # Parsear la información mediante BeautifulSoup
    soup = BeautifulSoup(frases_to_scrape.text, 'lxml')
    
    # Apuntar a los artículos para extraerlos
    frases_html = soup.find_all('div', attrs={'class': 'quote'})
    
    # Lista temporal para guardar las frases y detalles del autor
    data = []
    
    # Crear un diccionario para los tags
    tags_dict = {}
    next_tag_id = 1
    

    # Iterar sobre las frases y obtener las variables
    for frase in frases_html:
        contenido_frase = frase.find('span', class_='text').get_text()
        autor_nombre_completo = frase.find('small', class_='author').get_text()
        autor_url = frase.find('a')['href']
        autor_url = url + autor_url
        
        # Extraer detalles del autor
        details = get_author_details(autor_url)
        
        # Si los detalles no se pudieron obtener, continuar con el siguiente
        if details is None:
            continue
        
        # Dividir el nombre completo en nombre y apellido
        nombres = autor_nombre_completo.split()
        nombre = nombres[0]
        apellido = " ".join(nombres[1:]) if len(nombres) > 1 else ""

        # # Obtener las etiquetas
        # tags = [tag.get_text() for tag in frase.find_all('a', class_='tag')]
        
        # Obtener las etiquetas
        tags = [tag.get_text() for tag in frase.find_all('a', class_='tag')]
        tags_ids = []
        
        for tag in tags:
            if tag not in tags_dict:
                tags_dict[tag] = next_tag_id
                next_tag_id += 1
            tags_ids.append(tags_dict[tag])


        # Añadir la fila con todos los datos
        temp_row = {
            'Frase': contenido_frase,
            'Autor_Nombre': nombre,
            'Autor_Apellido': apellido,
            'Autor_URL': autor_url,
            'Author_Born_Date': details['author-born-date'],
            'Author_Born_Location': details['author-born-location'],
            'Author_Description': details['author-description'],
            'Tags': ', '.join(tags),  # Unir etiquetas en una sola cadena
            'Tags_IDs': ', '.join(map(str, tags_ids))
        }
        data.append(temp_row)
    
    # Crear un DataFrame de pandas con toda la información
    df = pd.DataFrame(data)
    
    # Crear un DataFrame para los tags
    tags_df = pd.DataFrame(list(tags_dict.items()), columns=['tag', 'tag_id'])
    

    return df,tags_df

# Ejecutar la función de scraping
final_df, tags_df = scrape_quotes(url)

# Inspeccionar el DataFrame final
print(final_df.head(10))
print(tags_df.head(10))

# Guardar los DataFrames en archivos Excel
with pd.ExcelWriter('frases_autores_detalles.xlsx') as writer:
    final_df.to_excel(writer, sheet_name='Frases_Autores_Detalles', index=False)
    tags_df.to_excel(writer, sheet_name='Tags', index=False)

