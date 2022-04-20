import os
import re
import subprocess
import sys
import requests


from colorama import Fore
from bs4 import BeautifulSoup

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}

def update_not_seen_list():

    film_non_visti = []

    pattern = re.compile('\(visto\)$')

    for line in open('input-file/datas.txt'):
        if not re.findall(pattern, line):
            film_non_visti.append(line)

    return film_non_visti

def get_main_torrents_data(content_page):
    torrents_data = []  # Un torrent per riga, ogni riga con le seguenti colonne: TITOLO | SIZE | SEED | LEECH | URL

    titles = []
    sizes = []
    seeds = []
    leeches = []
    urls = []

    soup = BeautifulSoup(content_page, 'html.parser')

    table_rows = soup.findAll("tr")

    for row in table_rows:
        if row.find("th") is None:
            titles.append(row.find("td", {"class": "coll-1"}).findAll("a")[1])
            sizes.append(row.find("td", {"class": "coll-4"}))
            seeds.append(row.find("td", {"class": "coll-2"}))
            leeches.append(row.find("td", {"class": "coll-3"}))
            urls.append(row.find("td", {"class": "coll-1"}).findAll("a")[1]["href"])

    title_pattern = re.compile('^<a href=".+">(.+)</a>.*')
    size_pattern = re.compile('^<td class=".+">(.+)<span class=".+">.+</span></td>')
    seed_leech_pattern = re.compile('^<td class=".+">(.+)</td>')

    title_matches = []
    size_matches = []
    seed_matches = []
    leech_matches = []

    for line in titles:
        title_matches.append(re.finditer(title_pattern, str(line)))
    for line in sizes:
        size_matches.append(re.finditer(size_pattern, str(line)))
    for line in seeds:
        seed_matches.append(re.finditer(seed_leech_pattern, str(line)))
    for line in leeches:
        leech_matches.append(re.finditer(seed_leech_pattern, str(line)))

    # Riciclo variabili
    titles = []
    sizes = []
    seeds = []
    leeches = []

    for match in title_matches:
        for line in match:
            titles.append(line.group(1))  # La posizione 1 corrisponde a quella del titolo!
    for match in size_matches:
        for line in match:
            sizes.append(line.group(1))  # La posizione 1 corrisponde a quella della size!
    for match in seed_matches:
        for line in match:
            seeds.append(line.group(1))  # La posizione 1 corrisponde a quella del seed!
    for match in leech_matches:
        for line in match:
            leeches.append(line.group(1))  # La posizione 1 corrisponde a quella della leech!

    torrents_data.append(titles)
    torrents_data.append(sizes)
    torrents_data.append(seeds)
    torrents_data.append(leeches)
    torrents_data.append(urls)

    # Risoluzione titoli tagliati
    for i in range(len(torrents_data[0])):
        if '...' in torrents_data[0][i]:
            torrents_data[0][i] = re.split(r'\/' ,torrents_data[4][i])[3]

    return torrents_data

def get_number_of_results(film_title):
    pages = getAllPagesWithResults(film_title, proxy_enabled=False, manual_proxies=False, auto_proxy_enabled=False, auto_proxies=False)

    number_of_results = 0
    
    for page in pages:
        soup = BeautifulSoup(page.content, 'html.parser')
        table_rows = soup.findAll("tr")

        number_of_results += (len(table_rows) - 1)

    return number_of_results

def open_magnet(magnet):
    """Open magnet according to os."""
    if sys.platform.startswith('linux'):
        subprocess.Popen(['xdg-open', magnet],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif sys.platform.startswith('win32'):
        os.startfile(magnet)
    elif sys.platform.startswith('cygwin'):
        os.startfile(magnet)
    elif sys.platform.startswith('darwin'):
        subprocess.Popen(['open', magnet],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        subprocess.Popen(['xdg-open', magnet],stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_magnet(content_torrent_page):

    soup = BeautifulSoup(content_torrent_page, 'html.parser')

    list_items = soup.findAll("li")
    for item in list_items:
        anchor = item.find("a")
        if anchor is not None and anchor.text == "Magnet Download":
            magnet_link = anchor['href']
            break

    return magnet_link

def getSSLProxyList():
    try:
        content_page = requests.get('https://www.sslproxies.org/').content

        soup = BeautifulSoup(content_page, 'html.parser')

        print(Fore.LIGHTYELLOW_EX + "Lista proxy caricata con successo!\n" + Fore.RESET)

        return re.findall(r'(\d+\.\d+\.\d+\.\d+\:\d+)', str(soup))
    except: 
        print('Impossibile raggiungere la fonte dai cui prelevare la lista dei Proxy!')

def existingPage(url):
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    if re.findall('Bad search request', str(soup)) or re.findall('No results were returned. Please refine your search', str(soup)):
        return False
    
    return True

def getAllPagesWithResults(film_to_search, proxy_enabled, manual_proxies, auto_proxy_enabled, auto_proxies):
    pages = []

    page_number = 1

    url = ('https://1337x.to/search/' + film_to_search + '+ITA/'+ str(page_number) +'/')

    while existingPage(url):
        if proxy_enabled:
            page = requests.get(url, headers=headers, proxies=manual_proxies) 
        elif auto_proxy_enabled:
            page = requests.get(url, headers=headers, proxies=auto_proxies)
        else:
            page = requests.get(url, headers=headers)

        pages.append(page)

        page_number += 1

        url = ('https://1337x.to/search/' + film_to_search + '+ITA/'+ str(page_number) +'/')

    return pages