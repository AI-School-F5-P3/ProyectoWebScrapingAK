import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from db import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from datetime import datetime
import math

# Configuración de la página al inicio
st.set_page_config(page_title="Frases Célebres", layout="wide")

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
        SELECT frase.frase_texto, autor.autor_id, autor.autor_nombre, autor.autor_apellido, autor.autor_url, array_agg(tag.tag_texto) as tags
        FROM frase
        JOIN autor ON frase.autor_id = autor.autor_id
        JOIN frase_tag ON frase.frase_id = frase_tag.frase_id
        JOIN tag ON frase_tag.tag_id = tag.tag_id
        GROUP BY frase.frase_id, autor.autor_id, autor.autor_nombre, autor.autor_apellido, autor.autor_url
        """
        autores_query = """
        SELECT autor_id, autor_nombre, autor_apellido, autor_fecha_nac, autor_lugar_nac, autor_descripcion
        FROM autor
        """
        tags_query = """
        SELECT tag_id, tag_texto
        FROM tag
        """
        frases_df = self.db_connector.fetch_data(frases_query)
        autores_df = self.db_connector.fetch_data(autores_query)
        tags_df = self.db_connector.fetch_data(tags_query)
        return frases_df, autores_df, tags_df

    def get_quotes_by_author_id(self, author_id):
        """Fetches quotes by a specific author ID."""
        query = f"""
        SELECT frase.frase_texto, autor.autor_nombre, autor.autor_apellido, autor.autor_url, array_agg(tag.tag_texto) as tags
        FROM frase
        JOIN autor ON frase.autor_id = autor.autor_id
        JOIN frase_tag ON frase.frase_id = frase_tag.frase_id
        JOIN tag ON frase_tag.tag_id = tag.tag_id
        WHERE autor.autor_id = {author_id}
        GROUP BY frase.frase_id, autor.autor_nombre, autor.autor_apellido, autor.autor_url
        """
        return self.db_connector.fetch_data(query)

    def get_quotes_by_author(self, author_name):
        """Fetches quotes by a specific author."""
        query = f"""
        SELECT frase.frase_texto, autor.autor_nombre, autor.autor_apellido, autor.autor_url, array_agg(tag.tag_texto) as tags
        FROM frase
        JOIN autor ON frase.autor_id = autor.autor_id
        JOIN frase_tag ON frase.frase_id = frase_tag.frase_id
        JOIN tag ON frase_tag.tag_id = tag.tag_id
        WHERE autor.autor_nombre ILIKE '%{author_name}%' OR autor.autor_apellido ILIKE '%{author_name}%'
        GROUP BY frase.frase_id, autor.autor_nombre, autor.autor_apellido, autor.autor_url
        """
        return self.db_connector.fetch_data(query)

    def get_quotes_by_tag(self, tag_text):
        """Fetches quotes by a specific tag."""
        query = f"""
        SELECT frase.frase_texto, autor.autor_nombre, autor.autor_apellido, autor.autor_url, array_agg(tag.tag_texto) as tags
        FROM frase
        JOIN autor ON frase.autor_id = autor.autor_id
        JOIN frase_tag ON frase.frase_id = frase_tag.frase_id
        JOIN tag ON frase_tag.tag_id = tag.tag_id
        WHERE tag.tag_texto ILIKE '%{tag_text}%'
        GROUP BY frase.frase_id, autor.autor_nombre, autor.autor_apellido, autor.autor_url
        """
        return self.db_connector.fetch_data(query)


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

    def show_quotes(self):
        st.subheader("Frases")
        frases_df, _, _ = self.data_fetcher.get_data()
        self.display_data_with_pagination(frases_df, self.display_quote, 'quotes')

    def show_authors(self):
        st.subheader("Autores")
        _, autores_df, _ = self.data_fetcher.get_data()
        self.display_data_with_pagination(autores_df, self.display_author, 'authors')

    def display_data_with_pagination(self, data_df, display_func, page_type):
        items_per_page = 10
        if page_type not in st.session_state:
            st.session_state[page_type] = 1

        total_items = len(data_df)
        total_pages = math.ceil(total_items / items_per_page)
        current_page = st.session_state[page_type]

        start_idx = (current_page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)

        # Mostrar datos de la página actual
        for index in range(start_idx, end_idx):
            display_func(data_df.iloc[index])

        # Controles de navegación
        col1, col2, col3 = st.columns([1, 1, 1])
    
        with col1:
            if current_page > 1:
                if st.button('Anterior', key=f'previous_{page_type}', help="Ir a la página anterior"):
                    st.session_state[page_type] -= 1
                    st.experimental_rerun()

        with col3:
            if current_page < total_pages:
                if st.button('Siguiente', key=f'next_{page_type}', help="Ir a la página siguiente"):
                    st.session_state[page_type] += 1
                    st.experimental_rerun()

    def display_quote(self, row):
        st.markdown(f"""
        <div style="background-color:#FFFACD;padding:10px;border-radius:10px;margin-bottom:10px;">
            <p><strong>Frase:</strong> {row['frase_texto']}</p>
            <p><strong>Autor:</strong> <a href="{row['autor_url']}" target="_blank">{row['autor_nombre']} {row['autor_apellido']}</a></p>
            <p><strong>Tags:</strong> {', '.join(row['tags'])}</p>
        </div>
        """, unsafe_allow_html=True)

    def display_author(self, row):
        st.markdown(f"""
        <div style="background-color:#E6E6FA;padding:10px;border-radius:10px;margin-bottom:10px;">
            <p><strong>Nombre:</strong> {row['autor_nombre']} {row['autor_apellido']}</p>
            <p><strong>Fecha de nacimiento:</strong> {row['autor_fecha_nac']}</p>
            <p><strong>Lugar de nacimiento:</strong> {row['autor_lugar_nac']}</p>
            <p><strong>Descripción:</strong> {row['autor_descripcion']}</p>
        </div>
        """, unsafe_allow_html=True)

    def search_quotes_by_author(self):
        st.subheader("Buscar Frases por Autor")

        # Obtener los datos necesarios
        try:
            frases_df, autores_df, _ = self.data_fetcher.get_data()
        except Exception as e:
            st.error(f"Error al obtener los datos de la base de datos: {e}")
            return

        # Crear lista de selección para los dropdowns
        author_options = autores_df.apply(lambda x: f"{x['autor_nombre']} {x['autor_apellido']}", axis=1).tolist()
        
        # Dropdown para selección de autor
        selected_author = st.selectbox("Selecciona un autor", author_options)

        # Filtrar el DataFrame de autores para obtener el autor_id
        if selected_author:
            selected_author_name, selected_author_lastname = selected_author.split(' ', 1)
            author_filtered_df = autores_df[
                (autores_df['autor_nombre'] == selected_author_name) & 
                (autores_df['autor_apellido'] == selected_author_lastname)
            ]
            
            if not author_filtered_df.empty:
                selected_author_id = author_filtered_df.iloc[0]['autor_id']
            else:
                st.write("No se encontró el autor seleccionado.")
                selected_author_id = None
        else:
            selected_author_id = None

        # Buscar y mostrar frases por autor
        if selected_author_id:
            try:
                frases_df_by_author = self.data_fetcher.get_quotes_by_author_id(selected_author_id)
                if not frases_df_by_author.empty:
                    st.write(f"Frases del autor seleccionado:")
                    for index, row in frases_df_by_author.iterrows():
                        self.display_quote(row)
                else:
                    st.write("No se encontraron frases para el autor seleccionado.")
            except Exception as e:
                st.error(f"Error al buscar frases por autor: {e}")

    def search_quotes_by_tag(self):
        st.subheader("Buscar Frases por Tag")

        # Obtener los datos necesarios
        try:
            frases_df, _, tags_df = self.data_fetcher.get_data()
        except Exception as e:
            st.error(f"Error al obtener los datos de la base de datos: {e}")
            return

        # Crear lista de selección para los dropdowns
        tag_options = tags_df['tag_texto'].tolist()

        # Dropdown para selección de tag
        selected_tag = st.selectbox("Selecciona un tag", tag_options)

        # Buscar y mostrar frases por tag
        if selected_tag:
            try:
                # Filtrar frases relacionadas con el tag seleccionado
                query = f"""
                SELECT frase.frase_texto, autor.autor_nombre, autor.autor_apellido, autor.autor_url, array_agg(tag.tag_texto) as tags
                FROM frase
                JOIN frase_tag ON frase.frase_id = frase_tag.frase_id
                JOIN tag ON frase_tag.tag_id = tag.tag_id
                JOIN autor ON frase.autor_id = autor.autor_id
                WHERE tag.tag_texto = %s
                GROUP BY frase.frase_id, autor.autor_nombre, autor.autor_apellido, autor.autor_url
                """
                
                # Ejecutar la consulta
                with self.db_connector.engine.connect() as conn:
                    frases_df_by_tag = pd.read_sql_query(query, conn, params=(selected_tag,))
                
                if not frases_df_by_tag.empty:
                    st.write(f"Frases con el tag '{selected_tag}':")
                    for index, row in frases_df_by_tag.iterrows():
                        self.display_quote(row)
                else:
                    st.write("No se encontraron frases con el tag seleccionado.")
            except Exception as e:
                st.error(f"Error al buscar frases por tag: {e}")




    def show_statistics(self):
        st.subheader("Estadísticas")
        frases_df, _, _ = self.data_fetcher.get_data()

        frases_por_autor = frases_df.groupby(['autor_nombre', 'autor_apellido']).size().reset_index(name='counts')
        frases_por_autor['full_name'] = frases_por_autor['autor_nombre'] + ' ' + frases_por_autor['autor_apellido']

        frases_por_tag = frases_df.explode('tags').groupby('tags').size().reset_index(name='counts')

        st.bar_chart(frases_por_autor.set_index('full_name')['counts'], height=300)
        st.bar_chart(frases_por_tag.set_index('tags')['counts'], height=300)

    # def show_on_this_day(self):
    #     st.subheader("Un día como hoy nacía...")
    #     _, autores_df, _ = self.data_fetcher.get_data()
    #     today = datetime.today()
    #     today_date = f"{today.strftime('%B')} {today.day}"

    #     for index, row in autores_df.iterrows():
    #         if today_date in row['autor_fecha_nac']:
    #             st.markdown(f"**Nombre:** {row['autor_nombre']} {row['autor_apellido']}")
    #             st.markdown(f"**Fecha de nacimiento:** {row['autor_fecha_nac']}")
    #             st.markdown(f"**Lugar de nacimiento:** {row['autor_lugar_nac']}")
    #             st.markdown(f"**Descripción:** {row['autor_descripcion']}")
    #             st.markdown("---")

    # def create_quote(self):
    #     st.subheader("Crea tu frase")
    #     word1 = st.text_input("Palabra 1")
    #     word2 = st.text_input("Palabra 2")
    #     word3 = st.text_input("Palabra 3")

    #     if st.button("Generar frase"):
    #         if word1 and word2 and word3:
    #             new_quote = f"{word1} {word2} {word3}."
    #             st.success(f"Frase generada: {new_quote}")
    #         else:
    #             st.error("Por favor, ingrese tres palabras.")

    def run(self):
        """Runs the Streamlit app."""
        st.sidebar.title("Navegación")
        menu = ["Frases", "Autores", "Buscar Frases por Autor", "Buscar Frases por Tag", "Estadísticas"]
        choice = st.sidebar.selectbox("Selecciona una opción", menu)

        st.title("Frases Célebres")

        if choice == "Frases":
            self.show_quotes()
        elif choice == "Autores":
            self.show_authors()
        elif choice == "Buscar Frases por Autor":
            self.search_quotes_by_author()
        elif choice == "Buscar Frases por Tag":
            self.search_quotes_by_tag()
        elif choice == "Estadísticas":
            self.show_statistics()
        # elif choice == "Un día como hoy":
        #     self.show_on_this_day()
        # elif choice == "Crea tu frase":
        #     self.create_quote()

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
