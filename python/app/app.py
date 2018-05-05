from flask import Flask, render_template, json, request, redirect, session
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from collections import OrderedDict
import random

mysql = MySQL()
app = Flask(__name__)

# konfiguracje MySQL:
app.config['MYSQL_DATABASE_USER'] = 'pz2017_10'
app.config['MYSQL_DATABASE_PASSWORD'] = 'vV8bdtj2fGMhaG2u'
app.config['MYSQL_DATABASE_DB'] = 'pz2017_10'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 5432
app.secret_key = '329743bjshads93982472463246sas'
mysql.init_app(app)

def is_power2(n):
    n = n/2
    if n == 2:
        return True
    elif n > 2:
        is_power2(n)
    else:
        return False

def getMatchDetails(id_meczu, login):

    con = mysql.connect()  # lacze z baza danych
    cursor = con.cursor()
    cursor.callproc('sp_getMecz2', (id_meczu,))  # wywoluje procedure SQL, ktora pobiera mecz
    dane = cursor.fetchall()
    con.commit()

    data = dane[0][4]

    if dane[0][2] == login:
        przeciwnik = dane[0][3]  # zmienna przeciwnik zawiera login przeciwnika w danym meczu
    else:
        przeciwnik = dane[0][2]

    # zmienna punkty_meczu zawiera informacje czy uzytkownik zdobyl, czy stracil punkt [[1, 1 ,0, 0, 0,...], ...]
    przebieg_meczu = []
    # zmienne beda przechowywac dla kazdego setu ilosc zdobytych punktow przez gracza
    punkty_moje = {}
    punkty_przeciwnika = {}
    p_set = []
    wynik_meczu = [0, 0]  # zmienna przechowuje ilosc wygranych setow przez obu graczy
    id_turnieju = dane[0][1]


    if data:  # jeżeli mecz się odbył pobieram dane o punktach w tym meczu:
        # wywoluje w bazie procedure ktora dla danego meczu wyswietli punkty:
        cursor.callproc('sp_getPunkty', (id_meczu,))
        # pobrane z bazy dane zawieraja loginy graczy ktorzy zdobyli pojedynczy punkt
        # { {nr_setu, login1, id_meczu, }, {nr_setu,{...}} }
        dane2 = cursor.fetchall()
        con.commit()
        for j in dane2:  # zliczam punkty dla obu graczy
            if j[0] not in punkty_moje:  # jesli punkty dla tego setu nie sa liczone
                punkty_moje[j[0]] = 0  # punkty dla tego setu ustawiam na 0
                punkty_przeciwnika[j[0]] = 0
                przebieg_meczu.append(p_set)  # do przebiegu meczu dodaje poprzedni set
                p_set = []  # tworze pusty set, ktory bedzie zawieral przebieg gry [0, 1, 1, 0, ...]
            if j[1] == login:  # jesli punkt zdobyl gracz1 to dodaje mu punkt w tym secie
                punkty_moje[j[0]] += 1
                p_set.append(1)
            elif j[1] == przeciwnik:
                punkty_przeciwnika[j[0]] += 1
                p_set.append(0)
        przebieg_meczu.append(p_set)
        przebieg_meczu = przebieg_meczu[1:]

        for j in range(len(punkty_moje)):
            if punkty_moje[j + 1] > punkty_przeciwnika[j + 1]:
                wynik_meczu[0] += 1
            elif punkty_moje[j + 1] < punkty_przeciwnika[j + 1]:
                wynik_meczu[1] += 1

    cursor.close()
    con.close()
    # dla danego meczu uzupelniam nastepujace dane:
    return({'przeciwnik': przeciwnik,
                  'data': data,
                  'punkty_moje': punkty_moje,
                  'punkty_przeciwnika': punkty_przeciwnika,
                  'przebieg_meczu': przebieg_meczu,
                  'wynik_meczu': wynik_meczu,
                  'id_turnieju': id_turnieju,
                  })


def getUserMatches(login):
    ####### Rozegrane mecze zalogowanego uzytkownika ########

    con = mysql.connect()  # lacze z baza danych
    cursor = con.cursor()
    cursor.callproc('sp_getMecz', (login,))  # wywoluje procedure SQL, ktora pobiera mecze uzytkownika
    # pobrane z bazy dane zawiera liste meczy zalogowanego uzytkownika
    # struktura pobranego meczu: {id_meczu, ..., login1, login2}
    dane = cursor.fetchall()
    con.commit()

    mecze = []
    mecze2 = []

    for i in dane:  # dla kazdego meczu zalogowanego uzytkownika
        if i[2] == login:
            przeciwnik = i[3]  # zmienna przeciwnik zawiera login przeciwnika w danym meczu
        else:
            przeciwnik = i[2]

        id_meczu = i[0]  # zmienna zawiera id danego meczu

        # zmienna punkty_meczu zawiera informacje czy uzytkownik zdobyl, czy stracil punkt [[1, 1 ,0, 0, 0,...], ...]
        przebieg_meczu = []

        # zmienne beda przechowywac dla kazdego setu ilosc zdobytych punktow przez gracza
        punkty_moje = {}
        punkty_przeciwnika = {}
        p_set = []
        data = i[4]
        wynik_meczu = [0, 0]  # zmienna przechowuje ilosc wygranych setow przez obu graczy
        id_turnieju = i[1]

        if data:  # jeżeli mecz się odbył pobieram dane o punktach w tym meczu:
            # wywoluje w bazie procedure ktora dla danego meczu wyswietli punkty:
            cursor.callproc('sp_getPunkty', (id_meczu,))
            # pobrane z bazy dane zawieraja loginy graczy ktorzy zdobyli pojedynczy punkt
            # { {nr_setu, login1, id_meczu, }, {nr_setu,{...}} }
            dane2 = cursor.fetchall()
            con.commit()
            for j in dane2:  # zliczam punkty dla obu graczy
                if j[0] not in punkty_moje:  # jesli punkty dla tego setu nie sa liczone
                    punkty_moje[j[0]] = 0  # punkty dla tego setu ustawiam na 0
                    punkty_przeciwnika[j[0]] = 0
                    przebieg_meczu.append(p_set)  # do przebiegu meczu dodaje poprzedni set
                    p_set = []  # tworze pusty set, ktory bedzie zawieral przebieg gry [0, 1, 1, 0, ...]
                if j[1] == login:  # jesli punkt zdobyl gracz1 to dodaje mu punkt w tym secie
                    punkty_moje[j[0]] += 1
                    p_set.append(1)
                elif j[1] == przeciwnik:
                    punkty_przeciwnika[j[0]] += 1
                    p_set.append(0)
            przebieg_meczu.append(p_set)
            przebieg_meczu = przebieg_meczu[1:]

            for j in range(len(punkty_moje)):
                if punkty_moje[j + 1] > punkty_przeciwnika[j + 1]:
                    wynik_meczu[0] += 1
                elif punkty_moje[j + 1] < punkty_przeciwnika[j + 1]:
                    wynik_meczu[1] += 1

            # dla danego meczu uzupelniam nastepujace dane:
            mecze.append({'przeciwnik': przeciwnik,
                          'data': data,
                          'punkty_moje': punkty_moje,
                          'punkty_przeciwnika': punkty_przeciwnika,
                          'przebieg_meczu': przebieg_meczu,
                          'wynik_meczu': wynik_meczu,
                          'id_turnieju': id_turnieju,
                          })
        else:
            mecze2.append({'przeciwnik': przeciwnik,
                           'data': data,
                           'punkty_moje': punkty_moje,
                           'punkty_przeciwnika': punkty_przeciwnika,
                           'przebieg_meczu': przebieg_meczu,
                           'wynik_meczu': wynik_meczu,
                           'id_turnieju': id_turnieju,
                           })
    mecze = mecze + mecze2
    cursor.close()
    con.close()
    return mecze

def getTournamentMatches(id_turnieju):
    # dla turnieju pobieram dane meczach:

    con = mysql.connect()  # lacze z baza danych
    cursor = con.cursor()
    cursor.callproc('sp_getMeczTurnieju', (id_turnieju,))  # pobieram mecze turnieju o danym id
    dane2 = cursor.fetchall()
    con.commit()

    mecze = []
    mecze2 = []

    for k in dane2:  # dla każdego z meczy wydobywam informacje z bazy i dodaje do listy meczy 'mecze = []'
         # zmienna punkty_meczu zawiera informacje czy uzytkownik zdobyl, czy stracil punkt [[1, 1 ,0, 0, 0,...], ...]
        przebieg_meczu = []

        # zmienne beda przechowywac dla kazdego setu ilosc zdobytych punktow przez gracza
        punkty_gracz1 = {}
        punkty_gracz2 = {}
        p_set = []
        data = k[4]
        gracz1 = k[2]
        gracz2 = k[3]
        wynik_meczu = [0, 0]  # zmienna przechowuje ilosc wygranych setow przez obu graczy

        if data:  # jeżeli mecz się odbył
            cursor.callproc('sp_getPunkty', (k[0],))  # pobieram informacje o punktach danego meczu
            dane4 = cursor.fetchall()
            con.commit()
            for j in dane4:  # zliczam punkty dla obu graczy
                if j[0] not in punkty_gracz1:  # jesli punkty dla tego setu nie sa liczone
                    punkty_gracz1[j[0]] = 0  # punkty dla tego setu ustawiam na 0
                    punkty_gracz2[j[0]] = 0
                    przebieg_meczu.append(p_set)  # do przebiegu meczu dodaje poprzedni set
                    p_set = []  # tworze pusty set, ktory bedzie zawieral przebieg gry [0, 1, 1, 0, ...]
                if j[1] == k[2]:  # jesli punkt zdobyl gracz1 to dodaje mu punkt w tym secie
                    punkty_gracz1[j[0]] += 1
                    p_set.append(1)
                elif j[1] == k[3]:
                    punkty_gracz2[j[0]] += 1
                    p_set.append(0)
            przebieg_meczu.append(p_set)
            przebieg_meczu = przebieg_meczu[1:]

            for j in range(len(punkty_gracz1)):
                if punkty_gracz1[j + 1] > punkty_gracz2[j + 1]:
                    wynik_meczu[0] += 1
                elif punkty_gracz1[j + 1] < punkty_gracz2[j + 1]:
                     wynik_meczu[1] += 1

            mecze.append({
                'gracz1': gracz1,
                'gracz2': gracz2,
                'data': data,
                'punkty_gracz1': punkty_gracz1,
                'punkty_gracz2': punkty_gracz2,
                'przebieg_meczu': przebieg_meczu,
                'wynik_meczu': wynik_meczu,
                'id': k[0],

            })
        else:
            mecze2.append({
                'gracz1': gracz1,
                'gracz2': gracz2,
                'data': data,
                'punkty_gracz1': punkty_gracz1,
                'punkty_gracz2': punkty_gracz2,
                'przebieg_meczu': przebieg_meczu,
                'wynik_meczu': wynik_meczu,
                'id': k[0],
            })
    mecze = mecze + mecze2
    cursor.close()
    con.close()

    return mecze


@app.route("/")
def main():
    if session.get('user'):
        return redirect('userHome')
    else:
        return render_template('index.html')


@app.route('/showSignUp')
def showSignUp():
    if session.get('user'):
        return redirect('userHome')
    else:
        return render_template('signup.html')


@app.route('/signUp', methods=['POST'])
def signUp():
    # czytam wartosci z formularza rejestracji uzytkownika
    p_login = request.form['inputName']
    p_email = request.form['inputEmail']
    p_haslo = request.form['inputPassword']

    # walidacja:
    if p_login and p_email and p_haslo:

        # Jesli wszystko ok, lacze sie z baza danych:
        conn = mysql.connect()
        cursor = conn.cursor()
        # hashed_password = generate_password_hash(p_haslo)
        cursor.callproc('sp_createUser', (p_login, p_email, p_haslo))
        data = cursor.fetchall()
        print(data)
        conn.commit()
        cursor.close()
        conn.close()

        if len(data) is 0:
            return render_template('signin.html', info2='Konto zostało utworzone. Możesz teraz się zalogować.')
        else:
            return render_template('info.html', info='Nie udało się założyć konta')
    else:
        return json.dumps({'html': '<span>Wypełnij pola</span>'})

@app.route('/showSignIn')
def showSignin():
    if session.get('user'):
        return redirect('userHome')
    else:
        return render_template('signin.html')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    p_login = request.form['inputName']
    p_haslo = request.form['inputPassword']

    con = mysql.connect()
    cursor = con.cursor()
    cursor.callproc('sp_validateLogin', (p_login,))
    data = cursor.fetchall()
    con.commit()

    if len(data) > 0:
        if str(data[0][2]) == p_haslo:
            session['user'] = data[0][0]
            cursor.close()
            con.close()
            return redirect('/userHome')
        else:
            return render_template('signin.html', info="Podano złe dane logowania.")
    else:
        return render_template('signin.html', info="Podano złe dane logowania.")

@app.route('/userHome')
def userHome():
    #jesli uzytkownik poprawnie sie zalogowal
    if session.get('user'):
        login = session.get('user') #zmienna zawiera login zalogowanego uzytkownika

        #STATYSTYKI:
        con = mysql.connect() #lacze z baza danych
        cursor = con.cursor()
        cursor.callproc('sp_getMecz', (login,)) #wywoluje procedure SQL, ktora pobiera mecze uzytkownika
        dane = cursor.fetchall()
        con.commit()

        rozegrane_mecze = []
        nierozegrane_mecze = []

        for i in dane:
            if i[4]:
                rozegrane_mecze.append(i)
            else:
                nierozegrane_mecze.append(i)
        rozegrane_mecze = sorted(rozegrane_mecze, key=lambda x: x[4], reverse=True)

        cursor.callproc('sp_getWinners',)
        dane=cursor.fetchall()
        for i in dane:
            if i[0] == login:
                wygranych = i[1]



        statystyki={
            'rozegranych' : len(rozegrane_mecze),
            'wygranych' : wygranych,
            'nierozegranych' : len(nierozegrane_mecze),
        }

        #wydobywam szczegóły o ostatnich trzech rozegranych meczach
        mecze=[]
        for i in rozegrane_mecze[:3]:
            mecze.append(getMatchDetails(i[0], login)) #wydobywam szczegóły ostatnich trzech meczy i zapisuje do mecze=[]

        mecze2=[]
        for i in nierozegrane_mecze:
            if i[2] == login:
                przeciwnik = i[3]
            else:
                przeciwnik = i[2]

            mecze2.append({
                'przeciwnik' : przeciwnik,
                'id_turnieju' : i[1],
            })

        zdarzenia={
            'rozegrane_mecze' : mecze,
            'nierozegrane_mecze' : mecze2,
        }

        cursor.close()
        con.close()
        #przekazuje zmienne do wyswietlenia
        if len(statystyki):
            return render_template('userHome.html', login=login, statystyki=statystyki, zdarzenia=zdarzenia)
        else:
            return render_template('info.html', info='Brak danych', login=login)
    else:
        return redirect('/showSignUp')

@app.route('/myMatches')
def myMatches():
    #jesli uzytkownik poprawnie sie zalogowal
    if session.get('user'):
        login = session.get('user') #zmienna zawiera login zalogowanego uzytkownika
        mecze = getUserMatches(login)

        #przekazuje zmienne do wyswietlenia
        if len(mecze):
            return render_template('myMatches.html', login=login, mecze=mecze)
        else:
            return render_template('info.html', info='Nie rozegrałeś jeszcze żadnego meczu.', login=login)
    else:
        return redirect('/showSignUp')


@app.route('/showTournamentForm')
def showTournamentForm():
    if session.get('user'):
        # tworze listę loginów wszystkich użytkowników
        uzytkownicy = []
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc('sp_getUsers', ())
        dane = cursor.fetchall()
        con.commit()
        cursor.close()
        con.close()
        for i in dane:
            uzytkownicy.append(i[0])

        return render_template('newTournament.html', nadzorca=session.get('user'), uzytkownicy=uzytkownicy)
    else:
        return render_template('signin.html')

@app.route('/newTournament',  methods=['POST', 'GET'])
def newTournament():
    if session.get('user'):
        #pobieram z formularza: do_ilu_punkty, do_ilu_sety, typ, opis
        if request.method=='POST':
            p_uczestnicy = request.form.getlist('inputGracze')
            p_punkty = request.form['inputPunkty']
            p_sety = request.form['inputSety']
            p_typ = request.form.get('inputTyp')
            p_opis = request.form['inputOpis']
            p_login = session.get('user')

        if p_punkty and p_sety and p_typ and p_login:
            #Tworze turniej w bazie danych
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc('sp_newTurniej', (p_punkty, p_sety, p_typ, p_opis, p_login))  #
            id_turnieju = cursor.fetchall()
            con.commit()

            liczba_uczestnikow = len(p_uczestnicy)
            pary = []  # zmienna bedzie zawierac pary graczy ktorzy beda rozgrywac mecz
            if p_typ == 'ligowy':   #LIGOWY
                #tworze pary uczestnikow ktorzy beda razem grac ze soba mecze "kazdy z kazdym" LIGOWY
                for i in range(liczba_uczestnikow - 1):
                    for j in range(liczba_uczestnikow - 1 - i):
                        para = []
                        para.append(p_uczestnicy[i])
                        para.append(p_uczestnicy[j+i+1])
                        pary.append(para)
                random.shuffle(pary)
                info = 'Utworzono Turniej ligowy'
            elif p_typ == 'pucharowy':  #PUCHAROWY
                if is_power2(liczba_uczestnikow):
                    for i in range(int(liczba_uczestnikow / 2)):
                        para = []
                        para.append(p_uczestnicy[i])
                        para.append(p_uczestnicy[liczba_uczestnikow - i - 1])
                        pary.append(para)
                    info = 'Utworzono Turniej pucharowy'
                else:
                    info = 'Zla liczba uczestnikow. W turnieju pucharowym liczba uczestników musi wynosić 2^n'

            #wywoluje procedure SQL w bazie, ktora tworzy pojedyncze mecze dla turnieju:
            for i in pary:
                cursor.callproc('sp_newMecz', (id_turnieju, i[0], i[1]))
                con.commit()
            cursor.close()
            con.close()
        else:
            info = 'Nie utworzono turnieju!'

        return render_template('info.html', info = info, login=session.get('user'))
    else:

        return render_template('signin.html')

@app.route('/showTournament/<int:id>', methods=['GET'])
def showTournament(id):
    con = mysql.connect()  # lacze z baza danych
    cursor = con.cursor()
    cursor.callproc('sp_getTurniej', (id,))  # pobieram turniej o danym id
    dane3 = cursor.fetchall()  # dane o turnieju
    id = dane3[0][0]
    nadzorca = dane3[0][5]
    typ = dane3[0][3]
    opis = dane3[0][4]
    mecze = getTournamentMatches(id)
    zakonczony = True
    gracze = set()
    ranking={}
    rundy = []
    tabela = []
    wiersz = ['']

    for mecz in mecze:
        # sprawdzam czy turniej się zakończył:
        if mecz['data'] == None:
            zakonczony = False
        gracze.add(mecz['gracz1'])
        gracze.add(mecz['gracz2'])
    ilosc_graczy = len(gracze)

    if typ == 'pucharowy':
        # mecze muszą być posortowane wg kolejnosci (id)
        mecze = sorted(mecze, key=lambda x: x['id'])
        runda = []
        gracze = set()
        for mecz in mecze[:ilosc_graczy - 1]:
            if ((mecz['gracz1'] or mecz['gracz2']) in gracze):
                gracze = set()
                gracze.add((mecz['gracz1'], mecz['gracz2']))
                rundy.append(runda)
                runda = [mecz]
            else:
                gracze.add(mecz['gracz1'])
                gracze.add(mecz['gracz2'])
                runda.append(mecz)
            # ranking dla pucharowego:
            if zakonczony == True:
                if mecz['gracz1'] not in ranking:
                    ranking[mecz['gracz1']] = mecz['wynik_meczu'][0]
                else:
                    ranking[mecz['gracz1']] += mecz['wynik_meczu'][0]

                if mecz['gracz2'] not in ranking:
                    ranking[mecz['gracz2']] = mecz['wynik_meczu'][1]
                else:
                    ranking[mecz['gracz2']] += mecz['wynik_meczu'][1]
        rundy.append(runda)

        # jeśli odbywały się jakieś dodatkowe mecze (dogrywki o trzecie miejsce) to uwzgledniam kto wygrał dogrywkę
        if (zakonczony == True) and (len(mecze) > (ilosc_graczy - 1)):
            for m in mecze[ilosc_graczy - 1:]:
                if m['wynik_meczu'][0] > m['wynik_meczu'][1]:
                    ranking.pop(m['gracz2'])
                else:
                    ranking.pop(m['gracz1'])

        ranking = OrderedDict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))

    elif typ == 'ligowy':
        # ranking dla ligowego:
        if zakonczony == True:
            for mecz in mecze:
                if mecz['gracz1'] not in ranking:
                    ranking[mecz['gracz1']] = mecz['wynik_meczu'][0]
                else:
                    ranking[mecz['gracz1']] += mecz['wynik_meczu'][0]

                if mecz['gracz2'] not in ranking:
                    ranking[mecz['gracz2']] = mecz['wynik_meczu'][1]
                else:
                    ranking[mecz['gracz2']] += mecz['wynik_meczu'][1]

            # jeśli odbywały się jakieś dodatkowe mecze (dogrywki o trzecie miejsce) to uwzgledniam kto wygrał dogrywkę
            if (len(mecze) > ((ilosc_graczy*(ilosc_graczy - 1))/2)):
                for m in mecze[((ilosc_graczy*(ilosc_graczy - 1))/2):]:
                    if m['wynik_meczu'][0] > m['wynik_meczu'][1]:
                        ranking.pop(m['gracz2'])
                    else:
                        ranking.pop(m['gracz1'])

        ranking = OrderedDict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))

        ### tabela wyników
        for gracz in ranking:
            wiersz.append(gracz)
        tabela.append(wiersz)
        wiersz = []
        for gracz1 in ranking:
            wiersz.append(gracz1)
            for gracz2 in ranking:
                if gracz1 == gracz2:
                    wynik = '0:0'
                    wiersz.append(wynik)
                else:
                    for mecz in mecze:
                        if mecz['gracz1'] == gracz1 and mecz['gracz2'] == gracz2:
                            wynik = str(mecz['wynik_meczu'][0]) + ':' + str(mecz['wynik_meczu'][1])
                            wiersz.append(wynik)
                        elif mecz['gracz1'] == gracz2 and mecz['gracz2'] == gracz1:
                            wynik = str(mecz['wynik_meczu'][1]) + ':' + str(mecz['wynik_meczu'][0])
                            wiersz.append(wynik)
            tabela.append(wiersz)
            wiersz = []

    turniej={  # zapisuję dane turnieju do listy turniejów 'turnieje = []'
        'id': id,
        'nadzorca': nadzorca,
        'typ': typ,
        'opis': opis,
        'mecze': mecze,
        'rundy': rundy,
        'ranking' : ranking,
        'tabela' : tabela,
    }

    return render_template('tournament.html',turniej=turniej, login=session.get('user'))


@app.route('/myTournaments')
def myTournaments():
    if session.get('user'):
        login = session.get('user') #zmienna zawiera login zalogowanego uzytkownika

        ####### Rozegrane mecze zalogowanego uzytkownika ########

        con = mysql.connect() #lacze z baza danych
        cursor = con.cursor()
        cursor.callproc('sp_getTurniejeIdGracza', (login,))
        dane=cursor.fetchall()

        turnieje = [] #zmienna bedzie zawierac
        for i in dane:  #znajduje mecze, które naleza do turnieju i zapisuje id turniejow do zmiennej moje_turnieje
            cursor.callproc('sp_getTurniej', (i,))  # pobieram turniej o danym id
            dane3 = cursor.fetchall()  # dane o turnieju
            id = dane3[0][0]
            nadzorca = dane3[0][5]
            typ = dane3[0][3]
            opis = dane3[0][4]
            mecze = getTournamentMatches(id)
            ranking = {}
            gracze = set()
            rundy = []
            zakonczony = True
            tabela = []

            for mecz in mecze:
                #sprawdzam czy turniej się zakończył:
                if mecz['data'] == None:
                    zakonczony = False
                gracze.add(mecz['gracz1'])
                gracze.add(mecz['gracz2'])

            ilosc_graczy = len(gracze)

            if typ == 'pucharowy':
                # mecze muszą być posortowane wg kolejnosci (id)
                mecze = sorted(mecze, key=lambda x: x['id'])
                runda = []
                gracze = set()
                for mecz in mecze[:ilosc_graczy-1]:
                    if ((mecz['gracz1'] or mecz['gracz2']) in gracze):
                        gracze = set()
                        gracze.add((mecz['gracz1'], mecz['gracz2']))
                        rundy.append(runda)
                        runda = [mecz]
                    else:
                        gracze.add(mecz['gracz1'])
                        gracze.add(mecz['gracz2'])
                        runda.append(mecz)
                    # ranking dla pucharowego:
                    if zakonczony == True:
                        if mecz['gracz1'] not in ranking:
                            ranking[mecz['gracz1']] = mecz['wynik_meczu'][0]
                        else:
                            ranking[mecz['gracz1']] += mecz['wynik_meczu'][0]

                        if mecz['gracz2'] not in ranking:
                            ranking[mecz['gracz2']] = mecz['wynik_meczu'][1]
                        else:
                            ranking[mecz['gracz2']] += mecz['wynik_meczu'][1]
                rundy.append(runda)

                # jeśli odbywały się jakieś dodatkowe mecze (dogrywki o trzecie miejsce) to uwzgledniam kto wygrał dogrywkę
                if (zakonczony == True) and (len(mecze) > (ilosc_graczy - 1)):
                    for m in mecze[ilosc_graczy - 1:]:
                        if m['wynik_meczu'][0] > m['wynik_meczu'][1]:
                            ranking.pop(m['gracz2'])
                        else:
                            ranking.pop(m['gracz1'])

                ranking = OrderedDict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))

            elif typ == 'ligowy':
                # ranking dla ligowego:
                if zakonczony == True:
                    for mecz in mecze:
                        if mecz['gracz1'] not in ranking:
                            ranking[mecz['gracz1']] = mecz['wynik_meczu'][0]
                        else:
                            ranking[mecz['gracz1']] += mecz['wynik_meczu'][0]
                        if mecz['gracz2'] not in ranking:
                            ranking[mecz['gracz2']] = mecz['wynik_meczu'][1]
                        else:
                            ranking[mecz['gracz2']] += mecz['wynik_meczu'][1]
                    # jeśli odbywały się jakieś dodatkowe mecze (dogrywki o trzecie miejsce) to uwzgledniam kto wygrał dogrywkę
                    if (len(mecze) > ((ilosc_graczy * (ilosc_graczy - 1)) / 2)):
                        for m in mecze[((ilosc_graczy * (ilosc_graczy - 1)) / 2):]:
                            if m['wynik_meczu'][0] > m['wynik_meczu'][1]:
                                ranking.pop(m['gracz2'])
                            else:
                                ranking.pop(m['gracz1'])
                ranking = OrderedDict(sorted(ranking.items(), key=lambda x: x[1], reverse=True))

                ### tabela wyników
                wiersz = ['']

                for gracz in ranking:
                    wiersz.append(gracz)

                tabela.append(wiersz)
                wiersz = []

                for gracz1 in ranking:
                    wiersz.append(gracz1)
                    for gracz2 in ranking:
                        if gracz1 == gracz2:
                            wynik = '0:0'
                            wiersz.append(wynik)
                        else:
                            for mecz in mecze:
                                if mecz['gracz1'] == gracz1 and mecz['gracz2'] == gracz2:
                                    wynik = str(mecz['wynik_meczu'][0]) + ':' + str(mecz['wynik_meczu'][1])
                                    wiersz.append(wynik)
                                elif mecz['gracz1'] == gracz2 and mecz['gracz2'] == gracz1:
                                    wynik = str(mecz['wynik_meczu'][1]) + ':' + str(mecz['wynik_meczu'][0])
                                    wiersz.append(wynik)
                    tabela.append(wiersz)
                    wiersz = []

            turnieje.append({  # zapisuję dane turnieju do listy turniejów 'turnieje = []'
                'id': id,
                'nadzorca': nadzorca,
                'typ': typ,
                'opis': opis,
                'mecze': mecze,
                'rundy' : rundy,
                'ranking' : ranking,
                'tabela' : tabela,
            })

        cursor.close()
        con.close()
        return render_template('myTournaments.html', turnieje = turnieje, login=session.get('user'))
    return render_template('signin.html')

@app.route('/deleteTournament/<int:id>', methods=['GET'])
def deleteTournament(id):
    con = mysql.connect()
    cursor = con.cursor()
    cursor.callproc('sp_getTurniej', (id,))
    dane = cursor.fetchall()
    print(dane)


    if session.get('user') == dane[0][5]:
        cursor.callproc('sp_deleteTurniej',(id,))
        dane = cursor.fetchall()
        con.commit()
        cursor.close()
        con.close()
        return redirect('/myTournaments')
    else:
        con.commit()
        cursor.close()
        con.close()
        return redirect('/myTournaments')

@app.route('/rank')
def rank():
    ##################### RANKING #######################

    # wywoluje procedure w bazie ktora wypisuje loginy graczy ktorzy wygrali mecz
    con = mysql.connect()
    cursor = con.cursor()

    cursor.callproc('sp_getWinners', )
    dane = cursor.fetchall()

    cursor.callproc('sp_getLoosers', )
    dane2 = cursor.fetchall()

    con.commit()
    cursor.close()
    con.close()

    statystyki={}
    tmp={}
    for i in dane2:
        tmp[i[0]] = i[1]
    for i in dane:
        statystyki[i[0]] = [i[1], tmp[i[0]]]

    for i in statystyki.copy():    #wyrzucam ze statystyk graczy, którzy nie rozegrali, żadnego meczu:
        if (statystyki[i][0] + statystyki[i][1]) == 0:
            statystyki.pop(i)


    # sortuje wyniki graczy od najlepszego według wartości: (wygrane_mecze / rozegrane_mecze)
    statystyki = OrderedDict(sorted(statystyki.items(), key=lambda x: (x[1][0]) / (x[1][0]+x[1][1]), reverse=True))


    if len(statystyki):
        return render_template('rank.html', statystyki=statystyki, login=session.get('user'))
    else:
        return render_template('info.html', info='brak danych', login=session.get('user'))

@app.route('/logout')
def logout():
    if session.get('user'):
        session.pop('user', None)
        return redirect('/')
    else:
        return redirect('/')


if __name__ == "__main__":
    app.run()


