import requests
from bs4 import BeautifulSoup
import csv, time, re
from datetime import datetime

CATEGORIES = [
    '/szerelveny/hegesztheto-acel-idom',
    '/szerelveny/forraszthato-rez-idom',
    '/szerelveny/gazbekotes',
    '/szerelveny/aga-gebo-acelcso-idomok',
    '/szerelveny/hidraulikus-valto',
    '/szerelveny/hocserelo',
    '/szerelveny/hidraulikusan-kiegyenlitett-oszto',
    '/szerelveny/kazantolto-csap',
    '/szerelveny/keveroszelep-allitomotor-szabalyzas',
    '/szerelveny/nyomascsokkento',
    '/szerelveny/nyomasmero-homero',
    '/szerelveny/muanyag-es-otretegu-cso/padlofutes-cso',
    '/szerelveny/press-idom/pe-hd-sutheto-idom',
    '/spl/601898/PPR-idom',
    '/szerelveny/radiatorszelep-termofej',
    '/szerelveny/szifon',
    '/szerelveny/szigeteles',
    '/Tolozar',
    '/szerelveny/visszacsapo-szelep-labszelep',
    '/szerelveny/vizfocsap-fagycsap',
    '/szerelveny/vizora-szerelvenyek',
    '/szerelveny/vizszuro',
    '/szerszam',
    '/klima-es-legkondicionalo-berendezesek/klimaszerelesi-anyagok',
    '/gazkazan/baxi-kazan',
]
BASE_URL = 'https://www.kazanwebshop.hu'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.kazanwebshop.hu/', 'Accept-Language': 'hu-HU,hu;q=0.9'}

def get_stock_from_page(html):
    parser = BeautifulSoup(html, 'html.parser')
    products = []
    for h2 in parser.find_all('h2'):
        a = h2.find('a')
        if not a: continue
        block = h2.find_parent('li') or h2.find_parent('article') or h2.parent.parent
        if not block: continue
        block_text = block.get_text()
        img = block.find('img', src=re.compile(r'/img/15757/'))
        img_sku = ''
        if img and img.get('src'):
            m = re.search(r'/img/15757/([^/]+)/', img['src'])
            if m: img_sku = m.group(1)
        href = a.get('href', '')
        m = re.search(r'/spd/([^/]+)/', href)
        url_sku = m.group(1) if m else ''
        sku = img_sku or url_sku
        if not sku: continue
        in_stock = 'Raktaron' in block_text or 'Raktaron' in block_text
        products.append({'sku': sku, 'stock': 5000 if in_stock else 0})
    return products

def scrape_category(cat_url):
    products = {}
    session = requests.Session()
    for page in range(1, 20):
        url = BASE_URL + cat_url if page == 1 else BASE_URL + cat_url + f',{page}'
        try:
            r = session.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200: break
            prods = get_stock_from_page(r.text)
            if not prods: break
            for p in prods: products[p['sku']] = p['stock']
            time.sleep(0.5)
        except Exception as e:
            print(f'Hiba: {e}'); break
    return products

def main():
    all_products = {}
    for cat in CATEGORIES:
        print(f'Kategoria: {cat}')
        prods = scrape_category(cat)
        all_products.update(prods)
        time.sleep(1)
    with open('keszlet.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Cikkszam', 'Raktarkeszlet'])
        for sku, stock in sorted(all_products.items()):
            writer.writerow([sku, stock])
    print(f'Keszlet: {len(all_products)} termek')

if __name__ == '__main__': main()
