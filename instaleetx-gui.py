from cgitb import text
from faulthandler import disable
import socket
import webbrowser
import requests
import PySimpleGUI as sg
import colorama

from core import *

def serviceStatus():
    leetx_status = ''
    
    try:
        if socket.gethostbyname('1337x.to') == '83.224.65.79':
            leetx_status = 'AGCOM LOCK'
        elif requests.get('https://1337x.to/', timeout=10).status_code == 200 and socket.gethostbyname('1337x.to') != '83.224.65.79': #AGCOM IP
            leetx_status = 'ONLINE'
        else:
            leetx_status = 'OFFLINE'
    except:
        leetx_status = 'OFFLINE'

    return leetx_status

class GUI:

    sg.theme('DarkPurple4')
    data = None

    def main_menu(self):

        leetx_status = serviceStatus()
        status_bar_text_color = ''

        if leetx_status == 'ONLINE':
            status_bar_text_color='green'
        elif leetx_status == 'AGCOM LOCK':
            status_bar_text_color='yellow'
        else:
            status_bar_text_color='red'


        layout = [[sg.Image(filename='resources/logo.png')],
                  [sg.Button('Mostra i film da vedere', size=65, font=1)],
                  [sg.Button('Scarica un film', size=65, font=1)],
                  [sg.Button('ESCI', size=65, font=1)],
                  [sg.StatusBar('Dev By @DavidG33k                                                              Stato 1337x.to: ' + leetx_status, key='-STATUSBAR-', font=1, pad=(20,15), text_color=status_bar_text_color)]]

        window = sg.Window("InstaLeetx", layout, element_justification='c')


        while True:
            
            event, values = window.read()

            if event == 'Mostra i film da vedere':
                self.data = update_not_seen_list()

                window.close()
                self.showNotSeenMovies()
                break

            if event == 'Scarica un film' and leetx_status == 'ONLINE':
                self.data = update_not_seen_list()
                if len(self.data) == 0:
                    sg.Popup('Nessun film da scaricare!', font=1)
                else:
                    window.close()
                    self.showMovieWithNumberOfResults()
                    break
            elif event == 'Scarica un film' and leetx_status != 'ONLINE':
                sg.Popup('1337x.to non raggiungibile!', font=1)

            if event == 'ESCI' or event == sg.WIN_CLOSED:
                break

        window.close()
         
    def showNotSeenMovies(self):

        headings = ['   TITOLO    ']

        converted_data = []
        for film_title in self.data:
            converted_data.append( [film_title] )

        layout = [[sg.Table(values=converted_data[0:][:],
                            headings=headings,
                            alternating_row_color='#46314A',
                            max_col_width=100,
                            def_col_width=70,
                            auto_size_columns=False,
                            display_row_numbers=True,
                            justification='center',
                            num_rows=10,
                            key='-TABLE-',
                            enable_events=True,
                            row_height=45,
                            font=1,
                            expand_x=True,
                            expand_y=True,
                            text_color='white',)],
                 [sg.Button('Aggiungi', font=1), sg.Button('Rimuovi', font=1, disabled=True), sg.Button('Segna come visto', font=1, disabled=True), sg.Button('Trailers', font=1, disabled=True)]
                ]

        window = sg.Window("InstaLeetx", layout, resizable=True)

        while True:
            event, values = window.read()

            if event == 'Aggiungi':
                window['Aggiungi'].update(disabled=True)
                window['Rimuovi'].update(disabled=True)
                window['Segna come visto'].update(disabled=True)
                window['Trailers'].update(disabled=True)

                self.addFilm()

                # Aggiorno tabella
                self.data = update_not_seen_list()
                updated_converted_data = []
                for film_title in self.data:
                    updated_converted_data.append( [film_title] )
                window['-TABLE-'].update(values=updated_converted_data[0:][:])

                window['Aggiungi'].update(disabled=False)
                window['Rimuovi'].update(disabled=False)
                window['Segna come visto'].update(disabled=False)
                window['Trailers'].update(disabled=False)

            if event == 'Rimuovi' and str(values['-TABLE-']) != '[]':
                if(sg.popup_ok_cancel('Sei sicuro di voler rimuovere il film dalla lista?', font=1, no_titlebar=True) == 'OK'):

                    self.removeFilm(values['-TABLE-'])

                    # Aggiorno tabella
                    self.data = update_not_seen_list()
                    updated_converted_data = []
                    for film_title in self.data:
                        updated_converted_data.append( [film_title] )
                    window['-TABLE-'].update(values=updated_converted_data[0:][:])

                    window['Rimuovi'].update(disabled=True)
                    window['Segna come visto'].update(disabled=True)
                    window['Trailers'].update(disabled=True)
                    values['-TABLE-'] = '[]'

            if event == 'Segna come visto' and str(values['-TABLE-']) != '[]':
                self.markAsSeen(values['-TABLE-'])

                # Aggiorno tabella
                self.data = update_not_seen_list()
                updated_converted_data = []
                for film_title in self.data:
                    updated_converted_data.append( [film_title] )
                window['-TABLE-'].update(values=updated_converted_data[0:][:])

                window['Rimuovi'].update(disabled=True)
                window['Segna come visto'].update(disabled=True)
                window['Trailers'].update(disabled=True)
                values['-TABLE-'] = '[]'

            if event == 'Trailers':
                self.openTrailers(values['-TABLE-'])

            if event == '-TABLE-' and str(values['-TABLE-']) != '[]':
                window['Rimuovi'].update(disabled=False)
                window['Segna come visto'].update(disabled=False)
                window['Trailers'].update(disabled=False)

                

            if event == sg.WIN_CLOSED:
                window.close()
                self.main_menu()
                break

        window.close()

    def addFilm(self):
        layout = [[sg.Text('Inserisci il titolo:', font=1)],
                  [sg.InputText(key='-TITLE-')],
                  [sg.Button('Aggiungi', font=1)]]

        window = sg.Window("InstaLeetx", layout, element_justification='c')

        while True:
            event, values = window.read()

            if event == 'Aggiungi':
                if len(values['-TITLE-']) != 0:
                    with open('input-file/datas.txt', 'a') as file:
                        file.write(str(values['-TITLE-']) + '\n')

                    sg.Popup('Titolo aggiunto con successo!', font=1)
                    window.close()
                    break
                else:
                    sg.Popup('Non hai inserito alcun titolo!', font=1)

            if event == sg.WIN_CLOSED:
                window.close()
                break

        window.close()

    def removeFilm(self, index_to_remove):
        index_to_remove = re.sub(r'^\[', '', str(index_to_remove))
        index_to_remove = re.sub(r'\]$', '', index_to_remove)
        
        index_to_remove = int(index_to_remove)

        film_to_remove = ''

        for i, line in enumerate(self.data):
            if i == index_to_remove:
                film_to_remove = line

        with open("input-file/datas.txt", "r") as f:
            lines = f.readlines()

        with open("input-file/datas.txt", "w") as f:
            for i, line in enumerate(lines):
                if line != film_to_remove:
                    f.write(line)

    def markAsSeen(self, index_to_mark):
        index_to_mark = re.sub(r'^\[', '', str(index_to_mark))
        index_to_mark = re.sub(r'\]$', '', index_to_mark)
        
        index_to_mark = int(index_to_mark)
        
        for i, line in enumerate(self.data):
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

    def openTrailers(self, index_to_open):
        index_to_open = re.sub(r'^\[', '', str(index_to_open))
        index_to_open = re.sub(r'\]$', '', index_to_open)
        
        index_to_open = int(index_to_open)
        
        for i, line in enumerate(self.data):
            if i == index_to_open:
                film_to_open = line

        film_to_open = film_to_open.rstrip("\n")

        webbrowser.open('https://www.youtube.com/results?search_query=' + film_to_open + ' trailer')

    def showMovieWithNumberOfResults(self):
        headings = ['   TITOLO    ','   RISULTATI    ']

        converted_data = []
        for film_title in self.data:
            converted_data.append( [film_title, str(get_number_of_results(film_title.rstrip("\n")))] )

        layout = [[sg.Table(values=converted_data[0:][:],
                            headings=headings,
                            alternating_row_color='#46314A',
                            auto_size_columns=True,
                            display_row_numbers=True,
                            justification='center',
                            num_rows=10,
                            key='-TABLE-',
                            enable_events=True,
                            row_height=45,
                            font=1,
                            text_color='white',)],
                 [sg.Button('Vedi risultati', font=1, disabled=True), sg.Button('Trailers', font=1, disabled=True)]
                ]

        window = sg.Window("InstaLeetx", layout)

        while True:
            event, values = window.read()

            if event == '-TABLE-' and str(values['-TABLE-']) != '[]':
                window['Vedi risultati'].update(disabled=False)
                window['Trailers'].update(disabled=False)

            if event == 'Vedi risultati':
                index_to_search = re.sub(r'^\[', '', str(values['-TABLE-']))
                index_to_search = re.sub(r'\]$', '', index_to_search)
        
                index_to_search = int(index_to_search)

                if int(converted_data[index_to_search][1]) != 0:
                    self.showMovieResults(index_to_search)
                else:
                    sg.Popup('Nessun risultato al momento!', font=1)

            if event == 'Trailers':
                self.openTrailers(values['-TABLE-'])

            if event == sg.WIN_CLOSED:
                window.close()
                self.main_menu()
                break

        window.close

    def showMovieResults(self, index_to_search):

        for i, line in enumerate(self.data):
            if i == index_to_search:

                film_to_search = line.rstrip("\n")

                page_number = 1

                url = ('https://1337x.to/search/' + film_to_search + '+ITA/'+ str(page_number) +'/')

                pages = getAllPagesWithResults(film_to_search, False, False, False, False)


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

                converted_data = []
                for i in range(len(torrents_data[0])):
                    converted_data.append( [torrents_data[0][i], torrents_data[1][i], torrents_data[2][i], torrents_data[3][i]] )

        headings = ['   TORRENT    ', '    DIMENSIONE    ', '    SEEDERS    ', '    LEECHERS    ']

        layout = [[sg.Table(values=converted_data,
                            headings=headings,
                            alternating_row_color='#46314A',
                            auto_size_columns=False,
                            col_widths=[80, 15, 15, 15],
                            display_row_numbers=True,
                            justification='center',
                            expand_x=True,
                            expand_y=True,
                            num_rows=20,
                            key='-TABLE-',
                            enable_events=True,
                            row_height=30,
                            font=1,
                            text_color='white',)],
                 [sg.Button('Scarica', font=1, disabled=True)]
                ]

        window = sg.Window("InstaLeetx", layout, resizable=True)

        while True:
            event, values = window.read()

            if event == 'Scarica':
                torrent_chosen = re.sub(r'^\[', '', str(values['-TABLE-']))
                torrent_chosen = re.sub(r'\]$', '', torrent_chosen)
        
                index_to_search = int(index_to_search)

                torrent_url = ('https://1337x.to' + torrents_data[4][int(torrent_chosen)])

                torrent_page = requests.get(torrent_url, headers=headers)

                if torrent_page.status_code == 200:
                    magnet_link = get_magnet(torrent_page.content)
                    open_magnet(magnet_link)
                    window.close()
                    break
                else:
                    sg.Popup('Errore imprevisto. Riprova!')
     
            if event == '-TABLE-' and str(values['-TABLE-']) != '[]':
                window['Scarica'].update(disabled=False)

            if event == sg.WIN_CLOSED:
                window.close()
                break


def main(name: str):
    if name == '__main__':
        GUI().main_menu()


main(__name__)