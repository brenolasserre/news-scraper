import requests
import random
from bs4 import BeautifulSoup
import concurrent.futures
import html
from flask import Flask, jsonify
from flask_compress import Compress

app = Flask(__name__)
Compress(app)

def extract_data_lanacion(url, max_headlines=3):
    response = requests.get(url)
    headlines = []
    soup = BeautifulSoup(response.text, 'html.parser')

    section = soup.find('div', {'id': 'content-main'})
    articles = section.find('div', {'class': 'row-gap-tablet-3'})

    idx = 0
    for card in articles.findAll('article', {'class': 'mod-article'}):
        if idx >= max_headlines:
            break
        idx += 1

        texto = card.find('section', {'class': 'mod-description'})
        media = card.find('div', {'class': 'content-media'})

        h = texto.find('h2').find('a').string
        f = texto.find('time')
        i = media.find('img')
        if h:
            img_url = i.attrs['src'].split('?')[0].replace(' ', '%20')
            headlines.append({
                'title': html.unescape(str(h)),
                'img': img_url,
                'time': f.text.strip()
            })
    return headlines

def extract_data_dolarhoy(url, max_headlines=3):
    response = requests.get(url)
    headlines = []
    soup = BeautifulSoup(response.text, 'html.parser')

    section = soup.find('section', {'class': 'tag'})
    articles = section.find('div', {'class': 'grid'})

    idx = 0
    for card in articles.findAll('div', {'class': 'item is-12'}):
        if idx >= max_headlines:
            break
        idx += 1

        texto = card.find('div', {'class': 'nota__body'})
        media = card.find('div', {'class': 'nota__media'})

        headerContainer = texto.find('div', {'class': 'nota__titulo'})
        h = headerContainer.find('h2').find('a').string
        i = media.find('amp-img')
        if h:
            img_url = i.attrs['src'].split('?')[0].replace(' ', '%20')
            headlines.append({
                'title': html.unescape(str(h)),
                'img': img_url,
            })
    return headlines

def download_pages(urls):
    responses = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(download_page, url): url for url in urls}
        for future in concurrent.futures.as_completed(futures):
            url = futures[future]
            try:
                responses[url] = future.result()
            except Exception as exc:
                print(f"{url} generated an exception: {exc}")
    return responses

def download_page(url):
    return requests.get(url)

def get_headline_list():
    max_headlines = 6
    urls = ["https://www.lanacion.com.ar/dolar-hoy/", "https://dolarhoy.com/tag/dolar"]
    page_responses = download_pages(urls)

    headlines = []
    for url, response in page_responses.items():
        if response.status_code == 200:
            if 'lanacion' in url:
                headlines += extract_data_lanacion(url, max_headlines=max_headlines // 2)
            elif 'dolarhoy' in url:
                headlines += extract_data_dolarhoy(url, max_headlines=max_headlines // 2)

    random.shuffle(headlines)
    return headlines

@app.route('/articulos')
def articulos():
    headlines = get_headline_list()
    lanacion_output = [{'source': 'La Nacion', 'title': x['title'], 'img': x['img']} for x in headlines[:6]]
    dolarhoy_output = [{'source': 'Dolar Hoy', 'title': x['title'], 'img': x['img']} for x in headlines[6:]]

    return jsonify(lanacion_output + dolarhoy_output)

if __name__ == '__main__':
    app.run(debug=True)
