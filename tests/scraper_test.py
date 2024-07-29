import pytest
from unittest.mock import patch, Mock
from scraper import Scraper
import pandas as pd
import os

"""
para ejecutar indicar: pytest en el directorio raiz

"""


@pytest.fixture
def scraper():
    base_url = "https://quotes.toscrape.com/"
    return Scraper(base_url)

@patch('scraper.requests.get')
def test_get_author_details(mock_get, scraper):
    # Configurar el mock para la respuesta de requests
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <span class="author-born-date">January 1, 1900</span>
        <span class="author-born-location">in Testland</span>
        <div class="author-description">Test author description.</div>
    </html>
    """
    mock_get.return_value = mock_response

    # URL de prueba
    test_url = scraper.base_url + 'author/test_author'
    details = scraper.get_author_details(test_url)

    # Verificar que los detalles del autor se extrajeron correctamente
    assert details['author-born-date'] == 'January 1, 1900'
    assert details['author-born-location'] == 'in Testland'
    assert details['author-description'] == 'Test author description.'

@patch('scraper.requests.get')
def test_scrape_quotes(mock_get, scraper):
    # Configurar el mock para la respuesta de requests
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <div class="quote">
            <span class="text">“Test quote”</span>
            <small class="author">Test Author</small>
            <a href="/author/test_author">(author details)</a>
            <div class="tags">
                <a class="tag">test</a>
                <a class="tag">quote</a>
            </div>
        </div>
    </html>
    """
    mock_get.return_value = mock_response

    # Probar el scraping
    frases_df, tags_df = scraper.scrape_quotes()

    # Verificar que las frases y tags se extrajeron correctamente
    assert len(frases_df) == 1
    assert len(tags_df) == 2
    assert frases_df.iloc[0]['frase_texto'] == '“Test quote”'
    assert 'test' in frases_df.iloc[0]['Tags']
    assert 'quote' in frases_df.iloc[0]['Tags']

def test_save_to_excel(scraper):
    # Crear dataframes de prueba
    frases_df = pd.DataFrame({
        'frase_texto': ['Test quote'],
        'autor_nombre': ['Test'],
        'autor_apellido': ['Author'],
        'Tags': [['test', 'quote']],
        'Tags_IDs': [[1, 2]]
    })

    tags_df = pd.DataFrame({
        'tag_texto': ['test', 'quote'],
        'tag_id': [1, 2]
    })

    output_filename = 'test_output.xlsx'

    # Probar guardar a Excel
    try:
        scraper.save_to_excel(frases_df, tags_df, output_filename)
        result = os.path.exists(output_filename)
    except Exception as e:
        result = False
        print(f"Error al guardar el archivo Excel: {e}")
    
    # Limpiar el archivo después de la prueba
    if os.path.exists(output_filename):
        os.remove(output_filename)
    
    assert result

