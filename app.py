import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from db import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

class DatabaseConnector:
    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.engine = self._create_engine()

    def _create_engine(self):
        """Creates a SQLAlchemy engine."""
        return create_engine(f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}')

    def fetch_data(self, query):
        """Fetches data from the database using the provided query."""
        with self.engine.connect() as conn:
            df = pd.read_sql_query(query, conn)
        return df

class DataFetcher:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def get_data(self):
        """Fetches and returns data from the database."""
        frases_query = """
        SELECT frase_texto, autor_nombre, autor_apellido, tag_texto
        FROM frase
        JOIN autor ON frase.autor_id = autor.autor_id
        JOIN frase_tag ON frase.frase_id = frase_tag.frase_id
        JOIN tag ON frase_tag.tag_id = tag.tag_id
        """
        tags_query = """
        SELECT tag_id, tag_texto
        FROM tag
        """
        frases_df = self.db_connector.fetch_data(frases_query)
        tags_df = self.db_connector.fetch_data(tags_query)
        return frases_df, tags_df

class StreamlitApp:
    def __init__(self):
        self.db_connector = DatabaseConnector(
            db_name=DB_NAME,
            db_user=DB_USER,
            db_password=DB_PASSWORD,
            db_host=DB_HOST,
            db_port=DB_PORT
        )
        self.data_fetcher = DataFetcher(self.db_connector)

    def run(self):
        """Runs the Streamlit app."""
        st.title('Citas y Etiquetas')

        # Obtener datos
        frases_df, tags_df = self.data_fetcher.get_data()

        # Mostrar DataFrames en Streamlit
        st.subheader('Frases')
        st.write(frases_df)

        st.subheader('Etiquetas')
        st.write(tags_df)

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
