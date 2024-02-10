<template>
    <div class="container">
      <!--Durante la chiamata al server per la ricerca della ricetta viene mostrato il caricamento-->
      <div v-if="loading" class="d-flex justify-content-center">
        <div class="spinner-border text-primary" role="status"></div>
      </div>
      <template v-else>
        <!--Input per inserire la ricetta e button per inviare la richiesta al server-->
        <div class="input-group pb-3">
          <textarea v-model="ricetta" class="form-control" aria-label="With textarea"></textarea>
          <button @click="invia" type="button" class="btn btn-warning">Cerca ricetta</button>
        </div>
        <!--Durante la chiamata al server per ordinare le ricette viene mostrato il caricamento-->
        <div v-if="loadingOrdine" class="d-flex justify-content-center">
          <div class="spinner-border text-primary" role="status"></div>
        </div>
        <template v-else>
          <!--Quattro button per decidere che ordine eseguire-->
          <div v-if="data.length && !presenza" class="btn-group d-flex justify-content-center pb-3" role="group" aria-label="Basic outlined example">
            <button type="button" @click="ordine('lunghezza')" class="btn btn-outline-warning">Lunghezza ricetta</button>
            <button type="button" @click="ordine('ingredienti')" class="btn btn-outline-warning">Numero ingredienti</button>
            <button type="button" @click="ordine('calorie')" class="btn btn-outline-warning">Meno calorico</button>
            <button type="button" @click="ordine('valutazione')" class="btn btn-outline-warning">Valutazione</button>
          </div>
          <!--Alert in caso la ricetta inserita non venga trovata-->
          <div v-if="noRicetta" class="alert alert-danger pb-3" role="alert">
            Ricetta non trovata!
          </div>
          <!--Alert in caso la ricetta non venga inserita-->
          <div v-if="presenza" class="alert alert-danger pb-3" role="alert">
            Inserisci una ricetta!
          </div>
          <!--Alert in caso di errore della chiamata al server-->
          <div v-if="errore" class="alert alert-danger pb-3" role="alert">
            Errore nella chiamata al server(Dettagli in console)!
          </div>
          <template v-else>
            <!--Viene mostrata la card, componete da noi definito, per presentare le varie ricette-->
            <template v-for="(item, i) in data" :key="i">
              <!--Ad ogni componente vengono passati i valori della ricetta corrispondete e l'indice-->
              <recipe :elemento="item" :index="i"></recipe>
            </template>
          </template>
        </template>
      </template>
    </div>
  </template>
  
  <script>
  import axios from 'axios'; //Axios per chiamate al server
  import recipe from './Recipe.vue'; //Importazione del componente
  
  export default {
    data() {
      return {
        ricetta: '', //Variabile per la ricetta inserita in input
        data: [], //Array che conterrà i dati scaricati
        presenza: false, //Boolean per vedere se l'utente ha inserito la ricetta
        loading: false, //Boolean per la gestione del caricamento delle ricette
        loadingOrdine: false, //Boolean per la gestione del caricamento degli oridni
        noRicetta: false, //Boolean che attiva l'alert in caso di mancanza delle ricette
        errore: false, //Boolean che attiva l'alert in caso di errore nella chiamata al server
      };
    },
    components: {
      recipe
    },
    methods: {
      //Funzione che definisce il payload per fare la ricerca in base alla ricetta
      invia() {
        if(this.ricetta != ""){
          //Se l'utente ha inserito la ricetta si genera il payload
          this.presenza = false;
          const payload = {
            recipe: this.ricetta.toString()
          };
          //Viene eseguita la funzione di ricerca passando il payload
          this.ricerca(payload);
          this.ricetta = "";
        }else{
          //Se l'utente non inserice la ricetta viene mostrato l'errore
          this.presenza = true;
          this.data = [];
        }
      },
      //Funzione che emette la chiamata al server per ricercare le ricette
      ricerca(payload) {
        this.loading = true;
        const path = 'http://127.0.0.1:5002/ricerca';
        //Tramite axios viene effettuata la richiesta passando payload e percorso
        axios.post(path, payload)
        .then((res) => {
          //Se la richiesta è valida controllo che ci siano delle ricette
          if(res.data.dati.length != 0){
            //In caso positivo viene assegnato il risultato alla varibile corrispondente
            this.data = res.data.dati;
            this.noRicetta = false;
          }else{
            //In caso negativo viene mostrato l'alert di errore
            this.data = [];
            this.noRicetta = true;
          }
          this.loading = false;
          this.errore = false;
        })  
        .catch((error) => {
          //Se la richiesta non va a buon fine viene mostrato l'alert di errore
          console.error(error);
          this.loading = false;
          this.errore = true;
        });
      },
      //Funzione che ordina le ricette in base al tipo di ordine richiesto
      ordine(tipo){
        this.loadingOrdine = true;
        //Generazione del payload con le ricette e il tipo di ordine
        const payload = {
          pages: this.data,
          type: tipo.toString()
        };
        const path = 'http://127.0.0.1:5002/ordine';
        axios.post(path, payload)
        .then((res) => {
          //In caso di richiesta valida il server passa le ricette ordinate
          this.data = res.data.ordine;
          this.loadingOrdine = false;
          this.errore = false;
        })  
        .catch((error) => {
          //Se la richiesta non va a buon fine viene mostrato l'alert di errore
          console.error(error);
          this.loadingOrdine = false;
          this.errore = true;
        });
      },
    },
  };
  </script>
  