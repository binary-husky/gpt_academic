> **Note**
>
> Этот файл самовыражения автоматически генерируется модулем перевода markdown в этом проекте и может быть не на 100% правильным.
>
# <img src="logo.png" width="40" > GPT Академическая оптимизация (GPT Academic)

**Если вам нравится этот проект, пожалуйста, поставьте ему звезду. Если вы придумали более полезные языковые ярлыки или функциональные плагины, не стесняйтесь открывать issue или pull request. 
Чтобы перевести этот проект на произвольный язык с помощью GPT, ознакомьтесь и запустите [`multi_language.py`](multi_language.py) (экспериментальный).

> **Примечание**
> 
> 1. Обратите внимание, что только функциональные плагины (кнопки), помеченные **красным цветом**, поддерживают чтение файлов, некоторые плагины находятся в **выпадающем меню** в области плагинов. Кроме того, мы с наивысшим приоритетом рады и обрабатываем pull requests для любых новых плагинов!
> 
> 2. В каждом файле проекта функциональность описана в документе самоанализа [`self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A). С каждой итерацией выполнения версии вы можете в любое время вызвать повторное создание отчета о самоанализе этого проекта, щелкнув соответствующий функциональный плагин и вызвав GPT. Вопросы сборки описаны в [`wiki`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98). [Метод установки](#installation).
> 
> 3. Этот проект совместим и поощряет использование китайских языковых моделей chatglm и RWKV, пангу и т. Д. Поддержка нескольких api-key, которые могут существовать одновременно, может быть указан в файле конфигурации, например `API_KEY="openai-key1,openai-key2,api2d-key3"`. Если требуется временно изменить `API_KEY`, введите временный `API_KEY` в области ввода и нажмите клавишу Enter, чтобы он вступил в силу. 

> **Примечание**
>
> При установке зависимостей строго выбирайте версии, **указанные в файле requirements.txt**.
> 
> `pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`## Задание

Вы профессиональный переводчик научных статей.

Переведите этот файл в формате Markdown на русский язык. Не изменяйте существующие команды Markdown, ответьте только переведенными результатами.

## Результат

Функция | Описание
--- | ---
Однокнопочный стиль | Поддержка однокнопочного стиля и поиска грамматических ошибок в научных статьях
Однокнопочный перевод на английский и китайский | Однокнопочный перевод на английский и китайский
Однокнопочное объяснение кода | Показ кода, объяснение его, генерация кода, комментирование кода
[Настройка быстрых клавиш](https://www.bilibili.com/video/BV14s4y1E7jN) | Поддержка настройки быстрых клавиш
Модульный дизайн | Поддержка пользовательских функциональных плагинов мощных [функциональных плагинов](https://github.com/binary-husky/chatgpt_academic/tree/master/crazy_functions), плагины поддерживают [горячую замену](https://github.com/binary-husky/chatgpt_academic/wiki/Function-Plug-in-Guide)
[Анализ своей программы](https://www.bilibili.com/video/BV1cj411A7VW) | [Функциональный плагин] [Однокнопочный просмотр](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academicProject-Self-analysis-Report) исходного кода этого проекта
[Анализ программы](https://www.bilibili.com/video/BV1cj411A7VW) | [Функциональный плагин] Однокнопочный анализ дерева других проектов Python/C/C++/Java/Lua/...
Чтение статей, [перевод](https://www.bilibili.com/video/BV1KT411x7Wn) статей | [Функциональный плагин] Однокнопочное чтение полного текста научных статей и генерация резюме
Полный перевод [LaTeX](https://www.bilibili.com/video/BV1nk4y1Y7Js/) и совершенствование | [Функциональный плагин] Однокнопочный перевод или совершенствование LaTeX статьи
Автоматическое комментирование | [Функциональный плагин] Однокнопочное автоматическое генерирование комментариев функций
[Перевод](https://www.bilibili.com/video/BV1yo4y157jV/) Markdown на английский и китайский | [Функциональный плагин] Вы видели обе версии файлов [README](https://github.com/binary-husky/chatgpt_academic/blob/master/docs/README_EN.md) для этих 5 языков?
Отчет о чат-анализе | [Функциональный плагин] После запуска будет автоматически сгенерировано сводное извещение
Функция перевода полного текста [PDF-статьи](https://www.bilibili.com/video/BV1KT411x7Wn) | [Функциональный плагин] Извлечение заголовка и резюме [PDF-статьи](https://www.bilibili.com/video/BV1KT411x7Wn) и перевод всего документа (многопоточность)
[Arxiv Helper](https://www.bilibili.com/video/BV1LM4y1279X) | [Функциональный плагин] Введите URL статьи на arxiv и одним щелчком мыши переведите резюме и загрузите PDF
[Google Scholar Integration Helper](https://www.bilibili.com/video/BV19L411U7ia) | [Функциональный плагин] При заданном любом URL страницы поиска в Google Scholar позвольте gpt вам помочь [написать обзор](https://www.bilibili.com/video/BV1GP411U7Az/)
Сбор Интернет-информации + GPT | [Функциональный плагин] Однокнопочный [запрос информации из Интернета GPT](https://www.bilibili.com/video/BV1om4y127ck), затем ответьте на вопрос, чтобы информация не устарела никогда
Отображение формул / изображений / таблиц | Может одновременно отображать формулы в [формате Tex и рендеринге](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png), поддерживает формулы, подсвечивает код
Поддержка функций с многопоточностью | Поддержка многопоточного вызова chatgpt, однокнопочная обработка [больших объемов текста](https://www.bilibili.com/video/BV1FT411H7c5/) или программ
Темная тема gradio для запуска приложений | Добавьте ```/?__theme=dark``` после URL в браузере, чтобы переключиться на темную тему
[Поддержка нескольких моделей LLM](https://www.bilibili.com/video/BV1wT411p7yf), [API2D](https://api2d.com/) | Они одновременно обслуживаются GPT3.5, GPT4, [Clear ChatGLM](https://github.com/THUDM/ChatGLM-6B), [Fudan MOSS](https://github.com/OpenLMLab/MOSS)
Подключение нескольких новых моделей LLM, поддержка деплоя[huggingface](https://huggingface.co/spaces/qingxu98/gpt-academic) | Подключение интерфейса Newbing (новый Bing), подключение поддержки [LLaMA](https://github.com/facebookresearch/llama), поддержка [RWKV](https://github.com/BlinkDL/ChatRWKV) и [Pangu α](https://openi.org.cn/pangu/)
Больше новых функций (генерация изображения и т. д.) | См. на конце этого файла…- All buttons are dynamically generated by reading functional.py, and custom functions can be freely added to liberate the clipboard
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Revision/Correction
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- If the output contains formulas, they will be displayed in both tex and rendered form for easy copying and reading
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Don't feel like looking at project code? Show the entire project directly in chatgpt
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Mixing multiple large language models (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4）
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

In `config.py`, configure API KEY and other settings, [special network environment settings] (https://github.com/binary-husky/gpt_academic/issues/1).

(P.S. When the program is running, it will first check whether there is a secret configuration file named `config_private.py` and use the configuration in it to replace the same name in` config.py`. Therefore, if you understand our configuration reading logic, we strongly recommend that you create a new configuration file named `config_private.py` next to `config.py`, and transfer (copy) the configuration in `config.py` to `config_private.py`. `config_private.py` is not controlled by git, which can make your privacy information more secure. P.S. The project also supports configuring most options through `environment variables`, and the writing format of environment variables refers to the `docker-compose` file. Priority of read: `environment variable`>`config_private.py`>`config.py`)


3. Install dependencies
```sh
# （Option I: If familiar with Python）(Python version 3.9 or above, the newer the better), note: use the official pip source or the aliyun pip source, temporary switching source method: python -m pip install -r requirements.txt - i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# （Option II: If unfamiliar with Python）Use Anaconda, the steps are also similar (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # create an Anaconda environment
conda activate gptac_venv                 # activate Anaconda environment
python -m pip install -r requirements.txt # This step is the same as the pip installation
```

<details><summary> If you need to support Tsinghua ChatGLM/Fudan MOSS as backend, click here to expand </summary>
<p>

[Optional step] If you need to support Tsinghua ChatGLM/Fudan MOSS as backend, you need to install more dependencies (prerequisites: familiar with Python + have used Pytorch + computer configuration is strong):
```sh
# [Optional step I] Support Tsinghua ChatGLM. Tsinghua ChatGLM note: If you encounter the "Call ChatGLM fail cannot load ChatGLM parameters normally" error, refer to the following: 1: The default installation above is torch+cpu version, and cuda is used Need to uninstall torch and reinstall torch+cuda; 2: If you cannot load the model due to insufficient local configuration, you can modify the model accuracy in request_llm/bridge_chatglm.py, AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) Modify to AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llm/requirements_chatglm.txt  

# [Optional step II] Support Fudan MOSS
python -m pip install -r request_llm/requirements_moss.txt
git clone https://github.com/OpenLMLab/MOSS.git request_llm/moss  # Note that when executing this line of code, you must be in the project root path

# [Optional step III] Make sure the AVAIL_LLM_MODELS in the config.py configuration file contains the expected models. Currently, all supported models are as follows (the jittorllms series currently only supports the docker solution):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "newbing", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. Run
```sh
python main.py
```5. Testing Function Plugin
```
- Testing function plugin template function (requires GPT to answer what happened in history today), you can use this function as a template to implement more complex functions
    Click "[Function plugin Template Demo] On this day in history"
```

## Installation - Method 2: Using Docker

1. ChatGPT only (recommended for most people)

``` sh
git clone https://github.com/binary-husky/chatgpt_academic.git  # download the project
cd chatgpt_academic                                 # enter the path
nano config.py                                      # edit config.py with any text editor to configure "Proxy", "API_KEY", and "WEB_PORT" (eg 50923)
docker build -t gpt-academic .                      # install

# (Last step-Option 1) In a Linux environment, using `--net=host` is more convenient and faster
docker run --rm -it --net=host gpt-academic
# (Last step-Option 2) In macOS/windows environment, only -p option can be used to expose the port on the container (eg 50923) to the port on the host
docker run --rm -it -e WEB_PORT=50923 -p 50923:50923 gpt-academic
```

2. ChatGPT + ChatGLM + MOSS (requires familiarity with Docker)

``` sh
# Edit docker-compose.yml, delete solutions 1 and 3, and keep solution 2. Modify the configuration of solution 2 in docker-compose.yml, refer to the comments in it
docker-compose up
```

3. ChatGPT + LLAMA + PanGu + RWKV (requires familiarity with Docker)
``` sh
# Edit docker-compose.yml, delete solutions 1 and 2, and keep solution 3. Modify the configuration of solution 3 in docker-compose.yml, refer to the comments in it
docker-compose up
```


## Installation Method 3: Other Deployment Methods

1. How to use reverse proxy URL/Microsoft Azure API
Configure API_URL_REDIRECT according to the instructions in `config.py`.

2. Remote Cloud Server Deployment (Requires Knowledge and Experience of Cloud Servers)
Please visit [Deployment Wiki-1](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)

3. Using WSL2 (Windows Subsystem for Linux subsystem)
Please visit [Deployment Wiki-2](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)

4. How to run at the secondary URL (such as `http://localhost/subpath`)
Please visit [FastAPI Operation Instructions](docs/WithFastapi.md)

5. Using docker-compose to run
Please read docker-compose.yml and follow the prompts to operate.

---
# Advanced Usage
## Customize new convenient buttons / custom function plugins

1. Customize new convenient buttons (academic shortcuts)
Open `core_functional.py` with any text editor, add an entry as follows, and then restart the program. (If the button has been added successfully and is visible, both prefixes and suffixes can be hot-modified without having to restart the program.)
For example:
```
"Super English to Chinese": {
    # Prefix, will be added before your input. For example, describe your requirements, such as translation, code interpretation, polishing, etc.
    "Prefix": "Please translate the following content into Chinese, and then explain each proper noun that appears in the text with a markdown table:\n\n", 
    
    # Suffix, will be added after your input. For example, with the prefix, you can enclose your input content in quotes.
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

2. Custom function plugin

Write powerful function plugins to perform any task you can and can't imagine.
The difficulty of debugging and writing plugins in this project is very low. As long as you have a certain knowledge of python, you can implement your own plugin function by imitating the template we provide.
Please refer to the [Function Plugin Guide](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97) for details.

---
# Latest Update
## New feature dynamic

1. Сохранение диалогов. Вызовите "Сохранить текущий диалог" в разделе функций-плагина, чтобы сохранить текущий диалог как файл HTML, который можно прочитать и восстановить. Кроме того, вызовите «Загрузить архив истории диалога» в меню функций-плагина, чтобы восстановить предыдущую сессию. Совет: если нажать кнопку "Загрузить исторический архив диалога" без указания файла, можно просмотреть кэш исторических файлов HTML. Щелкните "Удалить все локальные записи истории диалогов", чтобы удалить все файловые кэши HTML.

2. Создание отчетов. Большинство плагинов создают рабочий отчет после завершения выполнения.
 
3. Модульный дизайн функций, простой интерфейс, но сильный функционал.

4. Это проект с открытым исходным кодом, который может «сам переводить себя».

5. Перевод других проектов с открытым исходным кодом - это не проблема.

6. Мелкие функции декорирования [live2d](https://github.com/fghrsh/live2d_demo) (по умолчанию отключены, нужно изменить `config.py`).

7. Поддержка большой языковой модели MOSS.

8. Генерация изображений с помощью OpenAI.

9. Анализ и подведение итогов аудиофайлов с помощью OpenAI.

10. Полный цикл проверки правописания с использованием LaTeX.

## Версии:
- Версия 3.5 (Todo): использование естественного языка для вызова функций-плагинов проекта (высокий приоритет)
- Версия 3.4 (Todo): улучшение многопоточной поддержки локальных больших моделей чата.
- Версия 3.3: добавлена функция объединения интернет-информации.
- Версия 3.2: функции-плагины поддерживают большое количество параметров (сохранение диалогов, анализирование любого языка программирования и одновременное запрос LLM-групп).
- Версия 3.1: поддержка одновременного запроса нескольких моделей GPT! Поддержка api2d, сбалансированное распределение нагрузки по нескольким ключам api.
- Версия 3.0: поддержка chatglm и других небольших LLM.
- Версия 2.6: перестройка структуры плагинов, улучшение интерактивности, добавлено больше плагинов.
- Версия 2.5: автоматическое обновление для решения проблемы длинного текста и переполнения токенов при обработке больших проектов.
- Версия 2.4: (1) добавлена функция полного перевода PDF; (2) добавлена функция переключения положения ввода; (3) добавлена опция вертикального макета; (4) оптимизация многопоточности плагинов.
- Версия 2.3: улучшение многопоточной интерактивности.
- Версия 2.2: функции-плагины поддерживают горячую перезагрузку.
- Версия 2.1: раскрывающийся макет.
- Версия 2.0: использование модульных функций-плагинов.
- Версия 1.0: базовые функции.

gpt_academic Разработчик QQ-группы-2: 610599535

- Известные проблемы
    - Некоторые плагины перевода в браузерах мешают работе фронтенда этого программного обеспечения
    - Высокая или низкая версия gradio может вызвать множество исключений

## Ссылки и учебные материалы

```
Мы использовали многие концепты кода из других отличных проектов, включая:

# Проект 1: Qinghua ChatGLM-6B:
https://github.com/THUDM/ChatGLM-6B

# Проект 2: Qinghua JittorLLMs:
https://github.com/Jittor/JittorLLMs

# Проект 3: Edge-GPT:
https://github.com/acheong08/EdgeGPT

# Проект 4: Chuanhu ChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# Проект 5: ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Больше:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
```