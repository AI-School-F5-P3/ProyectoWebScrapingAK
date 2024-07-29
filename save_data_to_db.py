import asyncio
import asyncpg
import pandas as pd
from scraper import Scraper
import db  # Importamos la configuración de la base de datos

class AsyncDataSaver:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    async def connect(self):
        self.conn = await asyncpg.connect(
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port
        )

    async def close(self):
        await self.conn.close()

    async def save_to_database(self, frases_df, tags_df):
        await self.connect()

        async with self.conn.transaction():
            try:
                # Insertar datos en la tabla de etiquetas (tags)
                for _, row in tags_df.iterrows():
                    try:
                        await self.conn.execute("""
                        INSERT INTO tag (tag_id, tag_texto)
                        VALUES ($1, $2)
                        ON CONFLICT (tag_id) DO UPDATE SET tag_texto = EXCLUDED.tag_texto
                        """, row.get('tag_id'), row.get('tag_texto'))
                    except Exception as e:
                        print(f"Error al insertar en tag: {e}")

                # Insertar datos en la tabla de autores
                for _, row in frases_df.iterrows():
                    try:
                        await self.conn.execute("""
                        INSERT INTO autor (autor_nombre, autor_apellido, autor_url, autor_fecha_nac, autor_lugar_nac, autor_descripcion)
                        VALUES ($1, $2, $3, $4, $5, TRIM($6))
                        ON CONFLICT (autor_nombre, autor_apellido)
                        DO UPDATE SET autor_url = EXCLUDED.autor_url,
                                      autor_fecha_nac = EXCLUDED.autor_fecha_nac,
                                      autor_lugar_nac = EXCLUDED.autor_lugar_nac,
                                      autor_descripcion = EXCLUDED.autor_descripcion
                        """, row.get('autor_nombre'), row.get('autor_apellido'),
                           row.get('autor_url'), row.get('autor_fecha_nac'),
                           row.get('autor_lugar_nac'), row.get('autor_descripcion'))
                    except Exception as e:
                        print(f"Error al insertar en autor: {e}")

                # Insertar datos en la tabla de frases (quotes)
                for _, row in frases_df.iterrows():
                    try:
                        # Obtener el id del autor
                        autor_id = await self.conn.fetchval("""
                        SELECT autor_id FROM autor WHERE autor_nombre = $1 AND autor_apellido = $2
                        """, row.get('autor_nombre'), row.get('autor_apellido'))

                        if autor_id:
                            frase_id = await self.conn.fetchval("""
                            INSERT INTO frase (frase_texto, autor_id)
                            VALUES ($1, $2)
                            ON CONFLICT (frase_texto)
                            DO UPDATE SET autor_id = EXCLUDED.autor_id
                            RETURNING frase_id
                            """, row.get('frase_texto'), autor_id)
                    except Exception as e:
                        print(f"Error al insertar o actualizar en frase: {e}")
                        continue

                    # Insertar relaciones en la tabla de unión frase_tag
                    tags_ids = row.get('Tags_IDs', [])  # 'Tags_IDs' es ahora una lista de IDs
                    for tag_id in tags_ids:
                        try:
                            tag_id = int(tag_id)  # Convertir a entero si es necesario
                            await self.conn.execute("""
                            INSERT INTO frase_tag (frase_id, tag_id)
                            VALUES ($1, $2)
                            ON CONFLICT (frase_id, tag_id) DO NOTHING
                            """, frase_id, tag_id)
                        except Exception as e:
                            print(f"Error al insertar en frase_tag: {e}")

            except asyncpg.PostgresError as e:
                print(f"Error de PostgreSQL: {e}")
            except Exception as e:
                print(f"Error inesperado: {e}")

        await self.close()

if __name__ == "__main__":
    base_url = "https://quotes.toscrape.com/"
    scraper = Scraper(base_url)
    frases_df, tags_df = scraper.scrape_quotes()
    
    data_saver = AsyncDataSaver(
        db_name=db.DB_NAME,
        db_user=db.DB_USER,
        db_password=db.DB_PASSWORD,
        db_host=db.DB_HOST,
        db_port=db.DB_PORT
    )
    
    asyncio.run(data_saver.save_to_database(frases_df, tags_df))
