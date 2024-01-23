


> **Nota**
>
> Questo README è stato tradotto da GPT (implementato da un plugin di questo progetto) e non è al 100% affidabile, per favore valuta attentamente i risultati della traduzione.
>
> 2023.11.7: Quando installi le dipendenze, seleziona le versioni **specificate** nel file `requirements.txt`. Comando di installazione: `pip install -r requirements.txt`.


# <div align=center><img src="logo.png" width="40"> GPT Ottimizzazione Accademica (GPT Academic)</div>

**Se ti piace questo progetto, per favore dagli una stella; se hai idee o plugin utili, fai una pull request!**

Se ti piace questo progetto, dagli una stella.
Per tradurre questo progetto in qualsiasi lingua con GPT, leggi ed esegui [`multi_language.py`](multi_language.py) (sperimentale).

> **Nota**
>
> 1. Fai attenzione che solo i plugin (pulsanti) **evidenziati** supportano la lettura dei file, alcuni plugin si trovano nel **menu a tendina** nell'area dei plugin. Inoltre, accogliamo e gestiamo con **massima priorità** qualsiasi nuovo plugin attraverso pull request.
>
> 2. Le funzioni di ogni file in questo progetto sono descritte in dettaglio nel [rapporto di traduzione automatica del progetto `self_analysis.md`](https://github.com/binary-husky/gpt_academic/wiki/GPT‐Academic项目自译解报告). Con l'iterazione della versione, puoi anche fare clic sui plugin delle funzioni rilevanti in qualsiasi momento per richiamare GPT e rigenerare il rapporto di auto-analisi del progetto. Domande frequenti [`wiki`](https://github.com/binary-husky/gpt_academic/wiki) | [Metodo di installazione standard](#installazione) | [Script di installazione one-click](https://github.com/binary-husky/gpt_academic/releases) | [Configurazione](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明)。
>
> 3. Questo progetto è compatibile e incoraggia l'uso di modelli di linguaggio di grandi dimensioni nazionali, come ChatGLM. Supporto per la coesistenza di più chiavi API, puoi compilare nel file di configurazione come `API_KEY="openai-key1,openai-key2,azure-key3,api2d-key4"`. Quando è necessario sostituire temporaneamente `API_KEY`, inserisci temporaneamente `API_KEY` nell'area di input e premi Invio per confermare.




<div align="center">

Funzionalità (⭐ = Nuove funzionalità recenti) | Descrizione
--- | ---
⭐[Integrazione di nuovi modelli](https://github.com/binary-husky/gpt_academic/wiki/%E5%A6%82%E4%BD%95%E5%88%87%E6%8D%A2%E6%A8%A1%E5%9E%8B)！ | Baidu [Qianfan](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Nlks5zkzu) e [Wenxin](https://cloud.baidu.com/doc/GUIDE/5268.9) Intelligence, [Tongyi Qianwen](https://modelscope.cn/models/qwen/Qwen-7B-Chat/summary), Shanghai AI-Lab [bookbrain](https://github.com/InternLM/InternLM), Xunfei [Xinghuo](https://xinghuo.xfyun.cn/), [LLaMa2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf), Zhipu API, DALLE3
Revisione, traduzione, spiegazione del codice | Revisione, traduzione, ricerca errori grammaticali nei documenti e spiegazione del codice con un clic
[Tasti di scelta rapida personalizzati](https://www.bilibili.com/video/BV14s4y1E7jN) | Supporta tasti di scelta rapida personalizzati
Design modulare | Supporto per plugin personalizzati potenti, i plugin supportano l'[aggiornamento in tempo reale](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[Analisi del codice](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugin] Un clic per analizzare alberi di progetti Python/C/C++/Java/Lua/... o [autoanalisi](https://www.bilibili.com/video/BV1cj411A7VW)
Lettura di documenti, traduzione di documenti | [Plugin] Un clic per interpretare documenti completi in latex/pdf e generare un riassunto
Traduzione completa di testi in Latex, revisione completa di testi in Latex | [Plugin] Un clic per tradurre o correggere documenti in latex
Generazione automatica di commenti in batch | [Plugin] Un clic per generare commenti di funzione in batch
Traduzione [cinese-inglese](https://www.bilibili.com/video/BV1yo4y157jV/) in Markdown | [Plugin] Hai visto sopra i README in 5 lingue diverse ([Inglese](https://github.com/binary-husky/gpt_academic/blob/master/docs/README_EN.md))?
Generazione di rapporti di analisi chat | [Plugin] Genera automaticamente un rapporto di sintesi dopo l'esecuzione
Funzionalità di traduzione di testo completo in PDF | [Plugin] Estrai il titolo e il riassunto dei documenti PDF e traduci tutto il testo (multithreading)
Aiutante per Arxiv | [Plugin] Inserisci l'URL dell'articolo Arxiv per tradurre riassunto e scaricare PDF in un clic
Controllo completo dei documenti in Latex | [Plugin] Rileva errori grammaticali e ortografici nei documenti in Latex simile a Grammarly + Scarica un PDF per il confronto
Assistente per Google Scholar | [Plugin] Dato qualsiasi URL della pagina di ricerca di Google Scholar, fai scrivere da GPT gli *articoli correlati* per te
Concentrazione delle informazioni di Internet + GPT | [Plugin] [Recupera informazioni da Internet](https://www.bilibili.com/video/BV1om4y127ck) utilizzando GPT per rispondere alle domande e rendi le informazioni sempre aggiornate
⭐Traduzione accurata di articoli Arxiv ([Docker](https://github.com/binary-husky/gpt_academic/pkgs/container/gpt_academic_with_latex)) | [Plugin] [Traduci articoli Arxiv ad alta qualità](https://www.bilibili.com/video/BV1dz4y1v77A/) con un clic, lo strumento di traduzione degli articoli migliore al mondo al momento
⭐[Inserimento della conversazione vocale in tempo reale](https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md) | [Plugin] [Ascolta l'audio](https://www.bilibili.com/video/BV1AV4y187Uy/) in modo asincrono, taglia automaticamente le frasi e trova automaticamente il momento giusto per rispondere
Visualizzazione di formule, immagini, tabelle | Mostra contemporaneamente formule in formato tex e renderizzato, supporta formule e evidenziazione del codice
⭐Plugin multi-agente AutoGen | [Plugin] Esplora le possibilità dell'emergenza intelligence multi-agente con l'aiuto di Microsoft AutoGen!
Attiva il tema scuro [qui](https://github.com/binary-husky/gpt_academic/issues/173) | Aggiungi ```/?__theme=dark``` alla fine dell'URL del browser per passare al tema scuro
Supporto di più modelli LLM | Essere servito contemporaneamente da GPT3.5, GPT4, [ChatGLM2 di Tsinghua](https://github.com/THUDM/ChatGLM2-6B), [MOSS di Fudan](https://github.com/OpenLMLab/MOSS)
⭐Modello di fine-tuning ChatGLM2 | Supporto per l'importazione del modello di fine-tuning di ChatGLM2, fornendo plug-in di assistenza per il fine tuning di ChatGLM2
Più supporto per modelli LLM, supporto del [deploy di Huggingface](https://huggingface.co/spaces/qingxu98/gpt-academic) | Aggiungi interfaccia Newbing (Bing Translator), introduce il supporto di [JittorLLMs](https://github.com/Jittor/JittorLLMs) di Tsinghua, supporto per [LLaMA](https://github.com/facebookresearch/llama) e [Panguα](https://openi.org.cn/pangu/)
⭐Pacchetto pip [void-terminal](https://github.com/binary-husky/void-terminal) | Fornisce funzionalità di tutti i plugin di questo progetto direttamente in Python senza GUI (in sviluppo)
⭐Plugin terminale virtuale | [Plugin] Richiama altri plugin di questo progetto utilizzando linguaggio naturale
Altre nuove funzionalità (come la generazione di immagini) ... | Vedi alla fine di questo documento ...

</div>


- Nuovo layout (modifica l'opzione LAYOUT in `config.py` per passare tra "layout sinistra / destra" e "layout sopra / sotto")
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/d81137c3-affd-4cd1-bb5e-b15610389762" width="700" >
</div>


- Tutti i pulsanti vengono generati dinamicamente leggendo `functional.py`, puoi aggiungere liberamente funzionalità personalizzate, liberando la clipboard
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Revisione / correzione
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>



- Se l'output contiene formule, saranno visualizzate sia in formato tex che in formato renderizzato per facilitarne la copia e la lettura.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Non hai voglia di guardare il codice del progetto? Mostralo direttamente al chatgpt in bocca.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Chiamate miste di modelli di grandi dimensioni (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

# Installazione
### Metodo di installazione I: Esegui direttamente (Windows, Linux o MacOS)

1. Scarica il progetto
```sh
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git
cd gpt_academic
```

2. Configura l'API_KEY

Nel file `config.py`, configura l'API KEY e altre impostazioni, [clicca qui per vedere come configurare l'API in ambienti di rete speciali](https://github.com/binary-husky/gpt_academic/issues/1) . [Pagina Wiki](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明).

「 Il programma controllerà prima se esiste un file di configurazione privata chiamato `config_private.py` e utilizzerà le configurazioni in esso contenute per sovrascrivere le configurazioni con lo stesso nome in `config.py`. Se comprendi questa logica di lettura, ti consigliamo vivamente di creare un nuovo file di configurazione chiamato `config_private.py` accanto a `config.py` e spostare (copiare) le configurazioni da `config.py` a `config_private.py` (basta copiare le voci di configurazione che hai modificato). 」

「 Supporta la configurazione del progetto tramite `variabili d'ambiente`, il formato di scrittura delle variabili d'ambiente è descritto nel file `docker-compose.yml` o nella nostra [pagina Wiki](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明) priorità di lettura della configurazione: `variabili d'ambiente` > `config_private.py` > `config.py`. 」

3. Installa le dipendenze
```sh
# (Scelta I: Se familiarizzato con python, python>=3.9) Nota: Usa il repository delle fonti ufficiale di pip o Ali pip per temporaneamente cambiare la fonte: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Scelta II: Usa Anaconda) Anche in questo caso, i passaggi sono simili (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # Crea l'ambiente anaconda
conda activate gptac_venv                 # Attiva l'ambiente anaconda
python -m pip install -r requirements.txt # Questo passaggio è identico alla procedura di installazione con pip
```


<details><summary>Se desideri utilizzare il backend di ChatGLM2 di Tsinghua/Fudan MOSS/RWKV, fai clic per espandere</summary>
<p>

[Optional] Se desideri utilizzare ChatGLM2 di Tsinghua/Fudan MOSS come backend, è necessario installare ulteriori dipendenze (Requisiti: conoscenza di Python + esperienza con Pytorch + hardware potente):
```sh
# [Optional Step I] Supporto per ChatGLM2 di Tsinghua. Note di ChatGLM di Tsinghua: Se si verifica l'errore "Call ChatGLM fail non può caricare i parametri di ChatGLM", fare riferimento a quanto segue: 1: L'installazione predefinita è la versione torch+cpu, per usare cuda è necessario disinstallare torch ed installare nuovamente la versione con torch+cuda; 2: Se il modello non può essere caricato a causa di una configurazione insufficiente, è possibile modificare la precisione del modello in request_llm/bridge_chatglm.py, sostituendo AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) con AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llms/requirements_chatglm.txt

# [Optional Step II] Supporto per Fudan MOSS
python -m pip install -r request_llms/requirements_moss.txt
git clone --depth=1 https://github.com/OpenLMLab/MOSS.git request_llms/moss  # Attenzione: eseguire questo comando nella directory principale del progetto

# [Optional Step III] Supporto per RWKV Runner
Consulta il Wiki: https://github.com/binary-husky/gpt_academic/wiki/%E9%80%82%E9%85%8DRWKV-Runner

# [Optional Step IV] Assicurati che il file di configurazione config.py includa i modelli desiderati. Di seguito sono elencati i modelli attualmente supportati (gli llm di jittorllms supportano solo la soluzione Docker):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "moss", "jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. Esegui
```sh
python main.py
```

### Metodo di installazione II: Utilizzo di Docker

0. Installa tutte le funzionalità del progetto (Questo è un'immagine di grandi dimensioni che include cuda e latex. Potrebbe non essere adatta se hai una connessione lenta o uno spazio su disco limitato)
[![fullcapacity](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml)

``` sh
# Modifica il file docker-compose.yml: mantieni solo la configurazione 0 e rimuovi le altre configurazioni. Avvia il seguente comando:
docker-compose up
```

1. ChatGPT + Wenxin Yiyu (Poem) + Spark, solo modelli online (Consigliato per la maggior parte delle persone)
[![basic](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml)
[![basiclatex](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml)
[![basicaudio](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml)

``` sh
# Modifica il file docker-compose.yml: mantieni solo la configurazione 1 e rimuovi le altre configurazioni. Avvia il seguente comando:
docker-compose up
```

P.S. Se hai bisogno del plugin LaTeX, consulta la pagina Wiki. In alternativa, puoi utilizzare le configurazioni 4 o 0 direttamente per ottenere questa funzionalità.

2. ChatGPT + ChatGLM2 + MOSS + LLAMA2 + Tongyi Q&W (Richiede conoscenze su Nvidia Docker)
[![chatglm](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml)

``` sh
# Modifica il file docker-compose.yml: mantieni solo la configurazione 2 e rimuovi le altre configurazioni. Avvia il seguente comando:
docker-compose up
```


### Metodo di installazione III: Altre opzioni di distribuzione
1. **Script di esecuzione con un clic per Windows**.
Se non conosci affatto l'ambiente python in Windows, puoi scaricare uno script di esecuzione con un clic dalla sezione [Release](https://github.com/binary-husky/gpt_academic/releases) per installare la versione che non richiede modelli locali.
Lo script è stato fornito da [oobabooga](https://github.com/oobabooga/one-click-installers).

2. Utilizzo di API di terze parti, Azure, Wenxin Yiyu (Poem), Xinghuo, ecc. vedi [pagina Wiki](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明)

3. Guida all'installazione del server cloud remoto.
Visita la [pagina Wiki sull'installazione del server cloud remoto](https://github.com/binary-husky/gpt_academic/wiki/云服务器远程部署指南).

4. Altre nuove piattaforme o metodi di distribuzione:
    - Uso di Sealos per il [deployment con un clic](https://github.com/binary-husky/gpt_academic/issues/993).
    - Uso di WSL2 (Windows Subsystem for Linux). Vedi [Guida all'installazione](https://github.com/binary-husky/gpt_academic/wiki/使用WSL2（Windows-Subsystem-for-Linux-子系统）部署) per maggiori informazioni.
    - Funzionamento su un sotto-percorso URL (`http://localhost/subpath`). Vedi [istruzioni FastAPI](docs/WithFastapi.md) per maggiori dettagli.



# Utilizzo avanzato
### I: Personalizzare nuovi pulsanti rapidi (tasti di scelta rapida accademici)
Apri `core_functional.py` con qualsiasi editor di testo e aggiungi le seguenti voci, quindi riavvia il programma. (Se il pulsante esiste già, sia il prefisso che il suffisso possono essere modificati a caldo senza la necessità di riavviare il programma.)
Ad esempio,
```
"Traduzione avanzata Cinese-Inglese": {
     # Prefisso, sarà aggiunto prima del tuo input. Ad esempio, utilizzato per descrivere la tua richiesta, come traduzione, spiegazione del codice, rifinitura, ecc.
     "Prefisso": "Si prega di tradurre il seguente testo in cinese e fornire spiegazione per i termini tecnici utilizzati, utilizzando una tabella in markdown uno per uno:\n\n",

     # Suffisso, sarà aggiunto dopo il tuo input. Ad esempio, in combinazione con il prefisso, puoi circondare il tuo input con virgolette.
     "Suffisso": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

### II: Plugin di funzioni personalizzate
Scrivi potentissimi plugin di funzioni per eseguire qualsiasi compito che desideri, sia che tu lo pensi o meno.
La scrittura di plugin per questo progetto è facile e richiede solo conoscenze di base di Python. Puoi seguire il [Guida ai Plugin di Funzione](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97) per maggiori dettagli.


# Aggiornamenti
### I: Aggiornamenti

1. Funzionalità di salvataggio della conversazione. Chiamare `Salva la conversazione corrente` nell'area del plugin per salvare la conversazione corrente come un file html leggibile e ripristinabile.
Inoltre, nella stessa area del plugin (menu a tendina) chiamare `Carica la cronologia della conversazione` per ripristinare una conversazione precedente.
Suggerimento: fare clic su `Carica la cronologia della conversazione` senza specificare un file per visualizzare la tua cronologia di archiviazione HTML.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. ⭐ Funzionalità di traduzione articoli Latex/Arxiv ⭐
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/002a1a75-ace0-4e6a-94e2-ec1406a746f1" height="250" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/9fdcc391-f823-464f-9322-f8719677043b" height="250" >
</div>

3. Terminale vuoto (Comprensione dell'intento dell'utente dai testi liberi + Chiamata automatica di altri plugin)

- Passaggio 1: Digitare "Chiamare il plugin per tradurre un documento PDF, l'indirizzo è https://openreview.net/pdf?id=rJl0r3R9KX"
- Passaggio 2: Fare clic su "Terminale vuoto"

<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/66f1b044-e9ff-4eed-9126-5d4f3668f1ed" width="500" >
</div>

4. Design modulare, interfacce semplici che supportano funzionalità potenti
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

5. Traduzione e interpretazione di altri progetti open source
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" height="250" >
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" height="250" >
</div>

6. Funzionalità leggera per [live2d](https://github.com/fghrsh/live2d_demo) (disabilitata per impostazione predefinita, richiede modifica di `config.py`)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. Generazione di immagini di OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

8. Elaborazione e riepilogo audio di OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

9. Correzione totale del testo di Latex
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" height="200" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/476f66d9-7716-4537-b5c1-735372c25adb" height="200">
</div>

10. Cambio linguaggio e tema
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/b6799499-b6fb-4f0c-9c8e-1b441872f4e8" width="500" >
</div>


### II: Versioni:
- versione 3.70 (todo): Ottimizzazione della visualizzazione del tema AutoGen e sviluppo di una serie di plugin correlati.
- versione 3.60: Introduzione di AutoGen come fondamento per i plugin della nuova generazione.
- versione 3.57: Supporto per GLM3, StarFirev3, Wenxin-yiyanv4 e correzione di bug sulla concorrenza dell'uso di modelli locali.
- versione 3.56: Possibilità di aggiungere dinamicamente pulsanti per funzionalità di base e nuova pagina di riepilogo del PDF.
- versione 3.55: Ristrutturazione dell'interfaccia utente, introduzione di finestre fluttuanti e barre dei menu.
- versione 3.54: Nuovo interprete di codice dinamico (Code Interpreter) (da perfezionare).
- versione 3.53: Possibilità di selezionare dinamicamente diversi temi dell'interfaccia utente, miglioramento della stabilità e risoluzione dei conflitti tra utenti multipli.
- versione 3.50: Utilizzo del linguaggio naturale per chiamare tutte le funzioni dei plugin di questo progetto (Terminale vuoto), supporto per la classificazione dei plugin, miglioramento dell'interfaccia utente e design di nuovi temi.
- versione 3.49: Supporto per la piattaforma Baidu Qianfan e Wenxin-yiyan.
- versione 3.48: Supporto per Alibaba DAXI 所见即所答, Shanghai AI-Lab Shusheng, Xunfei StarFire.
- versione 3.46: Supporto per la chat vocale in tempo reale completamente automatica.
- versione 3.45: Supporto personalizzato per il micro-aggiustamento del modello ChatGLM2.
- versione 3.44: Supporto ufficiale per Azure, miglioramento dell'usabilità dell'interfaccia.
- versione 3.4: + Funzionalità di traduzione di documenti arXiv e correzione di documenti LaTeX.
- versione 3.3: + Funzionalità di sintesi delle informazioni su Internet.
- versione 3.2: Il plugin di funzione supporta più interfacce dei parametri (funzionalità di salvataggio della conversazione, interpretazione di codici in qualsiasi linguaggio contemporaneamente, interrogare qualsiasi combinazione di LLM).
- versione 3.1: Supporto per l'interrogazione simultanea di più modelli GPT! Supporto per api2d, equilibrio del carico con più apikey.
- versione 3.0: Supporto per chatglm e altri piccoli llm.
- versione 2.6: Rielaborazione della struttura del plugin, miglioramento dell'interattività, aggiunta di ulteriori plugin.
- versione 2.5: Aggiornamento automatico, risoluzione del problema della lunghezza eccessiva del testo durante il riepilogo di grandi blocchi di codice che supera i token.
- versione 2.4: (1) Nuova funzionalità di traduzione di documenti PDF; (2) Nuova funzionalità di scambio delle posizioni tra l'area di input (input area); (3) Nuova opzione di layout verticale; (4) Ottimizzazione del plugin a threading multiplo.
- versione 2.3: Miglioramento dell'interattività con threading multiplo.
- versione 2.2: Supporto per il plugin con ricarica a caldo.
- versione 2.1: Layout pieghevole.
- versione 2.0: Introduzione di plugin modulari.
- versione 1.0: Funzioni di base

GPT Academic Developer QQ Group: `610599535`

- Problemi noti
    - Alcuni plug-in di traduzione del browser possono interferire con il funzionamento del frontend di questo software
    - L'app Gradio ufficiale ha molti bug di compatibilità, si consiglia di installare Gradio tramite `requirement.txt`

### III: Temi
Il tema può essere modificato modificando l'opzione `THEME` (config.py)
1. `Chuanhu-Small-and-Beautiful` [Website](https://github.com/GaiZhenbiao/ChuanhuChatGPT/)


### IV: Branch di Sviluppo di questo progetto

1. `master` branch: branch principale, versione stabile
2. `frontier` branch: branch di sviluppo, versione di test


### V: Riferimenti e Risorse di Apprendimento

```
Nel codice sono state utilizzate diverse idee dagli altri progetti, senza un ordine specifico:

# ChatGLM2-6B di Tsinghua:
https://github.com/THUDM/ChatGLM2-6B

# JittorLLMs di Tsinghua:
https://github.com/Jittor/JittorLLMs

# ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Edge-GPT:
https://github.com/acheong08/EdgeGPT

# ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT



# Installazione con un solo clic di Oobabooga:
https://github.com/oobabooga/one-click-installers

# Altre risorse:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
