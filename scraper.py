import requests
import pandas as pd
from bs4 import BeautifulSoup
import logging
import os

class Scraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tags_dict = {}
        self.next_tag_id = 1
        self.setup_logger()

    def setup_logger(self):
        # Asegurarse de que la carpeta 'logs' exista
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)

        # Crear el logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Crear manejador de archivo con la ruta dentro de la carpeta 'logs'
        log_file = os.path.join(log_dir, 'scraper.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # Crear el formato de los logs
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Agregar manejador de archivo al logger
        self.logger.addHandler(file_handler)

    def get_author_details(self, autor_url):
        """
        Extrae la fecha de nacimiento, ubicación de nacimiento y descripción del autor desde su página.
        """
        self.logger.info(f"Extrayendo detalles del autor desde: {autor_url}")
        try:
            autor_response = requests.get(autor_url)
            autor_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error al obtener la página del autor: {e}")
            return None
        
        try:
            autor_soup = BeautifulSoup(autor_response.text, 'lxml')
            
            born_date = autor_soup.find('span', class_='author-born-date')
            born_location = autor_soup.find('span', class_='author-born-location')
            description = autor_soup.find('div', class_='author-description')
            
            details = {
                'author-born-date': born_date.get_text() if born_date else '',
                'author-born-location': born_location.get_text() if born_location else '',
                'author-description': description.get_text() if description else ''
            }
            self.logger.info(f"Detalles del autor obtenidos: {details}")
        except Exception as e:
            self.logger.error(f"Error al procesar la página del autor: {e}")
            details = None
        
        return details

    def scrape_quotes(self):
        """
        Realiza el scraping de frases, autores y etiquetas desde la página especificada.
        """
        self.logger.info("Iniciando scraping de frases")
        data = []
        page_number = 1

        while True:
            page_url = f"{self.base_url}page/{page_number}/"
            self.logger.info(f"Scraping página: {page_url}")

            try:
                frases_to_scrape = requests.get(page_url)
                frases_to_scrape.raise_for_status()
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error al realizar la petición: {e}")
                break

            try:
                soup = BeautifulSoup(frases_to_scrape.text, 'lxml')
                frases_html = soup.find_all('div', attrs={'class': 'quote'})

                if not frases_html:
                    self.logger.info("No se encontraron más frases.")
                    break

                for frase in frases_html:
                    try:
                        contenido_frase = frase.find('span', class_='text').get_text()
                        self.logger.info(f"Frase obtenida: {contenido_frase}")
                        
                        autor_nombre_completo = frase.find('small', class_='author').get_text()
                        autor_url = frase.find('a')['href']
                        autor_url = self.base_url + autor_url
                        
                        details = self.get_author_details(autor_url)
                        
                        if details is None:
                            self.logger.warning(f"No se pudieron obtener detalles del autor para la frase: {contenido_frase}")
                            continue
                        
                        nombres = autor_nombre_completo.split()
                        nombre = nombres[0]
                        apellido = " ".join(nombres[1:]) if len(nombres) > 1 else ""

                        tags = [tag.get_text() for tag in frase.find_all('a', class_='tag')]
                        self.logger.info(f"Tags obtenidos: {tags}")
                        
                        tags_ids = []
                        
                        for tag in tags:
                            if tag not in self.tags_dict:
                                self.tags_dict[tag] = self.next_tag_id
                                self.next_tag_id += 1
                            tags_ids.append(self.tags_dict[tag])
                        self.logger.info(f"IDs de los tags: {tags_ids}")
                        
                        temp_row = {
                            'frase_texto': contenido_frase,
                            'autor_nombre': nombre,
                            'autor_apellido': apellido,
                            'autor_url': autor_url,
                            'autor_fecha_nac': details['author-born-date'],
                            'autor_lugar_nac': details['author-born-location'],
                            'autor_descripcion': details['author-description'],
                            'Tags': tags,
                            'Tags_IDs': tags_ids
                        }
                        data.append(temp_row)
                    except Exception as e:
                        self.logger.error(f"Error al procesar una frase: {e}")
                        continue

                page_number += 1
            except Exception as e:
                self.logger.error(f"Error al procesar la página de frases: {e}")
                break
        
        try:
            frases_df = pd.DataFrame(data)
            frases_df['autor_descripcion'] = frases_df['autor_descripcion'].str.strip()
            tags_df = pd.DataFrame(list(self.tags_dict.items()), columns=['tag_texto', 'tag_id'])
            
            self.logger.info(f"Scraping completado. Total de frases: {len(frases_df)}. Total de tags: {len(tags_df)}.")
        except Exception as e:
            self.logger.error(f"Error al crear los DataFrames: {e}")
            frases_df, tags_df = pd.DataFrame(), pd.DataFrame()
        
        return frases_df, tags_df

    def save_to_excel(self, frases_df, tags_df, filename='frases_autores_detalles.xlsx'):
        """
        Guarda los DataFrames en un archivo Excel con dos hojas: una para las frases y otra para los tags.
        """
        try:
            with pd.ExcelWriter(filename) as writer:
                frases_df.to_excel(writer, sheet_name='Frases_Autores_Detalles', index=False)
                tags_df.to_excel(writer, sheet_name='Tags', index=False)
            self.logger.info(f"Datos guardados en {filename}")
        except Exception as e:
            self.logger.error(f"Error al guardar los datos en Excel: {e}")

if __name__ == "__main__":
    base_url = "https://quotes.toscrape.com/"
    scraper = Scraper(base_url)
    
    frases_df, tags_df = scraper.scrape_quotes()
    
    scraper.save_to_excel(frases_df, tags_df)
