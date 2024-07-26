import requests
import pandas as pd
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tags_dict = {}
        self.next_tag_id = 1

    def get_author_details(self, autor_url):
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

    def scrape_quotes(self):
        """
        Realiza el scraping de frases, autores y etiquetas desde la página especificada.
        
        Returns:
        tuple: (pd.DataFrame, pd.DataFrame) con la información de frases, autores y etiquetas.
        """
        data = []
        page_number = 1

        while True:
            page_url = f"{self.base_url}page/{page_number}/"
            print(f"Scraping página: {page_url}")

            try:
                frases_to_scrape = requests.get(page_url)
                frases_to_scrape.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error al realizar la petición: {e}")
                break

            soup = BeautifulSoup(frases_to_scrape.text, 'lxml')

            frases_html = soup.find_all('div', attrs={'class': 'quote'})

            if not frases_html:
                break

            for frase in frases_html:
                contenido_frase = frase.find('span', class_='text').get_text()
                autor_nombre_completo = frase.find('small', class_='author').get_text()
                autor_url = frase.find('a')['href']
                autor_url = self.base_url + autor_url
                
                details = self.get_author_details(autor_url)
                
                if details is None:
                    continue
                
                nombres = autor_nombre_completo.split()
                nombre = nombres[0]
                apellido = " ".join(nombres[1:]) if len(nombres) > 1 else ""

                tags = [tag.get_text() for tag in frase.find_all('a', class_='tag')]
                tags_ids = []
                
                for tag in tags:
                    if tag not in self.tags_dict:
                        self.tags_dict[tag] = self.next_tag_id
                        self.next_tag_id += 1
                    tags_ids.append(self.tags_dict[tag])
                
                temp_row = {
                    'frase_texto': contenido_frase,
                    'autor_nombre': nombre,
                    'autor_apellido': apellido,
                    'autor_url': autor_url,
                    'autor_fecha_nac': details['author-born-date'],
                    'autor_lugar_nac': details['author-born-location'],
                    'autor_descripcion': details['author-description'],
                    'Tags': tags,  # Dejar como lista de etiquetas
                    'Tags_IDs': tags_ids  # Dejar como lista de IDs
                }
                data.append(temp_row)
            
            page_number += 1
        
        frases_df = pd.DataFrame(data)
        
        # Limpiar espacios en blanco en la columna 'autor_descripcion'
        frases_df['autor_descripcion'] = frases_df['autor_descripcion'].str.strip()
        
        tags_df = pd.DataFrame(list(self.tags_dict.items()), columns=['tag_texto', 'tag_id'])
        
        return frases_df, tags_df

    def save_to_excel(self, frases_df, tags_df, filename='frases_autores_detalles.xlsx'):
        """
        Guarda los DataFrames en un archivo Excel con dos hojas: una para las frases y otra para los tags.
        
        Args:
        frases_df (pd.DataFrame): DataFrame con frases y detalles de autores.
        tags_df (pd.DataFrame): DataFrame con los tags y sus IDs.
        filename (str): Nombre del archivo Excel.
        """
        with pd.ExcelWriter(filename) as writer:
            frases_df.to_excel(writer, sheet_name='Frases_Autores_Detalles', index=False)
            tags_df.to_excel(writer, sheet_name='Tags', index=False)
        print(f"Datos guardados en {filename}")

if __name__ == "__main__":
    base_url = "https://quotes.toscrape.com/"
    scraper = Scraper(base_url)
    
    frases_df, tags_df = scraper.scrape_quotes()
    
    print(f"Número de registros en frases_df: {len(frases_df)}")
    print(f"Número de registros en tags_df: {len(tags_df)}")
    
    print(frases_df.head(20))
    print(tags_df.head(20))
    
    scraper.save_to_excel(frases_df, tags_df)

    print("Columnas en frases_df:", frases_df.columns)
    print("Columnas en tags_df:", tags_df.columns)

    # Verificar los datos
    print(frases_df[['frase_texto', 'Tags']])
