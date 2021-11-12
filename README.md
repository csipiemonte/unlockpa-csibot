# Branched
# CSI Chatbot
Chatbot domanda/risposta per CSI (Consorzio per il Sistema Informativo) di Regione Piemonte



### Prerequisiti
* git
* Python 3.6 o superiore
* Virtualenv

Facoltativi
* Docker
* Docker compose

### Installazione (linux Virtualenv)


* Ambiente Virtualenv:
	
	```
	virtualenv -p python3.6 venv
	source venv/bin/activate
	pip install -r requirements.txt
	```

### Esecuzione

```
source venv/bin/activate
python main.py botmanager
python main.py run
```

### Container Docker
Alternativamente all'installazione con Virtualenv, 
è possibile caricare l'applicazione in due container Docker.

Creazione dell'immagine:

è stato predisposto il build dal comando compose:

```
docker-compose  build
```
Avvio del container botmanager e un'istanza chatbot:
```
docker-compose up -d
```

N.B: 172.17.0.1 è l'indirizzo di default di docker al quale
sono raggiungibili le porte pubbliche degli altri container.
In alternativa è possibile configurare un'apposita rete.
new
### COMMAND LINE
Se si vuole utilizzare il modello per il riconoscimento delle domande sul tema unlockPA
è possibile lanciare: 
```
docker-compose exec botmanager python main.py insert --excel=/testdata/faqbot-V02-018.xlsx
 >>>  "{'id': 1, 'result': {'idbot': 30}, 'error': {'code': 0}}"
```
A questo punto la knowledge base sarà inserita nel database e il modello addestrato nella cartella dills

Recuperare l'idbot e associarlo ad un bot con il comando:
```
curl -i -X POST \
   -H "Content-Type:application/json" \
   -k -d \
'{"id":1, "service": "reboot", "body": 
{
  "idbot":30
}}' \
 'http://localhost:5001'
 ```


E' possibile verificare il corretto funzionamento utilizzando il seguente comando di query:

```
curl -i -X POST    -H "Content-Type:application/json"    -k -d '{"id":1, "service": "query", "body":
{
  "text":"posso uscire con il cane"
}}'  'http://localhost:5001'
```

Che offrirà una risposta del tipo:

```
{
	"id": 1,
	"result": {
		"answers": [{
				"text": "-2",
				"confidence": 0.9999999999999997,
				"index_ques": "28"
			}, {
				"text": "-2",
				"confidence": 0.9888400788508596,
				"index_ques": "28"
			}, {
				"text": "-2",
				"confidence": 0.862478021912424,
				"index_ques": "200"
			}, {
				"text": "-2",
				"confidence": 0.8205060098257122,
				"index_ques": "28"
			}, {
				"text": "-2",
				"confidence": 0.7569860055557888,
				"index_ques": "200"
			}
		]
	},
	"error": {
		"code": 0
	}
}

```
Nell'esempio sono state ritrovate 5 esempi somiglianti. Il campo index_ques identifica le domande di riferimento che corrispondono alla richiesta dell'utente.
il campo text identifica la risposta per un determinato comune. -2 identifica che il comune non ha definito la risposta alla specifica domanda.