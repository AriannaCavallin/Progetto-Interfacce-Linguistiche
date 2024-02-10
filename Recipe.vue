<template>
    <!--Card che mostrerà ogni ricetta-->
    <div class="card mb-3">
      <div class="row g-0">
        <div class="col-md-4">
          <!--Immagine contenuta nel vettore relativo alla ricetta-->
          <img :src="elemento[0]" class="img-fluid rounded-start">
        </div>
        <div class="col-md-8">
          <div class="card-body">
            <!--Indice nel vettore e nome della ricetta-->
            <h5 class="card-title">{{ index + 1 }}. {{ elemento[1] }}</h5>
            <!--In base all'ordine richiesto viene mostrato il dato corrispondente-->
            <p v-if="elemento[3] == 0 && elemento[4] == 'kcal'" class="card-text">kcal non presenti</p>
            <p v-else class="card-text">{{ elemento[3] }} {{ elemento[4] }}</p>
            <!--Button mostrato durante la richiesta per il calcolo della ricchezza lessicale-->
            <button v-if="loading" class="btn btn-success" type="button">
              <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
              <span role="status">Loading...</span>
            </button>
            <!--Button per il calcolo della ricchezza lessicale-->
            <template v-else>
              <button v-if="ricchezza == ''" @click="analizza(elemento[2])" type="button" class="btn btn-success">Ricchezza lessicale</button>
              <button v-else @click="ricchezza = ''" type="button" class="btn btn-success">Chiudi</button>
            </template>
          </div>
        </div>
        <!--Nel footer viene mostrato un alert di colore diverso in base al grado di ricchezza lessicale-->
        <div v-if="ricchezza != '' || errore" class=" pt-4 card-footer bg-transparent text-center">
          <div v-if="primaLettera(ricchezza) === 'A'" class="alert alert-success" role="alert">
            {{ricchezza}}
          </div>
          <div v-if="primaLettera(ricchezza) === 'M'" class="alert alert-warning" role="alert">
            {{ricchezza}}
          </div>
          <div v-if="primaLettera(ricchezza) === 'B'" class="alert alert-danger" role="alert">
            {{ricchezza}}
          </div>
          <!--Alert nel caso di errore del server-->
          <div v-if="errore" class="alert alert-danger pb-3" role="alert">
            Errore nella chiamata al server(Dettagli in console)!
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
    import axios from 'axios';
    
    export default {
      //Propietà passate dalla pagina padre
      props: {
          elemento: Array,
          index: Number,
      },
      data() {
        return {
          ricchezza: "", //Varibile che conterrà il valore di ricchezza lessicale
          loading: false, //Boolean per il caricamento
          errore: false, //Boolean per la gestione degli errori del server
        };
      },
      methods: {
        //Funzione che restituisce il primo carattere della stringa
        primaLettera(str) {
          return str.charAt(0);
        },
        //Funzione per il calcolo della ricchezza lessicale
        analizza(link){
          this.loading = true;
          const payload = {
            page: link.toString()
          };
          const path = 'http://127.0.0.1:5002/analizza';
          axios.post(path, payload)
          .then((res) => {
            this.ricchezza = res.data.preparation;
            this.loading = false;
            this.errore = false;
          })  
          .catch((error) => {
            console.error(error);
            this.loading = false;
            this.errore = true;
          });
        },
      },
    };
    </script>