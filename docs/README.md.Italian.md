> **Nota**
>
> Durante l'installazione delle dipendenze, selezionare rigorosamente le **versioni specificate** nel file requirements.txt.
>
> ` pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

# <img src="docs/logo.png" width="40" > GPT Ottimizzazione Accademica (GPT Academic)

**Se ti piace questo progetto, ti preghiamo di dargli una stella. Se hai sviluppato scorciatoie accademiche o plugin funzionali più utili, non esitare ad aprire una issue o pull request. Abbiamo anche una README in [Inglese|](docs/README_EN.md)[Giapponese|](docs/README_JP.md)[Coreano|](https://github.com/mldljyh/ko_gpt_academic)[Russo|](docs/README_RS.md)[Francese](docs/README_FR.md) tradotta da questo stesso progetto.
Per tradurre questo progetto in qualsiasi lingua con GPT, leggere e eseguire [`multi_language.py`](multi_language.py) (sperimentale).

> **Nota**
>
> 1. Si prega di notare che solo i plugin (pulsanti) contrassegnati in **rosso** supportano la lettura di file, alcuni plugin sono posizionati nel **menu a discesa** nella zona dei plugin. Accettiamo e gestiamo PR per qualsiasi nuovo plugin con **massima priorità**!
>
> 2. Le funzionalità di ogni file di questo progetto sono descritte dettagliatamente nella propria analisi di autotraduzione [`self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A). Con l'iterazione delle versioni, è possibile fare clic sui plugin funzionali correlati in qualsiasi momento per richiamare GPT e generare nuovamente il rapporto di analisi automatica del progetto. Le domande frequenti sono riassunte nella [`wiki`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98). [Metodo di installazione] (#installazione).
>
> 3. Questo progetto è compatibile e incoraggia l'utilizzo di grandi modelli di linguaggio di produzione nazionale come chatglm, RWKV, Pangu ecc. Supporta la coesistenza di più api-key e può essere compilato nel file di configurazione come `API_KEY="openai-key1,openai-key2,api2d-key3"`. Per sostituire temporaneamente `API_KEY`, inserire `API_KEY` temporaneo nell'area di input e premere Invio per renderlo effettivo. 

<div align="center">Funzione | Descrizione
--- | ---
Correzione immediata | Supporta correzione immediata e ricerca degli errori di grammatica del documento con un solo clic
Traduzione cinese-inglese immediata | Traduzione cinese-inglese immediata con un solo clic
Spiegazione del codice immediata | Visualizzazione del codice, spiegazione del codice, generazione del codice, annotazione del codice con un solo clic
[Scorciatoie personalizzate](https://www.bilibili.com/video/BV14s4y1E7jN) | Supporta scorciatoie personalizzate
Design modularizzato | Supporta potenti [plugin di funzioni](https://github.com/binary-husky/chatgpt_academic/tree/master/crazy_functions) personalizzati, i plugin supportano l'[aggiornamento in tempo reale](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[Auto-profiling del programma](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugin di funzioni] [Comprensione immediata](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A) del codice sorgente di questo progetto
[Analisi del programma](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugin di funzioni] Un clic può analizzare l'albero di altri progetti Python/C/C++/Java/Lua/...
Lettura del documento, [traduzione](https://www.bilibili.com/video/BV1KT411x7Wn) del documento | [Plugin di funzioni] La lettura immediata dell'intero documento latex/pdf di un documento e la generazione di un riassunto
Traduzione completa di un documento Latex, [correzione immediata](https://www.bilibili.com/video/BV1FT411H7c5/) | [Plugin di funzioni] Una traduzione o correzione immediata di un documento Latex
Generazione di annotazioni in batch | [Plugin di funzioni] Generazione automatica delle annotazioni di funzione con un solo clic
[Traduzione cinese-inglese di Markdown](https://www.bilibili.com/video/BV1yo4y157jV/) | [Plugin di funzioni] Hai letto il [README](https://github.com/binary-husky/chatgpt_academic/blob/master/docs/README_EN.md) delle cinque lingue sopra?
Generazione di report di analisi di chat | [Plugin di funzioni] Generazione automatica di un rapporto di sintesi dopo l'esecuzione
[Funzione di traduzione di tutto il documento PDF](https://www.bilibili.com/video/BV1KT411x7Wn) | [Plugin di funzioni] Estrarre il titolo e il sommario dell'articolo PDF + tradurre l'intero testo (multithreading)
[Assistente di Arxiv](https://www.bilibili.com/video/BV1LM4y1279X) | [Plugin di funzioni] Inserire l'URL dell'articolo di Arxiv e tradurre il sommario con un clic + scaricare il PDF
[Assistente integrato di Google Scholar](https://www.bilibili.com/video/BV19L411U7ia) | [Plugin di funzioni] Con qualsiasi URL di pagina di ricerca di Google Scholar, lascia che GPT ti aiuti a scrivere il tuo [relatedworks](https://www.bilibili.com/video/BV1GP411U7Az/)
Aggregazione delle informazioni su Internet + GPT | [Plugin di funzioni] Fai in modo che GPT rilevi le informazioni su Internet prima di rispondere alle domande, senza mai diventare obsolete
Visualizzazione di formule/img/tabelle | È possibile visualizzare un'equazione in forma [tex e render](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png) contemporaneamente, supporta equazioni e evidenziazione del codice
Supporto per plugin di funzioni multithreading | Supporto per chiamata multithreaded di chatgpt, elaborazione con un clic di grandi quantità di testo o di un programma
Avvia il tema di gradio [scuro](https://github.com/binary-husky/chatgpt_academic/issues/173) | Aggiungere ```/?__theme=dark``` dopo l'URL del browser per passare a un tema scuro
Supporto per maggiori modelli LLM, supporto API2D | Sentirsi serviti simultaneamente da GPT3.5, GPT4, [Tsinghua ChatGLM](https://github.com/THUDM/ChatGLM-6B), [Fudan MOSS](https://github.com/OpenLMLab/MOSS) deve essere una grande sensazione, giusto?
Ulteriori modelli LLM supportat,i supporto per l'implementazione di Huggingface | Aggiunta di un'interfaccia Newbing (Nuovo Bing), introdotta la compatibilità con Tsinghua [Jittorllms](https://github.com/Jittor/JittorLLMs), [LLaMA](https://github.com/facebookresearch/llama), [RWKV](https://github.com/BlinkDL/ChatRWKV) e [PanGu-α](https://openi.org.cn/pangu/)
Ulteriori dimostrazioni di nuove funzionalità (generazione di immagini, ecc.)... | Vedere la fine di questo documento...
 
- Nuova interfaccia (modificare l'opzione LAYOUT in `config.py` per passare dal layout a sinistra e a destra al layout superiore e inferiore)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230361456-61078362-a966-4eb5-b49e-3c62ef18b860.gif" width="700" >
</div>Sei un traduttore professionista di paper accademici.

- Tutti i pulsanti vengono generati dinamicamente leggendo il file functional.py, e aggiungerci nuove funzionalità è facile, liberando la clipboard.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Revisione/Correzione
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- Se l'output contiene una formula, viene visualizzata sia come testo che come formula renderizzata, per facilitare la copia e la visualizzazione.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Non hai tempo di leggere il codice del progetto? Passa direttamente a chatgpt e chiedi informazioni.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Chiamata mista di vari modelli di lingua di grandi dimensioni (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

---
# Installazione
## Installazione - Metodo 1: Esecuzione diretta (Windows, Linux o MacOS)

1. Scarica il progetto
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. Configura API_KEY

In `config.py`, configura la tua API KEY e altre impostazioni, [configs for special network environments](https://github.com/binary-husky/gpt_academic/issues/1).

(N.B. Quando il programma viene eseguito, verifica prima se esiste un file di configurazione privato chiamato `config_private.py` e sovrascrive le stesse configurazioni in `config.py`.  Pertanto, se capisci come funziona la nostra logica di lettura della configurazione, ti consigliamo vivamente di creare un nuovo file di configurazione chiamato `config_private.py` accanto a `config.py`, e spostare (copiare) le configurazioni di `config.py` in `config_private.py`. 'config_private.py' non è sotto la gestione di git e può proteggere ulteriormente le tue informazioni personali. NB Il progetto supporta anche la configurazione della maggior parte delle opzioni tramite "variabili d'ambiente". La sintassi della variabile d'ambiente è descritta nel file `docker-compose`. Priorità di lettura: "variabili d'ambiente" > "config_private.py" > "config.py")


3. Installa le dipendenze
```sh
# (Scelta I: se sei familiare con python) (python 3.9 o superiore, più nuovo è meglio), N.B.: utilizza il repository ufficiale pip o l'aliyun pip repository, metodo temporaneo per cambiare il repository: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Scelta II: se non conosci Python) utilizza anaconda, il processo è simile (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # crea l'ambiente anaconda
conda activate gptac_venv                 # attiva l'ambiente anaconda
python -m pip install -r requirements.txt # questo passaggio funziona allo stesso modo dell'installazione con pip
```

<details><summary>Se si desidera supportare ChatGLM di Tsinghua/MOSS di Fudan come backend, fare clic qui per espandere</summary>
<p>

【Passaggio facoltativo】 Se si desidera supportare ChatGLM di Tsinghua/MOSS di Fudan come backend, è necessario installare ulteriori dipendenze (prerequisiti: conoscenza di Python, esperienza con Pytorch e computer sufficientemente potente):
```sh
# 【Passaggio facoltativo I】 Supporto a ChatGLM di Tsinghua. Note su ChatGLM di Tsinghua: in caso di errore "Call ChatGLM fail 不能正常加载ChatGLM的参数" , fare quanto segue: 1. Per impostazione predefinita, viene installata la versione di torch + cpu; per usare CUDA, è necessario disinstallare torch e installare nuovamente torch + cuda; 2. Se non è possibile caricare il modello a causa di una configurazione insufficiente del computer, è possibile modificare la precisione del modello in request_llm/bridge_chatglm.py, cambiando AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) in AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llm/requirements_chatglm.txt  

# 【Passaggio facoltativo II】 Supporto a MOSS di Fudan
python -m pip install -r request_llm/requirements_moss.txt
git clone https://github.com/OpenLMLab/MOSS.git request_llm/moss  # Si prega di notare che quando si esegue questa riga di codice, si deve essere nella directory radice del progetto

# 【Passaggio facoltativo III】 Assicurati che il file di configurazione config.py includa tutti i modelli desiderati, al momento tutti i modelli supportati sono i seguenti (i modelli della serie jittorllms attualmente supportano solo la soluzione docker):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "newbing", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. Esegui
```sh
python main.py
```5. Plugin di test delle funzioni
```
- Funzione plugin di test (richiede una risposta gpt su cosa è successo oggi in passato), puoi utilizzare questa funzione come template per implementare funzionalità più complesse
    Clicca su "[Demo del plugin di funzione] Oggi nella storia"
```

## Installazione - Metodo 2: Utilizzo di Docker

1. Solo ChatGPT (consigliato per la maggior parte delle persone)

``` sh
git clone https://github.com/binary-husky/chatgpt_academic.git  # scarica il progetto
cd chatgpt_academic                                 # entra nel percorso
nano config.py                                      # con un qualsiasi editor di testo, modifica config.py configurando "Proxy", "API_KEY" e "WEB_PORT" (ad esempio 50923)
docker build -t gpt-academic .                      # installa

#(ultimo passaggio - selezione 1) In un ambiente Linux, utilizzare '--net=host' è più conveniente e veloce
docker run --rm -it --net=host gpt-academic
#(ultimo passaggio - selezione 2) In un ambiente MacOS/Windows, l'opzione -p può essere utilizzata per esporre la porta del contenitore (ad es. 50923) alla porta della macchina
docker run --rm -it -e WEB_PORT=50923 -p 50923:50923 gpt-academic
```

2. ChatGPT + ChatGLM + MOSS (richiede familiarità con Docker)

``` sh
# Modifica docker-compose.yml, elimina i piani 1 e 3, mantieni il piano 2. Modifica la configurazione del piano 2 in docker-compose.yml, si prega di fare riferimento alle relative annotazioni
docker-compose up
```

3. ChatGPT + LLAMA + Pangu + RWKV (richiede familiarità con Docker)

``` sh
# Modifica docker-compose.yml, elimina i piani 1 e 2, mantieni il piano 3. Modifica la configurazione del piano 3 in docker-compose.yml, si prega di fare riferimento alle relative annotazioni
docker-compose up
```


## Installazione - Metodo 3: Altre modalità di distribuzione

1. Come utilizzare un URL di reindirizzamento / AzureAPI Cloud Microsoft
Configura API_URL_REDIRECT seguendo le istruzioni nel file `config.py`.

2. Distribuzione su un server cloud remoto (richiede conoscenze ed esperienza di server cloud)
Si prega di visitare [wiki di distribuzione-1] (https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)

3. Utilizzo di WSL2 (Windows Subsystem for Linux)
Si prega di visitare [wiki di distribuzione-2] (https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)

4. Come far funzionare ChatGPT all'interno di un sottodominio (ad es. `http://localhost/subpath`)
Si prega di visitare [Istruzioni per l'esecuzione con FastAPI] (docs/WithFastapi.md)

5. Utilizzo di docker-compose per l'esecuzione
Si prega di leggere il file docker-compose.yml e seguire le istruzioni fornite.

---
# Uso avanzato
## Personalizzazione dei pulsanti / Plugin di funzione personalizzati

1. Personalizzazione dei pulsanti (scorciatoie accademiche)
Apri `core_functional.py` con qualsiasi editor di testo e aggiungi la voce seguente, quindi riavvia il programma (se il pulsante è già stato aggiunto con successo e visibile, il prefisso e il suffisso supportano la modifica in tempo reale, senza bisogno di riavviare il programma).

ad esempio
```
"超级英译中": {
    # Prefisso, verrà aggiunto prima del tuo input. Ad esempio, descrivi la tua richiesta, come tradurre, spiegare il codice, correggere errori, ecc.
    "Prefix": "Per favore traduci questo testo in Cinese, e poi spiega tutti i termini tecnici nel testo con una tabella markdown:\n\n", 
    
    # Suffisso, verrà aggiunto dopo il tuo input. Ad esempio, con il prefisso puoi circondare il tuo input con le virgolette.
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

2. Plugin di funzione personalizzati

Scrivi plugin di funzione personalizzati e esegui tutte le attività che desideri o non hai mai pensato di fare.
La difficoltà di scrittura e debug dei plugin del nostro progetto è molto bassa. Se si dispone di una certa conoscenza di base di Python, è possibile realizzare la propria funzione del plugin seguendo il nostro modello. Per maggiori dettagli, consultare la [guida al plugin per funzioni] (https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97).

---
# Ultimo aggiornamento
## Nuove funzionalità dinamiche1. Funzionalità di salvataggio della conversazione. Nell'area dei plugin della funzione, fare clic su "Salva la conversazione corrente" per salvare la conversazione corrente come file html leggibile e ripristinabile, inoltre, nell'area dei plugin della funzione (menu a discesa), fare clic su "Carica la cronologia della conversazione archiviata" per ripristinare la conversazione precedente. Suggerimento: fare clic su "Carica la cronologia della conversazione archiviata" senza specificare il file consente di visualizzare la cache degli archivi html di cronologia, fare clic su "Elimina tutti i record di cronologia delle conversazioni locali" per eliminare tutte le cache degli archivi html.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. Generazione di rapporti. La maggior parte dei plugin genera un rapporto di lavoro dopo l'esecuzione.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

3. Progettazione modulare delle funzioni, semplici interfacce ma in grado di supportare potenti funzionalità.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

4. Questo è un progetto open source che può "tradursi da solo".
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="500" >
</div>

5. Tradurre altri progetti open source è semplice.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="500" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="500" >
</div>

6. Piccola funzione decorativa per [live2d](https://github.com/fghrsh/live2d_demo) (disattivata per impostazione predefinita, è necessario modificare `config.py`).
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. Supporto del grande modello linguistico MOSS
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236639178-92836f37-13af-4fdd-984d-b4450fe30336.png" width="500" >
</div>

8. Generazione di immagini OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

9. Analisi e sintesi audio OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

10. Verifica completa dei testi in LaTeX
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" width="500" >
</div>


## Versione:
- versione 3.5(Todo): utilizzo del linguaggio naturale per chiamare tutti i plugin di funzioni del progetto (alta priorità)
- versione 3.4(Todo): supporto multi-threading per il grande modello linguistico locale Chatglm
- versione 3.3: +funzionalità di sintesi delle informazioni su Internet
- versione 3.2: i plugin di funzioni supportano più interfacce dei parametri (funzionalità di salvataggio della conversazione, lettura del codice in qualsiasi lingua + richiesta simultanea di qualsiasi combinazione di LLM)
- versione 3.1: supporto per interrogare contemporaneamente più modelli gpt! Supporto api2d, bilanciamento del carico per più apikey
- versione 3.0: supporto per Chatglm e altri piccoli LLM
- versione 2.6: ristrutturazione della struttura del plugin, miglioramento dell'interattività, aggiunta di più plugin
- versione 2.5: auto-aggiornamento, risoluzione del problema di testo troppo lungo e overflow del token durante la sintesi di grandi progetti di ingegneria
- versione 2.4: (1) funzionalità di traduzione dell'intero documento in formato PDF aggiunta; (2) funzionalità di scambio dell'area di input aggiunta; (3) opzione di layout verticale aggiunta; (4) ottimizzazione della funzione di plugin multi-threading.
- versione 2.3: miglioramento dell'interattività multi-threading
- versione 2.2: i plugin di funzioni supportano l'hot-reload
- versione 2.1: layout ripiegabile
- versione 2.0: introduzione di plugin di funzioni modulari
- versione 1.0: funzione di basegpt_academic sviluppatori gruppo QQ-2: 610599535

- Problemi noti
    - Alcuni plugin di traduzione del browser interferiscono con l'esecuzione del frontend di questo software
    - La versione di gradio troppo alta o troppo bassa può causare diversi malfunzionamenti

## Riferimenti e apprendimento

```
Il codice fa riferimento a molte altre eccellenti progettazioni di progetti, principalmente:

# Progetto 1: ChatGLM-6B di Tsinghua:
https://github.com/THUDM/ChatGLM-6B

# Progetto 2: JittorLLMs di Tsinghua:
https://github.com/Jittor/JittorLLMs

# Progetto 3: Edge-GPT:
https://github.com/acheong08/EdgeGPT

# Progetto 4: ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# Progetto 5: ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Altro:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
```