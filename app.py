#Importazione delle librerie
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request
from flask_cors import CORS
import stanza

#Definizione del server Flask
app = Flask(__name__)
app.config.from_object(__name__)

CORS(app, resources={r'/*': {'origins': '*'}})

#Download dei modelli per l'italiano di Stanza
stanza.download('it')

#Carica il modulo di elaborazione per l'italiano
nlp = stanza.Pipeline('it', processors='tokenize,mwt,pos')

#Funzione per il calcolo della ricchezza lessicale
def ricchezzaLessicale(text):
    doc = nlp(text)
    ricchezza = ""

    #Estrazione delle parole in minuscolo e controlla che caratteri siano alfanumerici
    words = [word.text.lower() for sent in doc.sentences for word in sent.words if word.text.isalnum()]

    #Calcola della ricchezza lessicale (TTR - Type-Token Ratio)
    total_words = len(words)
    unique_words = len(set(words))
    ttr = unique_words / total_words if total_words > 0 else 0

    #In base al valore calcolato restituisce il grado di ricchezza lessicale
    if ttr >= 0 and ttr <= 0.3:
        ricchezza = "Bassa ricchezza lessicale"
    elif ttr > 0.3 and ttr <= 0.6:
        ricchezza = "Media ricchezza lessicale"
    else: 
        ricchezza = "Alta ricchezza lessicale"

    return ricchezza

#Utilizza beautiful soup per estrarre il rating della ricetta partendo dal link
def valutazione(url):
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')
    div = soup.find('div', {'class': 'gz-rating-panel'})
    rate = div['data-content-rate']
    #Sostituisce la virgola con il punto
    rate = rate.replace(',', '.')
    #Restituisce la valutazione convertita da stringa in float
    return float(rate)

#Funzione che sostituisce lo spazio vuoto nel nome della ricetta e lo sostituisce con il + nell'url
def modRicetta(nomeRicetta):
    result = nomeRicetta.lower()
    result = result.replace(" ", "+")
    return str(result)

#Utilizza beautiful soup per estrarre la preparazione della ricetta partendo dal link
def preparazione(url):
    preparation = ""
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')
    for tag in soup.find_all('div', class_="gz-content-recipe-step"):
        preparation += str(tag.find('p').text)
    return preparation

#Utilizza beautiful soup per estrarre le calorie della ricetta partendo dal link
def calorie(url):
    value = 0.0
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')
    if soup.find('div', class_="gz-text-calories-total") != None:
        value = float(soup.find('div', class_="gz-text-calories-total").text)
    else:
        #Nel caso non sia presente il valore restituisce 0
        value = 0.0
    return value

#Utilizza beautiful soup per estrarre e contare gli ingredienti della ricetta partendo dal link
def ingredienti(url):
    ingredients = []
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'html.parser')
    for tag in soup.find_all('dd', class_="gz-ingredient"):
        ingredients.append(tag.find('a').text)
    return len(ingredients)

#Funzione che accetta la richesta per la ricerca delle ricette
@app.route('/ricerca', methods=['POST'])
def search():
    lista = []
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        #Definisce l'url per ricercare le ricette in base all'input dell'utente
        url = 'https://www.giallozafferano.it/ricerca-ricette/' + modRicetta(post_data.get('recipe')) + '/'
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'html.parser')
        #Tramite beautiful soup prende il link per l'immagine, il link alla ricetta e il titolo
        for tag in soup.find_all('article', class_='gz-card gz-card-horizontal gz-mBottom3x gz-horizontal-view gz-card-search gz-ets-serp-target'):
            if(tag.find('a').find('img', class_="lazyload") != None):
               image = str(tag.find('a').find('img', class_="lazyload")['data-src'])
            else:
               image = str(tag.find('a').find('img')['src'])
            
            title = str(tag.find('a')['title'])
            link = str(tag.find('a')['href'])

            #tupla che conterrà i tre elementi che verrà poi inserita nella lista da restituire al client
            nuova_tupla = (image, title, link)
            lista.append(nuova_tupla)
        response_object['dati'] = lista
    #La risposta viene inviata al client in formato JSON
    return jsonify(response_object)

#Funzione che accetta la richesta per il calcolo della ricchezza lessicle sulla preparazione della ricetta
@app.route('/analizza', methods=['POST'])
def analysis():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        response_object['preparation'] = ricchezzaLessicale(preparazione(post_data.get('page')))
    return jsonify(response_object)

#Funzione che accetta la richesta per ordinare le ricette
@app.route('/ordine', methods=['POST'])
def order():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        lista_di_liste = post_data.get('pages')
        #Scorre la lista di liste che contiene le varie ricette
        for lista in lista_di_liste:
            #Se la lista ha 5 campi allora gli utlimi due vengono cancellati
            if len(lista) == 5:
                lista.remove(lista[-2])
                lista.remove(lista[-1])

        #Scorre la lista di liste che contiene le ricette e in base al tipo di ordine viene passato il valore e la descrizione del valore
        for lista in lista_di_liste:
            if post_data.get('type') == "lunghezza":
                lista.append(len(preparazione(lista[2])))
                lista.append("caratteri")
            elif post_data.get('type') == "ingredienti":
                lista.append(ingredienti(lista[2]))
                lista.append("ingredienti")
            elif post_data.get('type')== "calorie":
                lista.append(calorie(lista[2]))
                lista.append("kcal")
            else:
                lista.append(valutazione(lista[2]))
                lista.append("stelle")

        #La lista di liste viene oridnata in base al valore scelto e poi viene restituita al client
        lista_di_liste = sorted(lista_di_liste, key=lambda x: x[-2])
        response_object['ordine'] = lista_di_liste
    return jsonify(response_object)

#Viene avviato il server
if __name__ == '__main__':
    app.run()