import psycopg2
import db

def list_databases():
    try:
        # Conexión al servidor PostgreSQL (sin especificar una base de datos)
        conn = psycopg2.connect(dbname='postgres', user=db.DB_USER, password=db.DB_PASSWORD, host=db.DB_HOST, port=db.DB_PORT)
        cursor = conn.cursor()

        # Listar todas las bases de datos
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cursor.fetchall()

        print("Bases de datos disponibles:")
        for db in databases:
            print(f" - {db[0]}")

    except psycopg2.Error as e:
        print(f"Error al conectar con el servidor de base de datos: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    list_databases()
