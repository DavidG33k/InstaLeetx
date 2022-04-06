import os
import platform
import re
import subprocess
import sys
import socket
import requests
import colorama
import configparser
import time

from colorama import Fore
from bs4 import BeautifulSoup

def show_status(leetx_status, proxy_enabled, manual_proxies, auto_proxy_enabled):
    auto_proxies = {}

    if proxy_enabled: # Provo a raggiungerlo con proxy manuale
        try:
            r = requests.get('https://1337x.to/', proxies=manual_proxies, headers=headers, timeout=10)
            if r.status_code == 200:
                leetx_status = True
        except:
            pass

        if not leetx_status:
            proxy_enabled = False
            print('Server Proxy non raggiungibile! Aprire il file "input-file/proxy.ini" per risolvere il problema.')

    elif auto_proxy_enabled: # Provo a raggiungerlo con proxy automatico
        list_of_proxies = getSSLProxyList()
        
        for proxy in list_of_proxies:
            auto_proxies = {
                'https': proxy,
                'http': proxy
            }
        
            print("Tentativo connessione con: " + proxy)

            try:
                r = requests.get('https://1337x.to/', proxies=auto_proxies, headers=headers, timeout=10)
                print('Status code: ' + r.status_code)
                if r.status_code == 200:
                    print('Successo per ' + proxy + '\n')
                    leetx_status = True
                    break
            except:
                pass        
                    
        if not leetx_status:
            auto_proxy_enabled = False
            print(Fore.LIGHTYELLOW_EX + 'Nessun proxy attualmente funzionante.\n' + Fore.RESET)

    else: # Provo a raggiungerlo senza proxy
        try:
            if requests.get('https://1337x.to/', timeout=10).status_code == 200 and socket.gethostbyname('1337x.to') != '83.224.65.79': #AGCOM IP
                leetx_status = True
        except:
            pass



    try:
        if leetx_status:
            print('1337x.to [' + Fore.LIGHTGREEN_EX + 'ONLINE' + Fore.RESET + ']')
        elif socket.gethostbyname('1337x.to') == '83.224.65.79':  # AGCOM IP
            print('1337x.to [' + Fore.LIGHTYELLOW_EX + 'AGCOM LOCK' + Fore.RESET + ']')
        else:
            print('1337x.to [' + Fore.LIGHTRED_EX + 'OFFLINE' + Fore.RESET + ']')
    except:
        print('1337x.to [' + Fore.LIGHTRED_EX + 'OFFLINE' + Fore.RESET + ']')

    if proxy_enabled:
        print('Proxy manuale [' + Fore.LIGHTGREEN_EX + 'ABILITATO' + Fore.RESET + ']')
    else:
        print('Proxy manuale [' + Fore.LIGHTRED_EX + 'DISABILITATO' + Fore.RESET + ']')
    
    if auto_proxy_enabled:
        print('Proxy automatico [' + Fore.LIGHTGREEN_EX + 'ABILITATO' + Fore.RESET + ']')
    else:
        print('Proxy automatico [' + Fore.LIGHTRED_EX + 'DISABILITATO' + Fore.RESET + ']')



    return leetx_status, proxy_enabled, auto_proxy_enabled, auto_proxies

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

    return torrents_data

def get_number_of_results(film_title):
    pages = getAllPagesWithResults(film_title, proxy_enabled, manual_proxies, auto_proxy_enabled, auto_proxies)

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

def clean_terminal():
    if platform.system() == "Windows":
        subprocess.Popen("cls", shell=True).communicate()
    else:  # Linux and Mac
        print("\033c", end="")

def print_logo():
    print('\n'
          ' /$$$$$$                       /$$               /$$                             /$$                       '+Fore.LIGHTGREEN_EX+'/$$  '+Fore.LIGHTWHITE_EX+'/$$$'+Fore.LIGHTRED_EX+'$$$'+Fore.RESET+' \n'
          '|_  $$_/                      | $$              | $$                            | $$                      '+Fore.LIGHTGREEN_EX+'/$$/ '+Fore.LIGHTWHITE_EX+'/$$__'+Fore.LIGHTRED_EX+'  $$'+Fore.RESET+'\n'
          '  | $$   /$$$$$$$   /$$$$$$$ /$$$$$$    /$$$$$$ | $$        /$$$$$$   /$$$$$$  /$$$$$$  /$$   /$$        '+Fore.LIGHTGREEN_EX+'/$$/ '+Fore.LIGHTWHITE_EX+'|__/  '+Fore.LIGHTRED_EX+'\ $$'+Fore.RESET+'\n'
          '  | $$  | $$__  $$ /$$_____/|_  $$_/   |____  $$| $$       /$$__  $$ /$$__  $$|_  $$_/ |  $$ /$$/       '+Fore.LIGHTGREEN_EX+'/$$/     '+Fore.LIGHTWHITE_EX+'/$$'+Fore.LIGHTRED_EX+'$$$/'+Fore.RESET+'\n'
          '  | $$  | $$  \ $$|  $$$$$$   | $$      /$$$$$$$| $$      | $$$$$$$$| $$$$$$$$  | $$    \  $$$$/       '+Fore.LIGHTGREEN_EX+'|  $$    '+Fore.LIGHTWHITE_EX+'|___'+Fore.LIGHTRED_EX+'  $$'+Fore.RESET+'\n'
          '  | $$  | $$  | $$ \____  $$  | $$ /$$ /$$__  $$| $$      | $$_____/| $$_____/  | $$ /$$ >$$  $$        '+Fore.LIGHTGREEN_EX+'\  $$  '+Fore.LIGHTWHITE_EX+'/$$  '+Fore.LIGHTRED_EX+'\ $$'+Fore.RESET+'\n'
          ' /$$$$$$| $$  | $$ /$$$$$$$/  |  $$$$/|  $$$$$$$| $$$$$$$$|  $$$$$$$|  $$$$$$$  |  $$$$//$$/\  $$        '+Fore.LIGHTGREEN_EX+'\  $$'+Fore.LIGHTWHITE_EX+'|  $$$'+Fore.LIGHTRED_EX+'$$$/'+Fore.RESET+'\n'
          '|______/|__/  |__/|_______/    \___/   \_______/|________/ \_______/ \_______/   \___/ |__/  \__/         '+Fore.LIGHTGREEN_EX+'\__/ '+Fore.LIGHTWHITE_EX+'\____'+Fore.LIGHTRED_EX+'__/ '+Fore.RESET+'\n'
          '                                                                                                       '+Fore.LIGHTGREEN_EX+'Dev by ' + Fore.LIGHTWHITE_EX + '@David'+Fore.LIGHTRED_EX+'G33k' + Fore.RESET + '\n'
          )

def print_menu():
    print('________________________________________________________________________________________________________________________\n')
    print('             ' + Fore.LIGHTMAGENTA_EX + 'MENU' + Fore.RESET)
    choice = input('1 - mostra i film non visti\n'
                   '2 - aggiungi un film alla lista\n'
                   '3 - rimuovi un film dalla lista\n'
                   '4 - segna un film come visto\n'
                   '5 - scarica un film\n'
                   '6 - abilita/disabilita Proxy automatico\n'
                   '7 - abilita/disabilita Proxy manuale\n'
                   '0 - ESCI\n')
    print('________________________________________________________________________________________________________________________\n')

    return choice

def print_warnings():
    print('                                            ' + Fore.LIGHTRED_EX + 'ATTENZIONE!' + Fore.RESET )
    print('InstaLeetx è un progetto italiano e open source ideato con il solo scopo di apprendere nuove skills in ambito web\n'
          'scraping e security e condividere le conoscenze apprese con la community. Il software in questione si occupa\n'
          'esclusivamente del prelevamento dei dati da siti pre esistenti con l\'obbiettivo di automatizzare l\'operazione.\n'
          'Il sottoscritto NON si assume ,quindi, alcuna responsabilità di come questo venga utilizzato, ne per danni a cose\n'
          'o persone. Ricordo che il download di contenuti di cui non si è ufficialmente in possesso è da intendere come\n'
          'attività pirata e quindi ILLECITA!\n\n')
    print('                          Sarai rediretto al menu tra '+ Fore.LIGHTGREEN_EX + '5' + Fore.RESET + ' secondi!')

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
        
        
    
colorama.init()

config = configparser.ConfigParser()
config.read('input-file/proxy.ini')

film_non_visti = update_not_seen_list()

leetx_status = False
proxy_enabled = False
auto_proxy_enabled = False

manual_proxies = {
    'https': config['DEFAULT']['PROXY'],
    'http': config['DEFAULT']['PROXY']
}
auto_proxies = {}

headers = {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}

clean_terminal()

print_logo()

print_warnings()

time.sleep(5)

clean_terminal()

print_logo()

leetx_status, proxy_enabled, auto_proxy_enabled, auto_proxies = show_status(leetx_status, proxy_enabled, manual_proxies, auto_proxy_enabled)

time.sleep(1)

choice = None

while choice != str(0):

    # Mostra i film non visti
    if choice == str(1):
        clean_terminal()
        print_logo()

        if len(film_non_visti) == 0:
            print('Nessun film in lista!')
        else:
            for i, line in enumerate(film_non_visti):
                print('%s) %s' %(i, line))

    # Aggiungi un film alla lista
    elif choice == str(2):
        clean_terminal()
        print_logo()

        film_name = input('Inserisci il titolo del film: ')

        if not film_name == '':
            with open('input-file/datas.txt', 'a') as file:
                file.write(str(film_name) + '\n')

            film_non_visti = update_not_seen_list()

            clean_terminal()
            print_logo()
        else:
            clean_terminal()
            print_logo()
            print('Non è stato inserito nulla!')

    # Rimuovi un film dalla lista
    elif choice == str(3):
        clean_terminal()
        print_logo()

        for i, line in enumerate(film_non_visti):
            print('%s) %s' %(i, line))

        if(len(film_non_visti) == 0):
            print('Nessun film in lista!')
        else:
            index_to_remove = input('\nNumero del film da rimuovere (lascia vuoto per tornare al menu): ')

            try:
                index_to_remove = int(index_to_remove)
            except:
                clean_terminal()
                print_logo()
                print('Riprova inserendo un numero!')

            if isinstance(index_to_remove, int):
                if index_to_remove != '' and int(index_to_remove) < len(film_non_visti):
                    for i, line in enumerate(film_non_visti):
                        if i == index_to_remove:
                            film_to_remove = line

                    with open("input-file/datas.txt", "r") as f:
                        lines = f.readlines()

                    with open("input-file/datas.txt", "w") as f:
                        for i, line in enumerate(lines):
                            if line != film_to_remove:
                                f.write(line)

                    film_non_visti = update_not_seen_list()

                    clean_terminal()
                    print_logo()
                else:
                    clean_terminal()
                    print_logo()
                    print('Nessun film selezionato!')

    # Segna un film come visto
    elif choice == str(4):
        clean_terminal()
        print_logo()

        for i, line in enumerate(film_non_visti):
            print('%s) %s' %(i, line))

        if len(film_non_visti) == 0:
            print('Nessun film in lista!')
        else:
            index_to_mark = input('\nNumero del film visto: ')

            try:
                index_to_mark = int(index_to_mark)
            except:
                clean_terminal()
                print_logo()
                print('Riprova inserendo un numero!')

            if isinstance(index_to_mark, int):
                if index_to_mark != '' and int(index_to_mark) < len(film_non_visti):
                    for i, line in enumerate(film_non_visti):
                        if i == index_to_mark:
                            film_to_mark = line

                    film_to_mark = film_to_mark.rstrip("\n")

                    f = open("input-file/datas.txt", "rt")
                    new_data = f.read()
                    new_data = new_data.replace(film_to_mark, film_to_mark + ' (visto)')
                    f.close()
                    f = open("input-file/datas.txt", "wt")
                    f.write(new_data)
                    f.close()

                    film_non_visti = update_not_seen_list()

                    clean_terminal()
                    print_logo()
                else:
                    clean_terminal()
                    print_logo()
                    print('Nessun film selezionato!.')

    # Scarica un film
    elif choice == str(5):
        clean_terminal()
        print_logo()

        if leetx_status:

            for i, line in enumerate(film_non_visti):
                print('%s) %s - %s' % (i, line.rstrip("\n"), Fore.LIGHTYELLOW_EX + '[Risultati: ' + str(get_number_of_results(line.rstrip("\n"))) + ']\n' + Fore.RESET))

            if len(film_non_visti) == 0:
                print(Fore.LIGHTYELLOW_EX + 'Nessun film in lista!\n' + Fore.RESET)
            else:
                index_to_search = input('\nNumero del film da scaricare: ')

                try:
                    index_to_search = int(index_to_search)
                except:
                    clean_terminal()
                    print_logo()
                    print(Fore.LIGHTYELLOW_EX + 'Riprova inserendo un numero!' + Fore.RESET)

                if isinstance(index_to_search, int):
                    if index_to_search != '' and int(index_to_search) < len(film_non_visti):
                        for i, line in enumerate(film_non_visti):
                            if i == index_to_search:

                                film_to_search = line.rstrip("\n")

                                page_number = 1

                                url = ('https://1337x.to/search/' + film_to_search + '+ITA/'+ str(page_number) +'/')

                                pages = getAllPagesWithResults(film_to_search, proxy_enabled, manual_proxies, auto_proxy_enabled, auto_proxies)

                                clean_terminal()
                                print_logo()

                                torrents_data = None

                                for page in pages:
                                    page_torrents_data = get_main_torrents_data(page.content) 

                                    if torrents_data is None:
                                        torrents_data = page_torrents_data
                                    else:
                                        torrents_data[0] += (page_torrents_data[0])
                                        torrents_data[1] += (page_torrents_data[1])
                                        torrents_data[2] += (page_torrents_data[2])
                                        torrents_data[3] += (page_torrents_data[3])
                                        torrents_data[4] += (page_torrents_data[4])

                                if torrents_data is None:
                                    print(Fore.LIGHTYELLOW_EX+ 'Nessun risultato per adesso :(' + Fore.RESET)
                                else:
                                    for i, line in enumerate(torrents_data[0]):
                                        print('%s) %s' % (i, line))
                                        print('         ' + Fore.LIGHTCYAN_EX + torrents_data[1][i] + '          ' + Fore.LIGHTGREEN_EX + 'S: ' + torrents_data[2][i] + '          ' + Fore.LIGHTRED_EX + 'L: ' + torrents_data[3][i] + Fore.RESET + '\n')
                                    
                                    torrent_chosen = input('\nNumero del torrent (lascia vuoto per tornare al menu): ')

                                    try:
                                        torrent_chosen = int(torrent_chosen)
                                    except:
                                        clean_terminal()
                                        print_logo()
                                        print(Fore.LIGHTYELLOW_EX + 'Riprova inserendo un numero!' + Fore.RESET)

                                    if isinstance(torrent_chosen, int):
                                        if torrent_chosen != '' and int(torrent_chosen) < len(torrents_data[0]):
                                            torrent_url = ('https://1337x.to' + torrents_data[4][int(torrent_chosen)])

                                            if proxy_enabled:
                                                torrent_page = requests.get(torrent_url, headers=headers, proxies=manual_proxies)
                                            elif auto_proxy_enabled:
                                                torrent_page = requests.get(torrent_url, headers=headers, proxies=auto_proxies)
                                            else:
                                                torrent_page = requests.get(torrent_url, headers=headers)

                                            if torrent_page.status_code == 200:
                                                magnet_link = get_magnet(torrent_page.content)
                                                open_magnet(magnet_link)
                                                clean_terminal()
                                                print_logo()
                                        else:
                                            clean_terminal()
                                            print_logo()
                                            print(Fore.LIGHTYELLOW_EX + 'Scelta non valida!' + Fore.RESET)          
                    else:
                        clean_terminal()
                        print_logo()
                        print(Fore.LIGHTYELLOW_EX + 'Nessun film selezionato!' + Fore.RESET)
        else:
            clean_terminal()
            print_logo()
            print('\n' + Fore.LIGHTYELLOW_EX + '1337x.to non è al momento raggiungibile!' + Fore.RESET)

    # Abilita/disabilita proxy automatico
    elif choice == str(6):
        if proxy_enabled:
            proxy_enabled = False

        auto_proxy_enabled = not auto_proxy_enabled

        clean_terminal()
        print_logo()
        leetx_status, proxy_enabled, auto_proxy_enabled, auto_proxies = show_status(leetx_status, proxy_enabled, manual_proxies, auto_proxy_enabled)

    # Abilita/disabilita proxy manuale
    elif choice == str(7):
        if auto_proxy_enabled:
            auto_proxy_enabled = False

        proxy_enabled = not proxy_enabled

        clean_terminal()
        print_logo()
        leetx_status, proxy_enabled, auto_proxy_enabled, auto_proxies = show_status(leetx_status, proxy_enabled, manual_proxies, auto_proxy_enabled)

    elif(choice is not None):
        clean_terminal()
        print_logo()
        print('Scelta non valida!')

    choice = print_menu()