> **Hinweis**
>
> Bei der Installation von Abhängigkeiten sollten nur die in **requirements.txt** **angegebenen Versionen** streng ausgewählt werden.
>
> `pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

# <img src="docs/logo.png" width="40" > GPT Akademisch optimiert (GPT Academic)

**Wenn Ihnen dieses Projekt gefällt, geben Sie ihm bitte einen Stern; wenn Sie bessere Tastenkombinationen oder Funktions-Plugins entwickelt haben, können Sie gerne einen Pull Request eröffnen.**

Wenn Sie dieses Projekt mögen, geben Sie ihm bitte einen Stern. Wenn Sie weitere nützliche wissenschaftliche Abkürzungen oder funktionale Plugins entwickelt haben, können Sie gerne ein Problem oder eine Pull-Anforderung öffnen. Wir haben auch ein README in [Englisch|](docs/README_EN.md)[日本語|](docs/README_JP.md)[한국어|](https://github.com/mldljyh/ko_gpt_academic)[Русский|](docs/README_RS.md)[Français](docs/README_FR.md), das von diesem Projekt selbst übersetzt wurde.
Um dieses Projekt in eine beliebige Sprache mit GPT zu übersetzen, lesen Sie `multi_language.py` (experimentell).

> **Hinweis**
>
> 1. Beachten Sie bitte, dass nur Funktionserweiterungen (Schaltflächen) mit **roter Farbe** Dateien lesen können und einige Erweiterungen im **Dropdown-Menü** des Erweiterungsbereichs zu finden sind. Außerdem begrüßen wir jede neue Funktionserweiterung mit **höchster Priorität** und bearbeiten sie.
>
> 2. Die Funktionalität jeder Datei in diesem Projekt wird in der Selbstanalyse [`self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A) detailliert beschrieben. Mit der Weiterentwicklung der Versionen können Sie jederzeit die zugehörigen Funktions-Erweiterungen aufrufen, um durch Aufruf von GPT einen Selbstanalysebericht des Projekts zu erstellen. Häufig gestellte Fragen finden Sie in der [`Wiki`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98). [Installationsanweisungen](#Installation).
>
> 3. Dieses Projekt ist kompatibel und fördert die Verwendung von inländischen Sprachmodellen wie ChatGLM und RWKV, Pangu, etc. Es unterstützt das Vorhandensein mehrerer api-keys, die in der Konfigurationsdatei wie folgt angegeben werden können: `API_KEY="openai-key1,openai-key2,api2d-key3"`. Wenn ein `API_KEY` temporär geändert werden muss, geben Sie den temporären `API_KEY` im Eingabebereich ein und drücken Sie dann die Eingabetaste, um ihn zu übernehmen.Funktion | Beschreibung
--- | ---
Ein-Klick-Polieren | Unterstützt ein-Klick-Polieren und ein-Klick-Suche nach grammatikalischen Fehlern in wissenschaftlichen Arbeiten
Ein-Klick Chinesisch-Englisch Übersetzung | Ein-Klick Chinesisch-Englisch Übersetzung
Ein-Klick-Code-Erklärung | Zeigt Code, erklärt Code, erzeugt Code und fügt Kommentare zum Code hinzu
[Benutzerdefinierte Tastenkombinationen](https://www.bilibili.com/video/BV14s4y1E7jN) | Unterstützt benutzerdefinierte Tastenkombinationen
Modulare Gestaltung | Unterstützt leistungsstarke individuelle [Funktions-Plugins](https://github.com/binary-husky/chatgpt_academic/tree/master/crazy_functions). Plugins unterstützen [Hot-Updates](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[Selbstprogramm-Analyse](https://www.bilibili.com/video/BV1cj411A7VW) | [Funktions-Plugin] [Ein-Klick Verstehen](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A) der Quellcode dieses Projekts
[Programmanalyse](https://www.bilibili.com/video/BV1cj411A7VW) | [Funktions-Plugin] Ein-Klick-Analyse des Projektbaums anderer Python/C/C++/Java/Lua/...-Projekte
Lesen von Papieren, [Übersetzen](https://www.bilibili.com/video/BV1KT411x7Wn) von Papieren | [Funktions-Plugin] Ein-Klick Erklärung des gesamten LaTeX/PDF-Artikels und Erstellung einer Zusammenfassung
LaTeX-Volltext-Übersetzung und [Polieren](https://www.bilibili.com/video/BV1FT411H7c5/) | [Funktions-Plugin] Ein-Klick-Übersetzung oder-Polieren des LaTeX-Artikels
Bulk-Kommentargenerierung | [Funktions-Plugin] Ein-Klick Massenerstellung von Funktionskommentaren
Markdown [Chinesisch-Englisch Übersetzung](https://www.bilibili.com/video/BV1yo4y157jV/) | [Funktions-Plugin] Haben Sie die [README](https://github.com/binary-husky/chatgpt_academic/blob/master/docs/README_EN.md) in den oben genannten 5 Sprachen gesehen?
Analyse-Berichtserstellung von chat | [Funktions-Plugin] Automatische Zusammenfassung nach der Ausführung
[Funktion zur vollständigen Übersetzung von PDF-Artikeln](https://www.bilibili.com/video/BV1KT411x7Wn) | [Funktions-Plugin] Extrahiert Titel und Zusammenfassung der PDF-Artikel und übersetzt den gesamten Text (mehrere Threads)
[Arxiv-Assistent](https://www.bilibili.com/video/BV1LM4y1279X) | [Funktions-Plugin] Geben Sie die Arxiv-Artikel-URL ein und klicken Sie auf Eine-Klick-Übersetzung-Zusammenfassung + PDF-Download
[Google Scholar Integrations-Assistent](https://www.bilibili.com/video/BV19L411U7ia) | [Funktions-Plugin] Geben Sie eine beliebige Google Scholar Such-URL ein und lassen Sie gpt Ihnen bei der Erstellung von [relatedworks](https://www.bilibili.com/video/BV1GP411U7Az/) helfen
Internet-Informationen Aggregation + GPT | [Funktions-Plugin] Lassen Sie GPT eine Frage beantworten, indem es [zuerst Informationen aus dem Internet](https://www.bilibili.com/video/BV1om4y127ck/) sammelt und so die Informationen nie veralten
Anzeige von Formeln / Bildern / Tabellen | Zeigt Formeln in beiden Formen, [TeX-Format und gerendeter Form](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png), unterstützt Formeln und Code-Highlights
Unterstützung von PlugIns mit mehreren Threads | Unterstützt den Aufruf mehrerer Threads in Chatgpt, um Text oder Programme [Batch zu verarbeiten](https://www.bilibili.com/video/BV1FT411H7c5/)
Starten Sie das dunkle Gradio-[Thema](https://github.com/binary-husky/chatgpt_academic/issues/173) | Fügen Sie ```/?__theme=dark``` an das Ende der Browser-URL an, um das dunkle Thema zu aktivieren
[Unterstützung für mehrere LLM-Modelle](https://www.bilibili.com/video/BV1wT411p7yf), [API2D](https://api2d.com/) Interface-Unterstützung | Das Gefühl, gleichzeitig von GPT3.5, GPT4, [Tshinghua ChatGLM](https://github.com/THUDM/ChatGLM-6B), [Fudan MOSS](https://github.com/OpenLMLab/MOSS) bedient zu werden, muss toll sein, oder?
Zugriff auf weitere LLM-Modelle, Unterstützung von [huggingface deployment](https://huggingface.co/spaces/qingxu98/gpt-academic) | Hinzufügen der Newbing-Schnittstelle (neues Bing), Einführung der Unterstützung von [Jittorllms](https://github.com/Jittor/JittorLLMs) der Tsinghua-Universität, [LLaMA](https://github.com/facebookresearch/llama), [RWKV](https://github.com/BlinkDL/ChatRWKV) und [Pangu alpha](https://openi.org.cn/pangu/)
Weitere neue Funktionen (wie Bildgenerierung) …… | Siehe Ende dieses Dokuments ……

- Neue Oberfläche (Ändern Sie die LAYOUT-Option in `config.py`, um zwischen "Seitenlayout" und "Oben-unten-Layout" zu wechseln)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230361456-61078362-a966-4eb5-b49e-3c62ef18b860.gif" width="700" >
</div>- All buttons are dynamically generated by reading `functional.py`, and custom functions can be easily added, freeing up the clipboard.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Proofreading/Correcting
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- If the output contains formulas, they will be displayed in both tex format and rendered format for easy copying and reading.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Don't feel like reading the project code? Show off the entire project to chatgpt. 
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Multiple large language models are mixed and called together (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4).
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

---
# Installation
## Installation-Method 1: Run directly (Windows, Linux or MacOS)

1. Download the project
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. Configure API_KEY

Configure API KEY and other settings in `config.py`. [Special Network Environment Settings](https://github.com/binary-husky/gpt_academic/issues/1).

(P.S. When the program is running, it will first check whether there is a "config_private.py" private configuration file, and use the configuration defined in it to override the configuration of "config.py". Therefore, if you understand our configuration reading logic, we strongly recommend that you create a new configuration file named "config_private.py" next to "config.py" and transfer (copy) the configurations in "config.py" to "config_private.py". "config_private.py" is not controlled by git, which can make your privacy information more secure. P.S. The project also supports configuring most options through `environment variables`, and the writing format of environment variables refers to the `docker-compose` file. Reading priority: `environment variable` > `config_private.py` >`config.py`)


3. Install dependencies
```sh
# (Option I: If familar with Python) (Python version 3.9 or above, the newer the better), Note: Use the official pip source or Ali pip source, temporary switching method: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Option II: If not familiar with Python) Use anaconda with similar steps (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # Create an anaconda environment
conda activate gptac_venv                 # Activate the anaconda environment
python -m pip install -r requirements.txt # Same step as pip installation
```

<details><summary>Click to expand if supporting Tsinghua ChatGLM/Fudan MOSS as backend</summary>
<p>

[Optional Step] If supporting Tsinghua ChatGLM/Fudan MOSS as backend, additional dependencies need to be installed (Prerequisites: Familiar with Python + Used Pytorch + Sufficient computer configuration):
```sh
# [Optional Step I] Support Tsinghua ChatGLM. Remark: If encountering "Call ChatGLM fail Cannot load ChatGLM parameters", please refer to the following: 1: The above default installation is torch+cpu version. To use cuda, uninstall torch and reinstall torch+cuda; 2: If the model cannot be loaded due to insufficient machine configuration, you can modify the model precision in `request_llm/bridge_chatglm.py`, and modify all AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) to AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llm/requirements_chatglm.txt  

# [Optional Step II] Support Fudan MOSS
python -m pip install -r request_llm/requirements_moss.txt
git clone https://github.com/OpenLMLab/MOSS.git request_llm/moss # When executing this line of code, you must be in the project root path

# [Optional Step III] Make sure the AVAIL_LLM_MODELS in the config.py configuration file contains the expected models. Currently supported models are as follows (jittorllms series currently only supports docker solutions):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "newbing", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. Run
```sh
python main.py
```5. Testing Function Plugin
```
- Test function plugin template function (requires gpt to answer what happened today in history), you can use this function as a template to implement more complex functions
   Click "[Function Plugin Template Demo] Today in History"
```

## Installation-Method 2: Using Docker

1. Only ChatGPT (Recommended for most people)

``` sh
git clone https://github.com/binary-husky/chatgpt_academic.git  # Download the project
cd chatgpt_academic                                 # Enter the path
nano config.py                                      # Edit config.py with any text editor, Configure "Proxy","API_KEY"and"WEB_PORT" (e.g 50923) etc.
docker build -t gpt-academic .                      # Install

# (Last step-option 1) Under Linux environment, use `--net=host` is more convenient and quick
docker run --rm -it --net=host gpt-academic
# (Last step-option 2) Under macOS/windows environment, can only use the -p option to expose the container's port(eg.50923) to the port on the host.
docker run --rm -it -e WEB_PORT=50923 -p 50923:50923 gpt-academic
```

2. ChatGPT + ChatGLM + MOSS (Requires familiarity with Docker)

``` sh
# Modify docker-compose.yml, delete solution 1 and solution 3, and retain solution 2. Modify the configuration of solution 2 in docker-compose.yml, referring to the comments in it.
docker-compose up
```

3. ChatGPT+LLAMA+Pangu+RWKV(Requires familiarity with Docker)
``` sh
# Modify docker-compose.yml, delete solution 1 and solution 2, and retain solution 3. Modify the configuration of solution 3 in docker-compose.yml, referring to the comments in it.
docker-compose up
```


## Installation-Method 3: Other Deployment Options

1. How to use reverse proxy URL/Microsoft Azure API
Configure API_URL_REDIRECT according to the instructions in `config.py`.

2. Remote cloud server deployment (requires cloud server knowledge and experience)
Please visit [Deployment wiki-1](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)

3. Using WSL 2 (Windows subsystem for Linux)
Please visit [Deployment wiki-2](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)

4. How to run at a secondary URL (such as `http://localhost/subpath`)
Please visit [FastAPI operating instructions](docs/WithFastapi.md)

5. Use docker-compose to run
Please read docker-compose.yml and follow the prompts to operate.

---
# Advanced Usage
## Customize new convenience buttons / custom function plugins.

1. Customize new convenience buttons (Academic Shortcut Keys)
Open `core_functional.py` with any text editor, add an entry as follows, and then restart the program. (If the button has been added successfully and is visible, then the prefix and suffix can be hot-modified, and it will take effect without restarting the program.)
For example
```
"Super English to Chinese": {
   # Prefix, will be added before your input. For example, used to describe your requirements, such as translation, explaining code, polishing, etc.
    "Prefix": "Please translate the following content into Chinese, and then use a markdown table to explain the proper nouns that appear in the text one by one:\n\n", 
    
    # Suffix, will be added after your input. For example, combined with prefix, you can enclose your input content in quotes.
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

2. Custom function plugins

Write powerful function plugins to perform any task you want and can't think of.
The difficulty of plugin writing and debugging is very low in this project. As long as you have a certain knowledge of Python, you can implement your own plugin functions by imitating the template we provided.
For more information, please refer to the [Function Plugin Guide](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97).

---
# Latest Update
## New feature dynamics1. Funktion zur Speicherung von Dialogen. Rufen Sie im Bereich der Funktions-Plugins "Aktuellen Dialog speichern" auf, um den aktuellen Dialog als lesbares und wiederherstellbares HTML-Datei zu speichern. Darüber hinaus können Sie im Funktions-Plugin-Bereich (Dropdown-Menü) "Laden von Dialogverlauf" aufrufen, um den vorherigen Dialog wiederherzustellen. Tipp: Wenn Sie keine Datei angeben und stattdessen direkt auf "Laden des Dialogverlaufs" klicken, können Sie das HTML-Cache-Archiv anzeigen. Durch Klicken auf "Löschen aller lokalen Dialogverlaufsdatensätze" können alle HTML-Archiv-Caches gelöscht werden.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. Berichterstellung. Die meisten Plugins generieren nach Abschluss der Ausführung einen Arbeitsbericht.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

3. Modularisierte Funktionsgestaltung, einfache Schnittstellen mit leistungsstarken Funktionen.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

4. Dies ist ein Open-Source-Projekt, das sich "selbst übersetzen" kann.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="500" >
</div>

5. Die Übersetzung anderer Open-Source-Projekte ist kein Problem.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="500" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="500" >
</div>

6. Dekorieren Sie [`live2d`](https://github.com/fghrsh/live2d_demo) mit kleinen Funktionen (standardmäßig deaktiviert, Änderungen an `config.py` erforderlich).
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. Neue MOSS-Sprachmodellunterstützung.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236639178-92836f37-13af-4fdd-984d-b4450fe30336.png" width="500" >
</div>

8. OpenAI-Bildgenerierung.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

9. OpenAI-Audio-Analyse und Zusammenfassung.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

10. Latex-Proofreading des gesamten Textes.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" width="500" >
</div>


## Version:
- Version 3.5 (Todo): Rufen Sie alle Funktionserweiterungen dieses Projekts mit natürlicher Sprache auf (hohe Priorität).
- Version 3.4 (Todo): Verbesserte Unterstützung mehrerer Threads für Local Large Model (LLM).
- Version 3.3: + Internet-Informationssynthese-Funktion
- Version 3.2: Funktionserweiterungen unterstützen mehr Parameter-Schnittstellen (Speicherung von Dialogen, Interpretation beliebigen Sprachcodes + gleichzeitige Abfrage jeder LLM-Kombination)
- Version 3.1: Unterstützung mehrerer GPT-Modelle gleichzeitig! Unterstützung für API2D, Unterstützung für Lastenausgleich von mehreren API-Schlüsseln.
- Version 3.0: Unterstützung von Chatglm und anderen kleinen LLMs
- Version 2.6: Umstrukturierung der Plugin-Struktur zur Verbesserung der Interaktivität, Einführung weiterer Plugins
- Version 2.5: Automatische Aktualisierung, Problembehebung bei Quelltexten großer Projekte, wenn der Text zu lang ist oder Token überlaufen.
- Version 2.4: (1) Neue Funktion zur Übersetzung des gesamten PDF-Texts; (2) Neue Funktion zum Wechseln der Position des Eingabebereichs; (3) Neue Option für vertikales Layout; (4) Optimierung von Multithread-Funktions-Plugins.
- Version 2.3: Verbesserte Interaktivität mit mehreren Threads
- Version 2.2: Funktionserweiterungen unterstützen "Hot-Reload"
- Version 2.1: Faltbares Layout
- Version 2.0: Einführung von modularisierten Funktionserweiterungen
- Version 1.0: Grundlegende Funktionengpt_academic Entwickler QQ-Gruppe-2: 610599535

- Bekannte Probleme
    - Einige Browser-Übersetzungs-Plugins können die Frontend-Ausführung dieser Software stören.
    - Sowohl eine zu hohe als auch eine zu niedrige Version von Gradio führt zu verschiedenen Ausnahmen.

## Referenz und Lernen

```
Der Code bezieht sich auf viele Designs von anderen herausragenden Projekten, insbesondere:

# Projekt 1: ChatGLM-6B der Tsinghua Universität:
https://github.com/THUDM/ChatGLM-6B

# Projekt 2: JittorLLMs der Tsinghua Universität:
https://github.com/Jittor/JittorLLMs

# Projekt 3: Edge-GPT:
https://github.com/acheong08/EdgeGPT

# Projekt 4: ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# Projekt 5: ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Mehr:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
```