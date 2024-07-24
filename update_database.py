import time
import schedule
from scraper import Scraper
from save_data_to_db import save_to_database


"""
Utiliza el módulo schedule para programar el método update_database() 
que actualiza la base de datos. En el ejemplo, se programa para que se ejecute 
a la medianoche todos los días (00:00).
update_database(): Este método realiza el scraping de los datos y 
los guarda en la base de datos utilizando las funciones definidas previamente en Scraper y save_data_to_db.

"""

def update_database():
    base_url = "https://quotes.toscrape.com/"
    scraper = Scraper(base_url)
    quotes_df, tags_df = scraper.scrape_quotes()
    save_to_database(quotes_df, tags_df)
    print("Base de datos actualizada.")

def main():
    # Programar la tarea para que se ejecute cada día a la medianoche
    schedule.every().day.at("00:00").do(update_database)

    """Bucle Infinito: El script corre un bucle infinito que verifica periódicamente si hay alguna tarea 
    programada que deba ejecutarse (schedule.run_pending()). 
    Se usa time.sleep(1) para hacer una pausa breve entre cada verificación, evitando que el bucle consuma 
    demasiados recursos del sistema.
    """
    print("Iniciando programador de actualizaciones de base de datos...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
