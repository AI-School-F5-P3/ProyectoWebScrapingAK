# Proyecto de Web Scraping

## Descripción del Proyecto
**Empresa:** XYZ Corp

**Nombre del Proyecto:** Web Scraping para Frases Inspiradoras

**Objetivo:** 
Desarrollar un programa en Python para realizar web scraping en [Quotes to Scrape](https://quotes.toscrape.com/). El objetivo es extraer todas las frases, autores, etiquetas asociadas y las páginas "about" con información sobre los autores. Los datos extraídos deben ser formateados y almacenados adecuadamente.

## Objetivos del Proyecto
1. **Acceder a una web preparada para scraping:** El sitio web contiene numerosas frases con información relacionada.
2. **Extraer información relevante:** Utilizar técnicas de web scraping en Python para obtener todas las frases junto con la información adicional (autor, etiquetas, about).
3. **Formatear los datos:** Asegurarse de que los datos extraídos estén limpios y organizados de manera coherente.
4. **Almacenar los datos en una base de datos:** Utilizar una base de datos SQL o NoSQL para guardar la información extraída.

## Plazos
**Duración:** 4 días  
**Fecha de Presentación:** Martes, 30 de Julio

## Entregables
1. **Repositorio en GitHub:** El repositorio con todo el código fuente desarrollado.
2. **Demo del Programa:** Una demo que muestre el funcionamiento del programa de scraping.
3. **Presentación de Negocio para un Público Técnico:** Explicar el objetivo del proyecto, la implementación, una breve descripción del código y las tecnologías utilizadas.
4. **Tablero Kanban:** Un enlace al tablero Kanban (Trello, Jira, etc.) utilizado para organizar el trabajo.

## Tecnologías Utilizadas
- **Control de Versiones:** ![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/GitHub-181717?logo=github&logoColor=white)
- **Contenerización:** ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
- **Lenguaje de Programación:** ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
- **Bibliotecas de Python:** ![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4B0082?logo=python&logoColor=white) ![Scrapy](https://img.shields.io/badge/Scrapy-4B8BBE?logo=scrapy&logoColor=white) ![Requests](https://img.shields.io/badge/Requests-3776AB?logo=python&logoColor=white)
- **Bases de Datos:** ![MySQL](https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)
- **Herramientas de Gestión de Proyectos:** ![Trello](https://img.shields.io/badge/Trello-0052CC?logo=trello&logoColor=white) ![Jira](https://img.shields.io/badge/Jira-0052CC?logo=jira&logoColor=white)

## Niveles de Entrega
### Nivel Esencial
- Un script que accede a la web, extrae las frases y la información asociada, y la imprime en la consola.
- Limpieza básica de los datos extraídos.
- Documentación básica del código y README en GitHub.

### Nivel Medio
- Almacenamiento de los datos extraídos en una base de datos.
- Implementación de un sistema de logs para la trazabilidad del código.
- Pruebas unitarias para asegurar el correcto funcionamiento del scraper.

### Nivel Avanzado
- Programación orientada a objetos (OOP) para estructurar mejor el código.
- Gestión de errores robusta para manejar excepciones comunes en web scraping.
- Un script que actualiza automáticamente la base de datos con nuevos datos a intervalos regulares.

### Nivel Experto
- Dockerización del proyecto para asegurar un entorno de ejecución consistente.
- Implementación de un frontend básico para visualizar los datos extraídos.
- Despliegue de la aplicación en un servidor web accesible públicamente.
- Utilizar otras webs de frases para aumentar la cantidad de frases scrapeadas.

## Actividad Sugerida
### Objetivo
Familiarizarse con las técnicas de web scraping y el manejo de bases de datos para almacenar datos extraídos.

### Instrucciones
1. **Preparación:**
   - Familiarizarse con las herramientas de web scraping en Python (BeautifulSoup, Scrapy, Requests).
   - Configurar un entorno de desarrollo (recomendado: Virtualenv, Docker).

2. **Desarrollo del Scraper:**
   - Crear un script que acceda a la web y extraiga los datos necesarios.
   - Limpiar y formatear los datos para asegurar su consistencia.

3. **Almacenamiento en Base de Datos:**
   - Configurar una base de datos (SQL/NoSQL) para almacenar los datos.
   - Desarrollar el código para insertar los datos extraídos en la base de datos.

4. **Documentación y Presentación:**
   - Documentar el código y crear un README detallado.
   - Preparar una presentación explicativa para público no técnico.
   - Presentar el código y su funcionamiento a un público técnico, explicando las decisiones de diseño y los desafíos encontrados.


# App desarrollada: Frases Célebres

## Descripción

Esta aplicación de Streamlit permite a los usuarios buscar acceder a la información de frases y autores del sitio https://quotes.toscrape.com/ en un formato diferente. Permite filtrar por autor y por tag. También proporciona estadísticas del sitio. Está diseñada para mostrar la aplicación de la técnica de Web Scraping.

## Características

- **Interfaz de usuario intuitiva**: Permite buscar frases, autores, filtrar por autor y por tag.
- **Visualizaciones interactivas**: Muestra gráficos y datos de manera dinámica.


## Instalación

Para ejecutar esta aplicación, sigue estos pasos:

1. Clona el repositorio:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_DEL_REPOSITORIO>
    ```

2. Crea un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv env
    source env/bin/activate  # En Windows usa `env\Scripts\activate`
    ```

3. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

Para ejecutar la aplicación, usa el siguiente comando:

```bash
streamlit run app.py
