import asyncpg
import asyncio
import db  # Importamos la configuración de la base de datos

class AsyncDatabaseManager:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    async def create_database(self):
        try:
            # Conexión al servidor PostgreSQL (sin especificar una base de datos)
            conn = await asyncpg.connect(database='postgres', user=self.db_user, password=self.db_password, 
                                         host=self.db_host, port=self.db_port)
            # Verificar si la base de datos ya existe
            databases = await conn.fetch("SELECT datname FROM pg_database WHERE datname = $1", self.db_name)
            if not databases:
                await conn.execute(f'CREATE DATABASE {self.db_name}')
                print(f"Base de datos {self.db_name} creada.")
            else:
                print(f"La base de datos {self.db_name} ya existe.")
        
        except asyncpg.PostgresError as e:
            print(f"Error al crear la base de datos: {e}")
        
        finally:
            await conn.close()

    async def create_tables(self):
        try:
            # Conexión a la base de datos específica
            conn = await asyncpg.connect(database=self.db_name, user=self.db_user, password=self.db_password, 
                                         host=self.db_host, port=self.db_port)

            # Crear tablas si no existen
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS frase (
                frase_id SERIAL PRIMARY KEY,
                frase_text TEXT UNIQUE,
                autor_id INTEGER REFERENCES autor(autor_id),
                tag_id INTEGER REFERENCES tag(tag_id)                                                          
            )
            """)
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS autor (
                autor_id SERIAL PRIMARY KEY,
                autor_nombre VARCHAR(255),
                autor_apellido VARCHAR(255),
                autor_url VARCHAR(255),
                autor_fecha_nac VARCHAR(255),
                autor_lugar_nac VARCHAR(255),
                autor_descripcion TEXT,
                UNIQUE (autor_nombre, autor_apellido)
            )
            """)
            await conn.execute("""
            CREATE TABLE IF NOT EXISTS tag (
                tag_id SERIAL PRIMARY KEY,
                tag_text VARCHAR(255) UNIQUE
            )
            """)
            print("Tablas creadas.")
        
        except asyncpg.PostgresError as e:
            print(f"Error al crear las tablas: {e}")
        
        finally:
            await conn.close()

async def main():
    # Usamos la configuración importada desde db.py
    db_config = {
        'db_name': db.DB_NAME,
        'db_user': db.DB_USER,
        'db_password': db.DB_PASSWORD,
        'db_host': db.DB_HOST,
        'db_port': db.DB_PORT
    }

    db_manager = AsyncDatabaseManager(**db_config)
    await db_manager.create_database()
    await db_manager.create_tables()

if __name__ == "__main__":
    asyncio.run(main())
