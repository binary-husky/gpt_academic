


> **Hinweis**
>
> Dieses README wurde mithilfe der GPT-Übersetzung (durch das Plugin dieses Projekts) erstellt und ist nicht zu 100 % zuverlässig. Bitte überprüfen Sie die Übersetzungsergebnisse sorgfältig.
>
> 7. November 2023: Beim Installieren der Abhängigkeiten bitte nur die in der `requirements.txt` **angegebenen Versionen** auswählen. Installationsbefehl: `pip install -r requirements.txt`.


# <div align=center><img src="logo.png" width="40"> GPT Academic (GPT Akademisch)</div>

**Wenn Ihnen dieses Projekt gefällt, geben Sie ihm bitte einen Star. Wenn Sie praktische Tastenkombinationen oder Plugins entwickelt haben, sind Pull-Anfragen willkommen!**

Wenn Ihnen dieses Projekt gefällt, geben Sie ihm bitte einen Star.
Um dieses Projekt mit GPT in eine beliebige Sprache zu übersetzen, lesen Sie [`multi_language.py`](multi_language.py) (experimentell).

> **Hinweis**
>
> 1. Beachten Sie bitte, dass nur die mit **hervorgehobenen** Plugins (Schaltflächen) Dateien lesen können. Einige Plugins befinden sich im **Drop-down-Menü** des Plugin-Bereichs. Außerdem freuen wir uns über jede neue Plugin-PR mit **höchster Priorität**.
>
> 2. Die Funktionen jeder Datei in diesem Projekt sind im [Selbstanalysebericht `self_analysis.md`](https://github.com/binary-husky/gpt_academic/wiki/GPT-Academic-Selbstanalysebericht) ausführlich erläutert. Sie können jederzeit auf die relevanten Funktions-Plugins klicken und GPT aufrufen, um den Selbstanalysebericht des Projekts neu zu generieren. Häufig gestellte Fragen finden Sie im [`Wiki`](https://github.com/binary-husky/gpt_academic/wiki). [Standardinstallationsmethode](#installation) | [Ein-Klick-Installationsskript](https://github.com/binary-husky/gpt_academic/releases) | [Konfigurationsanleitung](https://github.com/binary-husky/gpt_academic/wiki/Projekt-Konfigurationsanleitung).
>
> 3. Dieses Projekt ist kompatibel mit und unterstützt auch die Verwendung von inländischen Sprachmodellen wie ChatGLM. Die gleichzeitige Verwendung mehrerer API-Schlüssel ist möglich, indem Sie sie in der Konfigurationsdatei wie folgt angeben: `API_KEY="openai-key1,openai-key2,azure-key3,api2d-key4"`. Wenn Sie den `API_KEY` vorübergehend ändern möchten, geben Sie vorübergehend den temporären `API_KEY` im Eingabebereich ein und drücken Sie die Eingabetaste, um die Änderung wirksam werden zu lassen.




<div align="center">

Funktionen (⭐= Kürzlich hinzugefügte Funktion) | Beschreibung
--- | ---
⭐[Neues Modell integrieren](https://github.com/binary-husky/gpt_academic/wiki/%E5%A6%82%E4%BD%95%E5%88%87%E6%8D%A2%E6%A8%A1%E5%9E%8B)! | Baidu [Qianfan](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Nlks5zkzu) und Wenxin Yanyi, [Tongyi Qianwen](https://modelscope.cn/models/qwen/Qwen-7B-Chat/summary), Shanghai AI-Lab [Shusheng](https://github.com/InternLM/InternLM), Xunfei [Xinghuo](https://xinghuo.xfyun.cn/), [LLaMa2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf), Cognitive Graph API, DALLE3
Verfeinern, Übersetzen, Codierung erläutern | Ein-Klick-Verfeinerung, Übersetzung, Suche nach grammatikalischen Fehlern in wissenschaftlichen Arbeiten, Erklärung von Code
[Eigene Tastenkombinationen](https://www.bilibili.com/video/BV14s4y1E7jN) definieren | Eigene Tastenkombinationen definieren
Modulare Gestaltung | Ermöglicht die Verwendung benutzerdefinierter leistungsstarker [Plugins](https://github.com/binary-husky/gpt_academic/tree/master/crazy_functions), Plugins unterstützen [Hot-Reload](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[Programmanalyse](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugin] Ermöglicht die Erstellung einer Projekthierarchie für Python/C/C++/Java/Lua/... mit nur einem Klick oder [Selbstanalyse](https://www.bilibili.com/video/BV1cj411A7VW)
Lesen von Forschungsarbeiten, Übersetzen von Forschungsarbeiten | [Plugin] Ermöglicht eine Umwandlung des gesamten Latex-/PDF-Forschungspapiers mit nur einem Klick und generiert eine Zusammenfassung
Latex-Übersetzung des vollständigen Textes, Ausbesserung | [Plugin] Ermöglicht eine Übersetzung oder Verbesserung der Latex-Forschungsarbeit mit nur einem Klick
Erzeugen von Batch-Anmerkungen | [Plugin] Erzeugt Funktionserläuterungen in Stapeln
Markdown- [En-De-Übersetzung](https://www.bilibili.com/video/BV1yo4y157jV/) | [Plugin] Haben Sie die [README](https://github.com/binary-husky/gpt_academic/blob/master/docs/README_EN.md) in den oben genannten 5 Sprachen gesehen?
Erzeugen eines Chat-Analyseberichts | [Plugin] Generiert einen zusammenfassenden Bericht nach der Ausführung
PDF-Textübersetzungsmerkmal | [Plugin] Extrahiert Titel und Zusammenfassung des PDF-Dokuments und übersetzt den vollständigen Text (mehrfädig)
Arxiv-Assistent | [Plugin] Geben Sie die URL eines Arxiv-Artikels ein, um eine Zusammenfassung zu übersetzen und die PDF-Datei herunterzuladen
Automatische Überprüfung von Latex-Artikeln | [Plugin] Überprüft die Grammatik und Rechtschreibung von Latex-Artikeln nach dem Vorbild von Grammarly und generiert eine PDF-Vergleichsdatei
Google Scholar Integration Assistant | [Plugin] Geben Sie eine beliebige URL der Google Scholar-Suchseite ein und lassen Sie GPT Ihre [Verwandten Arbeiten](https://www.bilibili.com/video/BV1GP411U7Az/) schreiben
Internetinformationsaggregation + GPT | [Plugin] Ermöglicht es GPT, Fragen durch das Durchsuchen des Internets zu beantworten und Informationen immer auf dem neuesten Stand zu halten
⭐Feine Übersetzung von Arxiv-Artikeln ([Docker](https://github.com/binary-husky/gpt_academic/pkgs/container/gpt_academic_with_latex)) | [Plugin] Übersetzt Arxiv-Artikel [mit hoher Qualität](https://www.bilibili.com/video/BV1dz4y1v77A/) mit einem Klick - das beste Übersetzungstool für wissenschaftliche Artikel
⭐[Echtzeit-Spracheingabe](https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md) | [Plugin] [Asynchrones Lauschen auf Audio-Eingabe](https://www.bilibili.com/video/BV1AV4y187Uy/), automatisches Zerschneiden des Textes, automatische Suche nach dem richtigen Zeitpunkt zur Beantwortung
Darstellen von Formeln/Bildern/Tabellen | Zeigt Formeln sowohl in [TEX-](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png)- als auch in gerenderten Formen an, unterstützt Formeln und Code-Hervorhebung
⭐AutoGen Multi-Agent Plugin | [Plugin] Erforscht die Möglichkeiten des emergenten Verhaltens von Multi-Agent-Systemen mit Microsoft AutoGen!
Start im Dark-Theme | Um das Dark-Theme zu aktivieren, fügen Sie ```/?__theme=dark``` am Ende der URL im Browser hinzu
[Mehrsprachige LLM-Modelle](https://www.bilibili.com/video/BV1wT411p7yf) unterstützt | Es ist sicherlich beeindruckend, von GPT3.5, GPT4, [ChatGLM2 der Tsinghua University](https://github.com/THUDM/ChatGLM2-6B), [MOSS der Fudan University](https://github.com/OpenLMLab/MOSS) bedient zu werden, oder?
⭐ChatGLM2 Feinabstimmungsmodell | Unterstützt das Laden von ChatGLM2-Feinabstimmungsmodellen und bietet Unterstützung für ChatGLM2-Feinabstimmungsassistenten
Integration weiterer LLM-Modelle, Unterstützung von [Huggingface-Deployment](https://huggingface.co/spaces/qingxu98/gpt-academic) | Hinzufügen der Newbing-Schnittstelle (neues Bing), Einführung der [Jittorllms der Tsinghua University](https://github.com/Jittor/JittorLLMs) zur Unterstützung von LLaMA und PanGu Alpha
⭐[void-terminal](https://github.com/binary-husky/void-terminal) Pip-Paket | Verwenden Sie das Projekt in Python direkt, indem Sie das gesamte Funktionsplugin verwenden (in Entwicklung)
⭐Void-Terminal-Plugin | [Plugin] Verwenden Sie natürliche Sprache, um andere Funktionen dieses Projekts direkt zu steuern
Weitere Funktionen anzeigen (z. B. Bildgenerierung) …… | Siehe das Ende dieses Dokuments ……
</div>


- Neues Interface (Ändern Sie die LAYOUT-Option in der `config.py`, um zwischen "Links-Rechts-Layout" und "Oben-Unten-Layout" zu wechseln)
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/d81137c3-affd-4cd1-bb5e-b15610389762" width="700" >
</div>


- Alle Schaltflächen werden dynamisch aus der `functional.py` generiert und ermöglichen das beliebige Hinzufügen benutzerdefinierter Funktionen zur Befreiung der Zwischenablage.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Überarbeiten/Korrigieren
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>



- If the output contains formulas, they will be displayed in both tex format and rendering format for easy copying and reading.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Don't want to look at the project code? Show off the whole project directly in chatgpt's mouth.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Multiple large language models mixed calling (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

# Installation
### Installation Method I: Run directly (Windows, Linux or MacOS)

1. Download the project
```sh
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git
cd gpt_academic
```

2. Configure API_KEY

In `config.py`, configure API KEY and other settings, [click to view special network environment configuration methods](https://github.com/binary-husky/gpt_academic/issues/1). [Wiki page](https://github.com/binary-husky/gpt_academic/wiki/Project-Configuration-Instructions).

「 The program will first check if there is a confidential configuration file named `config_private.py` and use its configuration to override the configuration with the same name in `config.py`. If you understand this reading logic, we strongly recommend that you create a new configuration file named `config_private.py` next to `config.py` and move (copy) the configuration in `config.py` to `config_private.py` (only copy the configuration items that you have modified). 」

「 You can configure the project through `environment variables`. The format of environment variables can refer to the `docker-compose.yml` file or our [Wiki page](https://github.com/binary-husky/gpt_academic/wiki/Project-Configuration-Instructions). The priority of configuration reading is: `environment variables` > `config_private.py` > `config.py`. 」


3. Install dependencies
```sh
# (Option I: if you are familiar with python, python>=3.9) Note: Use the official pip source or Ali pip source, temporary method to change the source: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Option II: Using Anaconda) The steps are similar (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # Create an anaconda environment
conda activate gptac_venv                 # Activate the anaconda environment
python -m pip install -r requirements.txt # This step is the same as installing with pip
```


<details><summary>If you need support for Tsinghua ChatGLM2/Fudan MOSS/RWKV as backend, please click to expand.</summary>
<p>

[Optional] If you need to support Tsinghua ChatGLM2/Fudan MOSS as the backend, you need to install additional dependencies (Prerequisites: Familiar with Python + Have used PyTorch + Strong computer configuration):
```sh
# [Optional Step I] Support Tsinghua ChatGLM2. Tsinghua ChatGLM note: If you encounter the error "Call ChatGLM fail cannot load ChatGLM parameters normally", refer to the following: 1: The default installation above is torch+cpu version. To use cuda, you need to uninstall torch and reinstall torch+cuda; 2: If you cannot load the model due to insufficient computer configuration, you can modify the model accuracy in request_llm/bridge_chatglm.py. Change AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) to AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llms/requirements_chatglm.txt

# [Optional Step II] Support Fudan MOSS
python -m pip install -r request_llms/requirements_moss.txt
git clone --depth=1 https://github.com/OpenLMLab/MOSS.git request_llms/moss  # When executing this line of code, you must be in the root path of the project

# [Optional Step III] Support RWKV Runner
Refer to the wiki: https://github.com/binary-husky/gpt_academic/wiki/Support-RWKV-Runner

# [Optional Step IV] Make sure the AVAIL_LLM_MODELS in config.py includes the expected models. The currently supported models are as follows (the jittorllms series only supports the docker solution at present):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. Run
```sh
python main.py
```

### Installation Method II: Use Docker

0. Deploy all capabilities of the project (this is a large image that includes cuda and latex. But if you have a slow internet speed or a small hard drive, it is not recommended to use this)
[![fullcapacity](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml)

``` sh
# Modify docker-compose.yml, keep solution 0 and delete other solutions. Then run:
docker-compose up
```

1. ChatGPT + Wenxin's words + spark and other online models (recommended for most people)
[![basic](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml)
[![basiclatex](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml)
[![basicaudio](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml)

``` sh
# Modify docker-compose.yml, keep solution 1 and delete other solutions. Then run:
docker-compose up
```

P.S. If you need the Latex plugin functionality, please refer to the Wiki. Also, you can directly use solution 4 or 0 to get the Latex functionality.

2. ChatGPT + ChatGLM2 + MOSS + LLAMA2 + Thousand Questions (Requires familiarity with [Nvidia Docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#installing-on-ubuntu-and-debian) runtime)
[![chatglm](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml)

``` sh
# Modify docker-compose.yml, keep solution 2 and delete other solutions. Then run:
docker-compose up
```


### Installation Method III: Other Deployment Methods
1. **Windows One-Click Script**.
Windows users who are completely unfamiliar with the python environment can download the one-click script for installation without local models in the published [Release](https://github.com/binary-husky/gpt_academic/releases).
The script is contributed by [oobabooga](https://github.com/oobabooga/one-click-installers).

2. Use third-party APIs, Azure, Wenxin's words, Spark, etc., see [Wiki page](https://github.com/binary-husky/gpt_academic/wiki/Project-Configuration-Instructions)

3. Pit avoidance guide for cloud server remote deployment.
Please visit the [Cloud Server Remote Deployment Wiki](https://github.com/binary-husky/gpt_academic/wiki/Cloud-Server-Remote-Deployment-Guide)

4. Some new deployment platforms or methods
    - Use Sealos [one-click deployment](https://github.com/binary-husky/gpt_academic/issues/993).
    - Use WSL2 (Windows Subsystem for Linux). Please visit the [deployment wiki-2](https://github.com/binary-husky/gpt_academic/wiki/Deploy-on-Windows-Subsystem-for-Linux-WSL2)
    - How to run under a subpath (such as `http://localhost/subpath`). Please visit [FastAPI Running Instructions](docs/WithFastapi.md)



# Fortgeschrittene Nutzung
### I: Benutzerdefinierte Tasten hinzufügen (akademische Hotkeys)
Öffnen Sie die Datei `core_functional.py` mit einem beliebigen Texteditor und fügen Sie folgenden Eintrag hinzu. Starten Sie dann das Programm neu. (Wenn die Schaltfläche bereits vorhanden ist, können sowohl das Präfix als auch das Suffix schnell geändert werden, ohne dass das Programm neu gestartet werden muss.)

Beispiel:
```
"Übersetzung von Englisch nach Chinesisch": {
    # Präfix, wird vor Ihrer Eingabe hinzugefügt. Zum Beispiel, um Ihre Anforderungen zu beschreiben, z.B. Übersetzen, Code erklären, verbessern usw.
    "Präfix": "Bitte übersetzen Sie den folgenden Abschnitt ins Chinesische und erklären Sie dann jedes Fachwort in einer Markdown-Tabelle:\n\n",

    # Suffix, wird nach Ihrer Eingabe hinzugefügt. Zum Beispiel, um Ihre Eingabe in Anführungszeichen zu setzen.
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

### II: Benutzerdefinierte Funktionsplugins
Schreiben Sie leistungsstarke Funktionsplugins, um beliebige Aufgaben zu erledigen, die Sie wünschen oder nicht erwartet haben.
Das Erstellen und Debuggen von Plugins in diesem Projekt ist einfach und erfordert nur Grundkenntnisse in Python. Sie können unser bereitgestelltes Template verwenden, um Ihre eigene Plugin-Funktion zu implementieren.
Weitere Informationen finden Sie in der [Plugin-Anleitung](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97).


# Aktualisierungen
### I: Neuigkeiten

1. Dialogspeicherungsfunktion. Rufen Sie im Funktionspluginbereich "Aktuellen Dialog speichern" auf, um den aktuellen Dialog als lesbare und wiederherstellbare HTML-Datei zu speichern.
Darüber hinaus können Sie im Funktionspluginbereich (Dropdown-Menü) "Dialoghistorie laden" aufrufen, um frühere Sitzungen wiederherzustellen.
Tipp: Wenn kein Dateiname angegeben ist, können Sie direkt auf "Dialoghistorie laden" klicken, um den Verlauf des HTML-Archivs anzuzeigen.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. ⭐ Latex/Arxiv-Papierübersetzungsfunktion ⭐
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/002a1a75-ace0-4e6a-94e2-ec1406a746f1" height="250" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/9fdcc391-f823-464f-9322-f8719677043b" height="250" >
</div>

3. Leere Terminaloberfläche (Verständnis der Benutzerabsicht und automatischer Aufruf anderer Plugins aus natürlicher Spracheingabe)

- Schritt 1: Geben Sie "Bitte Plugin aufrufen, um das PDF-Papier zu übersetzen, dessen Adresse https://openreview.net/pdf?id=rJl0r3R9KX ist" ein.
- Schritt 2: Klicken Sie auf "Leere Terminaloberfläche".

<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/66f1b044-e9ff-4eed-9126-5d4f3668f1ed" width="500" >
</div>

4. Modulare Funktionsgestaltung mit einfacher Schnittstelle für leistungsstarke Funktionen
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

5. Übersetzung und Lösung anderer Open-Source-Projekte
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" height="250" >
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" height="250" >
</div>

6. Funktionen zur Dekoration von [live2d](https://github.com/fghrsh/live2d_demo) (standardmäßig deaktiviert, config.py muss geändert werden)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-677397d7-abe6-4358-9bef-3c14a7041b59.png" width="500" >
</div>

7. OpenAI-Bildgenerierung
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

8. OpenAI-Audioanalyse und Zusammenfassung
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

9. Latex-Volltextkorrektur
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" height="200" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/476f66d9-7716-4537-b5c1-735372c25adb" height="200">
</div>

10. Sprach- und Themenwechsel
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/b6799499-b6fb-4f0c-9c8e-1b441872f4e8" width="500" >
</div>



### II: Versionen:
- Version 3.70 (ausstehend): Optimierung des AutoGen-Plugin-Themas und Entwicklung einer Reihe von abgeleiteten Plugins
- Version 3.60: Einführung von AutoGen als Grundlage für neue Plugin-Generation
- Version 3.57: Unterstützung von GLM3, SparkV3, WenxinYiyanV4, Behebung von Problemen bei gleichzeitiger Verwendung von lokalen Modellen
- Version 3.56: Dynamische Hinzufügung von Basisfunktionsbuttons, neue Übersichtsseite für PDFs
- Version 3.55: Überarbeitung der Benutzeroberfläche, Hinzufügung von Schwebefenstern und Menüleiste
- Version 3.54: Neuer dynamischer Code interpretier (Code Interpreter) (unfertig)
- Version 3.53: Unterstützung für dynamische Auswahl verschiedener Oberflächenthemen, Verbesserung der Stabilität und Behebung von Mehrbenutzerkonflikten
- Version 3.50: Verwenden Sie natürliche Sprache, um alle Funktionen dieses Projekts aufzurufen (leeres Terminal), Unterstützung für Plugin-Kategorien, verbesserte Benutzeroberfläche, neue Themen
- Version 3.49: Unterstützung für Baidu Qianfan Platform und WenxinYiyan
- Version 3.48: Unterstützung für Alibaba Damo Academy Tongyi Qianwen, Shanghai AI-Lab Shusheng, Xunfei Spark
- Version 3.46: Vollständig automatisierter Echtzeit-Sprachdialog
- Version 3.45: Anpassbare ChatGLM2-Feinjustierung
- Version 3.44: Offizielle Unterstützung für Azure, Verbesserung der Benutzerfreundlichkeit der Benutzeroberfläche
- Version 3.4: Hinzufügen von Arxiv-Papierübersetzung, LaTeX-Papierkorrektur
- Version 3.3: Hinzufügen von Internet-Informationen
- Version 3.2: Funktionsplugins unterstützen weitere Parameter (Dialog speichern, beliebigen Code analysieren und nach beliebigen LLM-Kombinationen fragen)
- Version 3.1: Unterstützung für die gleichzeitige Abfrage mehrerer GPT-Modelle! Unterstützung für API-Schlüssel-Lastenausgleich
- Version 3.0: Unterstützung von ChatGLM und anderen kleinen LLMs
- Version 2.6: Neugestaltung der Plugin-Struktur, Verbesserung der Interaktivität, Hinzufügen weiterer Plugins
- Version 2.5: Auto-Update zur Lösung von Problemen mit zu langem Text oder Tokenüberschuss beim Zusammenfassen von Code
- Version 2.4: (1) Hinzufügen der Funktion zur Übersetzung des vollständigen PDF-Texts; (2) Neues Feature zum Wechseln der Position des Eingabebereichs; (3) Hinzufügen der Option für eine vertikale Ausrichtung; (4) Verbesserung der Multithreading-Funktionen von Plugins.
- Version 2.3: Verbesserte Multithreading-Interaktivität
- Version 2.2: Funktionsplugins können heiß neu geladen werden
- Version 2.1: Faltbare Layouts
- Version 2.0: Einführung modularer Funktionsplugins
- Version 1.0: Grundfunktionen

Entwickler-QQ-Gruppe von GPT Academic: `610599535`

- Bekannte Probleme
    - Einige Browserübersetzungsplugins beeinflussen die Frontend-Ausführung dieser Software
    - Die offizielle Version von Gradio hat derzeit viele Kompatibilitätsprobleme. Installieren Sie Gradio daher unbedingt über `requirement.txt`.

### III: Themen
Sie können das Theme ändern, indem Sie die Option `THEME` (config.py) ändern.
1. `Chuanhu-Small-and-Beautiful` [Link](https://github.com/GaiZhenbiao/ChuanhuChatGPT/)


### IV: Entwicklungszweige dieses Projekts

1. `master` Branch: Hauptzweig, stabile Version
2. `frontier` Branch: Entwicklungsbranch, Testversion


### V: Referenzen und Lernen

```
Der Code basiert auf dem Design anderer herausragender Projekte. Die Reihenfolge ist beliebig:

# ChatGLM2-6B von Tsinghua:
https://github.com/THUDM/ChatGLM2-6B

# JittorLLMs von Tsinghua:
https://github.com/Jittor/JittorLLMs

# ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Edge-GPT:
https://github.com/acheong08/EdgeGPT

# ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT



# Oobabooga One-Click-Installations:
https://github.com/oobabooga/one-click-installers

# Weitere:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
