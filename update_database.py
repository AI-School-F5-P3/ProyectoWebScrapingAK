import asyncio
import asyncpg
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scraper import Scraper
import db  # Asegúrate de que este módulo tenga la configuración de la base de datos
from save_data_to_db import AsyncDataSaver
import time  # Para medir el tiempo de ejecución

class DatabaseUpdater:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    async def update_database(self):
        start_time = time.time()  # Marca el inicio del proceso
        print("Iniciando actualización de base de datos...")

        # Crear una instancia del scraper
        base_url = "https://quotes.toscrape.com/"
        scraper = Scraper(base_url)
        
        # Obtener datos de las citas y etiquetas
        frases_df, tags_df = scraper.scrape_quotes()

        # Conectar a la base de datos
        conn = await asyncpg.connect(
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )

        try:
            async with conn.transaction():
                # Insertar o actualizar datos en la base de datos
                data_saver = AsyncDataSaver(self.db_name, self.db_user, self.db_password, self.db_host, self.db_port)
                await data_saver.save_to_database(frases_df, tags_df)
                print("Actualización completada.")
        except Exception as e:
            print(f"Error durante la actualización: {e}")
        finally:
            await conn.close()

        end_time = time.time()  # Marca el final del proceso
        elapsed_time = end_time - start_time
        print(f"Tiempo total de actualización: {elapsed_time:.2f} segundos")

# Configuración del scheduler
def main():
    db_name = db.DB_NAME
    db_user = db.DB_USER
    db_password = db.DB_PASSWORD
    db_host = db.DB_HOST
    db_port = db.DB_PORT

    updater = DatabaseUpdater(db_name, db_user, db_password, db_host, db_port)

    scheduler = AsyncIOScheduler()

    # Programar la tarea para que se ejecute cada 24 horas (86400 segundos)
    scheduler.add_job(
        updater.update_database,
        trigger=IntervalTrigger(seconds=86400),
        name="Update Database",
        replace_existing=True
    )

    # Iniciar el scheduler
    scheduler.start()

    # Mantener el script corriendo
    try:
        print("Scheduler iniciado. Presiona Ctrl+C para salir.")
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Deteniendo scheduler...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
