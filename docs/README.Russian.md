


> **Примечание**
>
> Этот README был переведен с помощью GPT (реализовано с помощью плагина этого проекта) и не может быть полностью надежным, пожалуйста, внимательно проверьте результаты перевода.
>
> 7 ноября 2023 года: При установке зависимостей, пожалуйста, выберите **указанные версии** из `requirements.txt`. Команда установки: `pip install -r requirements.txt`.


# <div align=center><img src="logo.png" width="40"> GPT Academic (GPT Академический)</div>

**Если вам нравится этот проект, пожалуйста, поставьте звезду; если у вас есть удобные горячие клавиши или плагины, приветствуются pull requests!**
Чтобы перевести этот проект на произвольный язык с помощью GPT, прочтите и выполните [`multi_language.py`](multi_language.py) (экспериментально).

> **Примечание**
>
> 1. Пожалуйста, обратите внимание, что только плагины (кнопки), выделенные **жирным шрифтом**, поддерживают чтение файлов, некоторые плагины находятся в выпадающем меню **плагинов**. Кроме того, мы с радостью приветствуем и обрабатываем PR для любых новых плагинов с **наивысшим приоритетом**.
>
> 2. Функции каждого файла в этом проекте подробно описаны в [отчете о самостоятельном анализе проекта `self_analysis.md`](https://github.com/binary-husky/gpt_academic/wiki/GPT‐Academic项目自译解报告). С каждым новым релизом вы также можете в любое время нажать на соответствующий функциональный плагин, вызвать GPT для повторной генерации сводного отчета о самоанализе проекта. Часто задаваемые вопросы [`wiki`](https://github.com/binary-husky/gpt_academic/wiki) | [обычные методы установки](#installation) | [скрипт одношаговой установки](https://github.com/binary-husky/gpt_academic/releases) | [инструкции по настройке](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明).
>
> 3. Этот проект совместим и настоятельно рекомендуется использование китайской NLP-модели ChatGLM и других моделей больших языков производства Китая. Поддерживает одновременное использование нескольких ключей API, которые можно указать в конфигурационном файле, например, `API_KEY="openai-key1,openai-key2,azure-key3,api2d-key4"`. Если нужно временно заменить `API_KEY`, введите временный `API_KEY` в окне ввода и нажмите Enter для его подтверждения.




<div align="center">

Функции (⭐= Недавно добавленные функции) | Описание
--- | ---
⭐[Подключение новой модели](https://github.com/binary-husky/gpt_academic/wiki/%E5%A6%82%E4%BD%95%E5%88%87%E6%8D%A2%E6%A8%A1%E5%9E%8B)！ | Baidu [QianFan](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Nlks5zkzu) и WenxinYiYan, [TongYiQianWen](https://modelscope.cn/models/qwen/Qwen-7B-Chat/summary), Shanghai AI-Lab [ShuSheng](https://github.com/InternLM/InternLM), Xunfei [XingHuo](https://xinghuo.xfyun.cn/), [LLaMa2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf), ZhiPu API, DALLE3
Улучшение, перевод, объяснение кода | Одним нажатием выполнить поиск синтаксических ошибок в научных статьях, переводить, объяснять код
[Настройка горячих клавиш](https://www.bilibili.com/video/BV14s4y1E7jN) | Поддержка настройки горячих клавиш
Модульный дизайн | Поддержка настраиваемых мощных [плагинов](https://github.com/binary-husky/gpt_academic/tree/master/crazy_functions), плагины поддерживают [горячую замену](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[Профилирование кода](https://www.bilibili.com/video/BV1cj411A7VW) | [Плагин] Одним нажатием можно профилировать дерево проекта Python/C/C++/Java/Lua/... или [проанализировать самого себя](https://www.bilibili.com/video/BV1cj411A7VW)
Просмотр статей, перевод статей | [Плагин] Одним нажатием прочитать полный текст статьи в формате LaTeX/PDF и сгенерировать аннотацию
Перевод LaTeX статей, [улучшение](https://www.bilibili.com/video/BV1FT411H7c5/)| [Плагин] Одним нажатием перевести или улучшить статьи в формате LaTeX
Генерация пакетного комментария | [Плагин] Одним нажатием сгенерировать многострочный комментарий к функции
Перевод Markdown на английский и китайский | [Плагин] Вы видели документацию на сверху на пяти языках? [README](https://github.com/binary-husky/gpt_academic/blob/master/docs/README_EN.md)`
Анализ и создание отчета в формате чата | [Плагин] Автоматически генерируйте сводный отчет после выполнения
Функция перевода полноценной PDF статьи | [Плагин] Изъять название и аннотацию статьи из PDF + переводить полный текст (многопоточно)
[Arxiv помощник](https://www.bilibili.com/video/BV1LM4y1279X) | [Плагин] Просто введите URL статьи на arXiv, чтобы одним нажатием выполнить перевод аннотации + загрузить PDF
Одним кликом проверить статью на LaTeX | [Плагин] Проверка грамматики и правописания статьи LaTeX, добавление PDF в качестве справки
[Помощник Google Scholar](https://www.bilibili.com/video/BV19L411U7ia) | [Плагин] Создайте "related works" с помощью Google Scholar URL по вашему выбору.
Агрегирование интернет-информации + GPT | [Плагин] [GPT получает информацию из интернета](https://www.bilibili.com/video/BV1om4y127ck) и отвечает на вопросы, чтобы информация никогда не устаревала
⭐Точный перевод статей Arxiv ([Docker](https://github.com/binary-husky/gpt_academic/pkgs/container/gpt_academic_with_latex)) | [Плагин] [Переводите статьи Arxiv наивысшего качества](https://www.bilibili.com/video/BV1dz4y1v77A/) всего одним нажатием. Сейчас это лучший инструмент для перевода научных статей
⭐[Реальное время ввода голосом](https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md) | [Плагин] Асинхронно [слушать аудио](https://www.bilibili.com/video/BV1AV4y187Uy/), автоматически разбивать на предложения, автоматически находить момент для ответа
Отображение формул/изображений/таблиц | Поддержка отображения формул в форме [tex и рендеринга](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png), поддержка подсветки синтаксиса формул и кода
⭐Плагин AutoGen для множества интеллектуальных агентов | [Плагин] Используйте Microsoft AutoGen для исследования возможностей интеллектуального всплытия нескольких агентов!
Запуск [темной темы](https://github.com/binary-husky/gpt_academic/issues/173) | Добавьте `/?__theme=dark` в конец URL в браузере, чтобы переключиться на темную тему
[Поддержка нескольких моделей LLM](https://www.bilibili.com/video/BV1wT411p7yf) | Быть обслуживаемым GPT3.5, GPT4, [ChatGLM2 из Цинхуа](https://github.com/THUDM/ChatGLM2-6B), [MOSS из Фуданя](https://github.com/OpenLMLab/MOSS) одновременно должно быть очень приятно, не так ли?
⭐Модель ChatGLM2 Fine-tune | Поддержка загрузки модели ChatGLM2 Fine-tune, предоставляет вспомогательный плагин ChatGLM2 Fine-tune
Больше моделей LLM, поддержка [развертывания huggingface](https://huggingface.co/spaces/qingxu98/gpt-academic) | Включение интерфейса Newbing (новый Bing), введение поддержки китайских [Jittorllms](https://github.com/Jittor/JittorLLMs) для поддержки [LLaMA](https://github.com/facebookresearch/llama) и [Panguα](https://openi.org.cn/pangu/)
⭐Пакет pip [void-terminal](https://github.com/binary-husky/void-terminal) | Без GUI вызывайте все функциональные плагины этого проекта прямо из Python (разрабатывается)
⭐Плагин пустого терминала | [Плагин] Используя естественный язык, напрямую распоряжайтесь другими плагинами этого проекта
Больше новых функций (генерация изображений и т. д.) ... | Смотрите в конце этого документа ...
</div>


- Новый интерфейс (изменение опции LAYOUT в `config.py` позволяет переключиться между "расположением слева и справа" и "расположением сверху и снизу")
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/d81137c3-affd-4cd1-bb5e-b15610389762" width="700" >
</div>


- Все кнопки генерируются динамически на основе `functional.py` и могут быть свободно дополнены, освобождая буфер обмена
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Улучшение/исправление
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>



- Если вывод содержит формулы, они отображаются одновременно в виде tex и отрендеренного вида для удобства копирования и чтения
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Не хочешь смотреть код проекта? Весь проект сразу в уста ChatGPT
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Смешанное использование нескольких больших языковых моделей (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

# Установка
### Метод установки I: Прямой запуск (Windows, Linux или MacOS)

1. Скачайте проект
```sh
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git
cd gpt_academic
```

2. Настройте API_KEY

В файле `config.py` настройте API KEY и другие настройки, [нажмите здесь, чтобы узнать способы настройки в специальных сетевых средах](https://github.com/binary-husky/gpt_academic/issues/1). [Инструкции по настройке проекта](https://github.com/binary-husky/gpt_academic/wiki/Сonfig-Instructions).

「 Программа будет в первую очередь проверять наличие файла config_private.py с приватными настройками и заменять соответствующие настройки в файле config.py на те, которые указаны в файле config_private.py. Если вы понимаете эту логику, мы настоятельно рекомендуем вам создать новый файл настроек config_private.py рядом с файлом config.py и скопировать туда настройки из config.py (только те, которые вы изменяли). 」

「 Поддерживается настроить проект с помощью `переменных среды`. Пример настройки переменных среды можно найти в файле docker-compose.yml или на нашей [странице вики](https://github.com/binary-husky/gpt_academic/wiki/Сonfig-Instructions). Приоритет настроек: `переменные среды` > `config_private.py` > `config.py`. 」


3. Установите зависимости
```sh
# (Выбор I: Если знакомы с Python, python>=3.9). Примечание: используйте официальный pip-репозиторий или пакетный репозиторий Alibaba, временный способ изменить источник: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Выбор II: Используйте Anaconda). Шаги аналогичны (https://www.bilibili.com/video/BV1rc411W7Dr)：
conda create -n gptac_venv python=3.11    # Создание среды Anaconda
conda activate gptac_venv                 # Активация среды Anaconda
python -m pip install -r requirements.txt # Здесь все тоже самое, что и с установкой для pip
```


<details><summary>Если вам нужна поддержка ChatGLM2 от Цинхуа/MOSS от Фуданя/Раннера RWKV как бэкенда, нажмите, чтобы развернуть</summary>
<p>

【Опциональный шаг】Если вам нужна поддержка ChatGLM2 от Цинхуа/Сервиса MOSS от Фуданя, вам понадобится дополнительно установить дополнительные зависимости (предполагается, что вы знакомы с Python + PyTorch + у вас достаточно мощный компьютер):
```sh
# 【Опциональный шаг I】Поддержка ChatGLM2 от Цинхуа. Примечание к ChatGLM от Цинхуа: Если вы столкнулись с ошибкой "Call ChatGLM fail 不能正常加载ChatGLM的参数", обратите внимание на следующее: 1: По умолчанию установлена версия torch+cpu, для использования cuda необходимо удалить torch и установить версию torch+cuda; 2: Если вы не можете загрузить модель из-за недостаточной мощности компьютера, вы можете изменить точность модели в файле request_llm/bridge_chatglm.py, заменив AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) на AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llms/requirements_chatglm.txt

# 【Опциональный шаг II】Поддержка MOSS от Фуданя
python -m pip install -r request_llms/requirements_moss.txt
git clone --depth=1 https://github.com/OpenLMLab/MOSS.git request_llms/moss  # Обратите внимание, что когда вы запускаете эту команду, вы должны находиться в корневой папке проекта

# 【Опциональный шаг III】Поддержка RWKV Runner
Смотрите вики: https://github.com/binary-husky/gpt_academic/wiki/Поддержка-RWKV-Runner

# 【Опциональный шаг IV】Убедитесь, что config.py содержит все нужные вам модели. Пример:
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. Запустите программу
```sh
python main.py
```

### Метод установки II: Используйте Docker

0. Установка всех возможностей проекта (это большой образ с поддержкой cuda и LaTeX; но если у вас медленный интернет или маленький жесткий диск, мы не рекомендуем использовать этот метод).
[![fullcapacity](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml)

``` sh
# Измените файл docker-compose.yml, сохраните метод 0 и удалите другие методы. Затем запустите:
docker-compose up
```

1. Чат GPT + 文心一言 + Spark и другие онлайн-модели (рекомендуется для большинства пользователей)
[![basic](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml)
[![basiclatex](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml)
[![basicaudio](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml)

``` sh
# Измените файл docker-compose.yml, сохраните метод 1 и удалите другие методы. Затем запустите:
docker-compose up
```

P.S. Если вам нужен функционал, связанный с LaTeX, обратитесь к разделу Wiki. Кроме того, вы также можете использовать схему 4 или схему 0 для доступа к функционалу LaTeX.

2. Чат GPT + ChatGLM2 + MOSS + LLAMA2 + TakyiQ & Другие попытки ввести в обиход
[![chatglm](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml)

``` sh
# Измените файл docker-compose.yml, сохраните метод 2 и удалите другие методы. Затем запустите:
docker-compose up
```


### Метод установки III: Другие способы развертывания
1. **Скрипты запуска одним нажатием для Windows**.
Пользователи Windows, не знакомые с окружением Python, могут загрузить одну из версий в разделе [Релизы](https://github.com/binary-husky/gpt_academic/releases) для установки версии без локальных моделей.
Скрипты взяты из вкладки [oobabooga](https://github.com/oobabooga/one-click-installers).

2. Использование сторонних API, Azure и т. д., см. страницу [вики](https://github.com/binary-husky/gpt_academic/wiki/Сonfig-Instructions)

3. Руководство по развертыванию на удаленном сервере.
Пожалуйста, посетите [вики-страницу развертывания на облачном сервере](https://github.com/binary-husky/gpt_academic/wiki/Руководство-по-развертыванию-на-облаке).

4. Некоторые новые платформы или методы развертывания
    - Использование Sealos [для однократного развертывания](https://github.com/binary-husky/gpt_academic/issues/993)
    - Использование WSL2 (Windows Subsystem for Linux). См. [Руководство развертывания-2](https://github.com/binary-husky/gpt_academic/wiki/Using-WSL2-for-deployment)
    - Как запустить на вложенном URL-адресе (например, `http://localhost/subpath`). См. [Инструкции по работе с FastAPI](docs/WithFastapi.md)



# Расширенное использование
### I: Пользовательские удобные кнопки (академические сочетания клавиш)
Откройте файл `core_functional.py` в любом текстовом редакторе и добавьте следующие записи, затем перезапустите программу. (Если кнопка уже существует, то префикс и суффикс поддерживают горячую замену без перезапуска программы.)
Например,
```
"Супер-англо-русский перевод": {
    # Префикс, который будет добавлен перед вашим вводом. Например, используется для описания вашего запроса, например, перевода, объяснения кода, редактирования и т.д.
    "Префикс": "Пожалуйста, переведите следующий абзац на русский язык, а затем покажите каждый термин на экране с помощью таблицы Markdown:\n\n",

    # Суффикс, который будет добавлен после вашего ввода. Например, можно использовать с префиксом, чтобы заключить ваш ввод в кавычки.
    "Суффикс": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

### II: Пользовательские функциональные плагины
Создавайте мощные функциональные плагины для выполнения любых задач, которые вам нужны и которых вы и не можете себе представить.
Создание плагина для этого проекта и его отладка являются простыми задачами, и если у вас есть базовые знания Python, вы можете реализовать свой собственный функциональный плагин, используя наши предоставленные шаблоны.
Дополнительную информацию см. в [Руководстве по функциональным плагинам](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97).


# Обновления
### I: Динамические

1. Функция сохранения диалога. Вызовите "Сохранить текущий диалог" в области функциональных плагинов, чтобы сохранить текущий диалог в виде читаемого и восстанавливаемого html-файла.
Кроме того, можно использовать "Загрузить архивный файл диалога" в области функциональных плагинов (выпадающее меню), чтобы восстановить предыдущий разговор.
Подсказка: если не указывать файл и просто щелкнуть "Загрузить архивный файл диалога", можно просмотреть кэш сохраненных html-архивов.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. ⭐Перевод Latex/Arxiv статей⭐
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/002a1a75-ace0-4e6a-94e2-ec1406a746f1" height="250" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/9fdcc391-f823-464f-9322-f8719677043b" height="250" >
</div>

3. Void Terminal (понимание пользовательских намерений из естественного языка и автоматическое вызов других плагинов)

- Шаг 1: Введите "Пожалуйста, вызовите плагин для перевода PDF-статьи, адрес которой https://openreview.net/pdf?id=rJl0r3R9KX".
- Шаг 2: Нажмите "Void Terminal".

<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/66f1b044-e9ff-4eed-9126-5d4f3668f1ed" width="500" >
</div>

4. Модульный дизайн функционала, позволяющий реализовать мощные функции с помощью простых интерфейсов
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

5. Перевод и анализ других открытых проектов
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" height="250" >
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" height="250" >
</div>

6. Функциональность для украшения[meme](https://github.com/fghrsh/live2d_demo) (по умолчанию отключена, требуется изменение файла `config.py`)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. Генерация изображений с помощью OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

8. Анализ и обобщение аудио с помощью OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

9. Проверка и исправление ошибок во всем тексте LaTeX
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" height="200" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/476f66d9-7716-4537-b5c1-735372c25adb" height="200">
</div>

10. Изменение языка и темы
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/b6799499-b6fb-4f0c-9c8e-1b441872f4e8" width="500" >
</div>



### II: Версии:
- Версия 3.70 (в планах): Оптимизация темы AutoGen и разработка ряда дополнительных плагинов
- Версия 3.60: Внедрение AutoGen в качестве фундамента нового поколения плагинов
- Версия 3.57: Поддержка GLM3, Starfire v3, Wenxin One Word v4, исправление ошибок при совместном использовании локальной модели
- Версия 3.56: Поддержка добавления дополнительных функциональных кнопок в реальном времени, новая страница отчетов в формате PDF
- Версия 3.55: Переработка пользовательского интерфейса, внедрение плавающего окна и панели меню
- Версия 3.54: Добавлен интерпретатор кода (Code Interpreter) (в разработке)
- Версия 3.53: Динамический выбор различных тем интерфейса, повышение стабильности и решение проблемы конфликтов между несколькими пользователями
- Версия 3.50: Использование естественного языка для вызова всех функциональных плагинов проекта (Void Terminal), поддержка категоризации плагинов, улучшение пользовательского интерфейса, разработка новых тем
- Версия 3.49: Поддержка платформы Baidu Qianfan и Wenxin One Word
- Версия 3.48: Поддержка Ali Dharma Institute, Shanghai AI-Lab Scholar, Xunfei Starfire
- Версия 3.46: Поддержка реального голосового диалога с полной автоматизацией
- Версия 3.45: Поддержка настраиваемой модели ChatGLM2
- Версия 3.44: Официальная поддержка Azure, улучшение удобства пользовательского интерфейса
- Версия 3.4: +Перевод полных текстов PDF, +корректировка латексных документов
- Версия 3.3: +Интернет-информационные функции
- Версия 3.2: Поддержка дополнительных параметров в функциональных плагинах (функция сохранения диалога, интерпретация кода на любом языке + одновременный вопрос о любом комбинированном LLM)
- Версия 3.1: Поддержка одновременного обращения к нескольким моделям gpt! Поддержка API2D, поддержка равномерной нагрузки нескольких api-ключей
- Версия 3.0: Поддержка chatglm и других небольших моделей llm
- Версия 2.6: Переработка структуры плагинов для повышения интерактивности, добавление дополнительных плагинов
- Версия 2.5: Автоматическое обновление, решение проблемы с длиной текста и переполнением токенов при обработке текста
- Версия 2.4: (1) Добавление функции полного перевода PDF; (2) Добавление функции изменения позиции объекта ввода; (3) Добавление функции вертикального размещения; (4) Оптимизация многопоточных функциональных плагинов.
- Версия 2.3: Улучшение интерактивности многопоточности
- Версия 2.2: Поддержка живой перезагрузки функциональных плагинов
- Версия 2.1: Складываемый макет
- Версия 2.0: Введение модульных функциональных плагинов
- Версия 1.0: Базовые функции

GPT Academic Группа QQ разработчиков: `610599535`

- Известные проблемы
    - Некоторые расширения для браузера могут мешать работе пользовательского интерфейса этого программного обеспечения
    - У официального Gradio есть много проблем совместимости, поэтому обязательно установите Gradio с помощью `requirement.txt`

### III: Темы
Вы можете изменить тему путем изменения опции `THEME` (config.py)
1. `Chuanhu-Small-and-Beautiful` [ссылка](https://github.com/GaiZhenbiao/ChuanhuChatGPT/)


### IV: Ветви разработки этого проекта

1. Ветка `master`: Основная ветка, стабильная версия
2. Ветвь `frontier`: Ветвь разработки, версия для тестирования


### V: Справочники и обучение

```
В коде использовались многие функции, представленные в других отличных проектах, поэтому их порядок не имеет значения:

# ChatGLM2-6B от Тиньхуа:
https://github.com/THUDM/ChatGLM2-6B

# Линейные модели с ограниченной памятью от Тиньхуа:
https://github.com/Jittor/JittorLLMs

# ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Edge-GPT:
https://github.com/acheong08/EdgeGPT

# ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT



# Установщик с одним щелчком Oobabooga:
https://github.com/oobabooga/one-click-installers

# Больше:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
