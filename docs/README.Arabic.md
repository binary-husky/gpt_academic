


> **ملحوظة**
>
> تمت ترجمة هذا الملف README باستخدام GPT (بواسطة المكون الإضافي لهذا المشروع) وقد لا تكون الترجمة 100٪ موثوقة، يُرجى التمييز بعناية بنتائج الترجمة.
>
> 2023.11.7: عند تثبيت التبعيات، يُرجى اختيار الإصدار المُحدد في `requirements.txt`. الأمر للتثبيت: `pip install -r requirements.txt`.

# <div align=center><img src="logo.png" width="40"> GPT الأكاديمي</div>

**إذا كنت تحب هذا المشروع، فيُرجى إعطاؤه Star. لترجمة هذا المشروع إلى لغة عشوائية باستخدام GPT، قم بقراءة وتشغيل [`multi_language.py`](multi_language.py) (تجريبي).

> **ملحوظة**
>
> 1. يُرجى ملاحظة أنها الإضافات (الأزرار) المميزة فقط التي تدعم قراءة الملفات، وبعض الإضافات توجد في قائمة منسدلة في منطقة الإضافات. بالإضافة إلى ذلك، نرحب بأي Pull Request جديد بأعلى أولوية لأي إضافة جديدة.
>
> 2. تُوضّح كل من الملفات في هذا المشروع وظيفتها بالتفصيل في [تقرير الفهم الذاتي `self_analysis.md`](https://github.com/binary-husky/gpt_academic/wiki/GPT‐Academic项目自译解报告). يمكنك في أي وقت أن تنقر على إضافة وظيفة ذات صلة لاستدعاء GPT وإعادة إنشاء تقرير الفهم الذاتي للمشروع. للأسئلة الشائعة [`الويكي`](https://github.com/binary-husky/gpt_academic/wiki). [طرق التثبيت العادية](#installation) |  [نصب بنقرة واحدة](https://github.com/binary-husky/gpt_academic/releases) | [تعليمات التكوين](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明).
>
> 3. يتم توافق هذا المشروع مع ودعم توصيات اللغة البيجائية الأكبر شمولًا وشجاعة لمثل ChatGLM. يمكنك توفير العديد من مفاتيح Api المشتركة في تكوين الملف، مثل `API_KEY="openai-key1,openai-key2,azure-key3,api2d-key4"`. عند تبديل مؤقت لـ `API_KEY`، قم بإدخال `API_KEY` المؤقت في منطقة الإدخال ثم اضغط على زر "إدخال" لجعله ساري المفعول.



<div align="center">

الوظائف (⭐= وظائف مُضافة حديثًا) | الوصف
--- | ---
⭐[التوصل لنموذج جديد](https://github.com/binary-husky/gpt_academic/wiki/%E5%A6%82%E4%BD%95%E5%88%87%E6%8D%A2%E6%A8%A1%E5%9E%8B)! | بحث بيدو[تشيان فان](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Nlks5zkzu) ووينسين[جينرال](https://modelscope.cn/models/qwen/Qwen-7B-Chat/summary)، مختبرات شنغهاي للذكاء الصناعي[شو شينغ](https://github.com/InternLM/InternLM)، إكسنفلام[زينغهو]https://xinghuo.xfyun.cn/)، [LLaMa2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf)، واجهة بيانية ذكية و3 خدمات إضافية [DALLE3]
الجودة الفائقة، الترجمة، شرح الكود | الإصلاح الفوري للاخطاء النحوية في الأبحاث وترجمة وتحسين التصريف اللغوي للأكواد
[اختصارات مخصصة](https://www.bilibili.com/video/BV14s4y1E7jN) | دعم الاختصارات المخصصة
تصميم قابل للتوسيع | دعم الإضافات القوية المخصصة (الوظائف)، الإضافات قابلة للتحديث بشكل فوري
[تحليل البرنامج](https://www.bilibili.com/video/BV1cj411A7VW) | [وظائف] التحليل الشجري بناءً على البرنامج من Python/C/C++/Java/Lua/..., أو [التحليل الذاتي](https://www.bilibili.com/video/BV1cj411A7VW)
قراءة وترجمة الأبحاث | [وظائف] فك تشفير كامل لأوراق البحث بتنسيق LaTeX/PDF وإنشاء مستخلص
ترجمة وتحسين أوراق اللاتكس | [وظائف] ترجمة أو تحسين الأوراق المكتوبة بلاتكس
إنشاء تعليقات الدوال دفعة واحدة | [وظائف] إنشاء تعليقات الدوال بدفعة واحدة
ترجمة Markdown بين اللغتين العربية والإنجليزية | [وظائف] هل رأيت الـ 5 لغات المستخدمة في منشور [README](https://github.com/binary-husky/gpt_academic/blob/master/docs/README_EN.md) ؟
إنشاء تقرير تحليل الدردشة | [وظائف] إنشاء تقرير ملخص بعد تشغيله
ترجمة كاملة لأوراق PDF | [وظائف] تحليل الأوراق بتنسيق PDF لتحديد العنوان وملخصها وترجمتها (متعدد الخيوط)
مساعدة Arxiv | [وظائف] قم بإدخال رابط مقال Arxiv لترجمة الملخص وتحميل ملف PDF
تصحيح لاتكس بضغطة زر واحدة | [وظائف] إكمال تصحيح لاتكس بناءً على التركيبة النحوية، إخراج همز المقابل للمقارنة PDF
مساعد بحث Google بنسخة محلية | [وظائف] قم بتقديم رابط لصفحة بحث Google Scholar العشوائي حتى يساعدك GPT في كتابة [الأبحاث المتعلقة](https://www.bilibili.com/video/BV1GP411U7Az/)
تجميع معلومات الويب + GPT | [وظائف] جمع المعلومات من الويب بشكل سهل للرد على الأسئلة لجعل المعلومات محدثة باستمرار
⭐ترجمة دقيقة لأوراق Arxiv ([Docker](https://github.com/binary-husky/gpt_academic/pkgs/container/gpt_academic_with_latex)) | [وظائف] ترجمة مقالات Arxiv عالية الجودة بنقرة واحدة، أفضل أداة حاليا للترجمة
⭐[إدخال الصوت الفوري](https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md) | [وظائف] (غير متزامن) استماع الصوت وقطعه تلقائيًا وتحديد وقت الإجابة تلقائيًا
عرض الصيغ/الصور/الجداول | يمكن عرض الصيغ بشكل [TEX](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png) وأيضًا بتنسيق رسومي، يدعم عرض الصيغ وإبراز الكود
⭐إضغط على وكيل "شارلوت الذكي" | [وظائف] استكمال الذكاء للكأس الأول للذكاء المكتسب من مايكروسوفت، اكتشاف وتطوير عالمي العميل
تبديل الواجهة المُظلمة | يمكنك التبديل إلى الواجهة المظلمة بإضافة ```/?__theme=dark``` إلى نهاية عنوان URL في المتصفح
دعم المزيد من نماذج LLM | دعم لجميع GPT3.5 وGPT4 و[ChatGLM2 في جامعة ثوه في لين](https://github.com/THUDM/ChatGLM2-6B) و[MOSS في جامعة فودان](https://github.com/OpenLMLab/MOSS)
⭐تحوي انطباعة "ChatGLM2" | يدعم استيراد "ChatGLM2" ويوفر إضافة المساعدة في تعديله
دعم المزيد من نماذج "LLM"، دعم [نشر الحديس](https://huggingface.co/spaces/qingxu98/gpt-academic) | انضم إلى واجهة "Newbing" (Bing الجديدة)،نقدم نماذج Jittorllms الجديدة تؤيدهم [LLaMA](https://github.com/facebookresearch/llama) و   [盘古α](https://openi.org.cn/pangu/)
⭐حزمة "void-terminal" للشبكة (pip) | قم بطلب كافة وظائف إضافة هذا المشروع في python بدون واجهة رسومية (قيد التطوير)
⭐PCI-Express لإعلام (PCI) | [وظائف] باللغة الطبيعية، قم بتنفيذ المِهام الأخرى في المشروع
المزيد من العروض (إنشاء الصور وغيرها)……| شاهد أكثر في نهاية هذا المستند ...
</div>


- شكل جديد (عن طريق تعديل الخيار LAYOUT في `config.py` لقانون التوزيع "اليمين أو اليسار" أو "الأعلى أو الأسفل")
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/d81137c3-affd-4cd1-bb5e-b15610389762" width="700" >
</div>


- جميع الأزرار يتم إنشاؤها ديناميكيًا من خلال قراءة functional.py ويمكن إضافة وظائف مخصصة بحرية وتحرير الحافظة
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- التجميل / التحوير
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>



- إذا تضمّن الإخراج معادلات، فسيتم عرضها بشكلٍ يمكّن من النسخ والقراءة على النحوين: TEX ورسومية.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- هل تشعر بالكسل من قراءة كود المشروع؟ قم بمدها مباشرةً إلى ChatGPT
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- دمج نماذج اللغات الكبيرة المختلفة (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

# Installation
### طريقة التثبيت الأولى: التشغيل المباشر (Windows، Linux أو MacOS)

1. قم بتنزيل المشروع
```sh
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git
cd gpt_academic
```

2. قم بتكوين لغة البرمجة Python

في ملف `config.py`، قم بتكوين مفتاح الواجهة API والإعدادات الأخرى، [انقر هنا للاطلاع على طريقة تكوين الإعدادات في بيئة شبكة خاصة](https://github.com/binary-husky/gpt_academic/issues/1). [انقر هنا لزيارة صفحة الويكي](https://github.com/binary-husky/gpt_academic/wiki/توضيحات-تكوين-المشروع).

" ستقوم البرنامج بفحص وجود ملف تكوين خاص يسمى `config_private.py` بأولوية، وسيستخدم التكوينات الموجودة فيه لتجاوز التكوينات ذات الأسماء المطابقة في `config.py`. إذا كنت تفهم هذه الطريقة ونظام القراءة، فإننا نوصي بشدة بإنشاء ملف تكوين جديد يسمى `config_private.py` بجوار `config.py` ونقل (نسخ) التكوينات الموجودة في `config.py` إلى `config_private.py` (يجب نسخ العناصر التي قمت بتعديلها فقط). "

" يدعم المشروع التكوين من خلال `المتغيرات المحيطية`، ويمكن تحديد تنسيق كتابة المتغيرات المحيطية من خلال ملف `docker-compose.yml` أو صفحة الويكي الخاصة بنا. تعتمد أولوية القراءة على التكوينات على التالي: `المتغيرات المحيطية` > `config_private.py` > `config.py`. "

3. قم بتثبيت التبعيات
```sh
# (الخيار الأول: إذا كنت تعرف Python، python>=3.9) الملحوظة: استخدم مستودع pip الرسمي أو مستودع pip آلي بباي، يمكن تغيير المستودع المؤقت بواسطة الأمر: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (الخيار الثاني: باستخدام Anaconda) الخطوات مشابهة (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # إنشاء بيئة Anaconda
conda activate gptac_venv                 # تنشيط بيئة Anaconda
python -m pip install -r requirements.txt # هذه الخطوة مطابقة لخطوة تثبيت pip
```


<details><summary>إذا كنت بحاجة إلى دعم ChatGLM2 من الجامعة الصينية للاقتصاد وإدارة الأعمال وموس من جامعة فودان كخادم وجودة عالية لطرح الأسئلة، انقر هنا للعرض</summary>
<p>

【خطوات اختيارية】إذا كنت بحاجة إلى دعم جودة عالية لتشات جامعة تسينهوا (ChatGLM2) الصينية وجامعة فودان (MOSS)، يتعين عليك تثبيت تبعيات إضافية (شرط مسبق: التعامل مع Python واستخدام Pytorch وتوفر الحاسوب الشخصي بمواصفات قوية):
```sh
# 【خطوات اختيارية 1】دعم جودة عالية لتشات جامعة تسينهوا (ChatGLM2)
python -m pip install -r request_llms/requirements_chatglm.txt

# 【خطوات اختيارية 2】دعم جودة عالية لتشات جامعة فودان (MOSS)
python -m pip install -r request_llms/requirements_moss.txt
git clone --depth=1 https://github.com/OpenLMLab/MOSS.git request_llms/moss  # عند تنفيذ هذا الأمر، يجب أن تكون في مسار المشروع الرئيسي

# 【خطوات اختيارية 3】دعم RWKV Runner
راجع الويكي: https://github.com/binary-husky/gpt_academic/wiki/دليل-تكوين-RWKV

# 【خطوات اختيارية 4】تأكد من أن ملف التكوين config.py يحتوي على النماذج المرجوة، وهناك النماذج المدعومة حاليًا التالية (توجد خطط لتشغيل "jittorllms" في docker فقط):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>


4. تشغيل البرنامج
```sh
python main.py
```

### طريقة التثبيت الثانية: استخدام Docker

0. نصب القدرات الكاملة للمشروع (هذا هو الصورة الكبيرة التي تحتوي على CUDA و LaTeX. ولكن إذا كانت سرعة الإنترنت بطيئة أو القرص الصلب صغير، فإننا لا نوصي باستخدام هذا الخيار)
[![fullcapacity](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml)

``` sh
# قم بتعديل ملف docker-compose.yml للحفاظ على الخطة رقم 0 وحذف الخطط الأخرى. ثم أشغل:
docker-compose up
```

1. تشغيل نموذج ChatGPT فقط + 文心一言 (Wenxin YIYan) + Spark عبر الإنترنت (يُوصى بهذا الخيار للمعظم)

[![basic](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml)
[![basiclatex](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml)
[![basicaudio](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml)

``` sh
# قم بتعديل ملف docker-compose.yml للحفاظ على الخطة رقم 1 وحذف الخطط الأخرى. ثم أشغل:
docker-compose up
```

P.S. للاستفادة من إمكانية اللافتكس الإضافية، يرجى الرجوع إلى الويكي. بالإضافة إلى ذلك، يمكنك استخدام الخطة 4 أو الخطة 0 مباشرة للحصول على إمكانية اللافتكس.

2. تشغيل نموذج ChatGPT + نموذج ChatGLM2 + نموذج MOSS + نموذج LLAMA2 + تون يي تشين ون (QiChaYiWen) (يتطلب معرفة بتشغيل نيفيديا دوكر (Nvidia Docker))

[![chatglm](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml)

``` sh
# قم بتعديل ملف docker-compose.yml للحفاظ على الخطة رقم 2 وحذف الخطط الأخرى. ثم أشغل:
docker-compose up
```

### طريقة التثبيت الثالثة: طرائق نشر أخرى
1. **نصوص بنقرة واحدة لأنظمة Windows**.
يمكن لمستخدمي Windows الذين لا يعرفون بيئة Python تنزيل سكربت التشغيل بنقرة واحدة من [الإصدارات](https://github.com/binary-husky/gpt_academic/releases) المنشورة لتثبيت الإصدار الذي لا يحتوي على نماذج محلية.
المساهمة في السكربت تعود لـ[oobabooga](https://github.com/oobabooga/one-click-installers).

2. استخدام واجهة برمجة تطبيقات (API) مطراف ثالثة، Microsoft Azure، ونشوة النص، وغيرها، يرجى الرجوع إلى [صفحة الويكي](https://github.com/binary-husky/gpt_academic/wiki/إعدادات-التكوين-للمشروع) الخاصة بنا

3. دليل تجنب المشاكل عند نشر المشروع في خوادم السحابة.
يرجى زيارة صفحة [دليل نشر خوادم السحابة في المحيط](https://github.com/binary-husky/gpt_academic/wiki/دليل-نشر-خوادم-السحابة)

4. طرائق نشر المشروع بأحدث الأساليب
    - استخدام Sealos للنشر السريع [بنقرة واحدة](https://github.com/binary-husky/gpt_academic/issues/993).
    - استخدم WSL2 (Windows Subsystem for Linux). يُرجى زيارة صفحة الويكي [لدليل التثبيت-2](https://github.com/binary-husky/gpt_academic/wiki/دليل-تشغيل-WSL2-(Windows-Subsystem-for-Linux)
    - كيفية تشغيل البرنامج تحت عنوان فرعي (على سبيل المثال: `http://localhost/subpath`). يُرجى زيارة [إرشادات FastAPI](docs/WithFastapi.md)



# الاستخدام المتقدم
### I: إنشاء أزرار مخصصة (اختصارات أكاديمية)
افتح أي محرر نصوص وافتح `core_functional.py` وأضف الإدخالات التالية ثم أعد تشغيل البرنامج. (إذا كانت الأزرار موجودة بالفعل، بإمكانك تعديل البادئة واللاحقة حراريًا دون الحاجة لإعادة تشغيل البرنامج)
على سبيل المثال:
```
"ترجمة سوبر الإنجليزية إلى العربية": {
    # البادئة، ستتم إضافتها قبل إدخالاتك. مثلاً، لوصف ما تريده مثل ترجمة أو شرح كود أو تلوين وهلم جرا
    "بادئة": "يرجى ترجمة النص التالي إلى العربية ثم استخدم جدول Markdown لشرح المصطلحات المختصة المذكورة في النص:\n\n",

    # اللاحقة، سيتم إضافتها بعد إدخالاتك. يمكن استخدامها لوضع علامات اقتباس حول إدخالك.
    "لاحقة": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

### II: إنشاء مكونات وظيفية مخصصة
قم بكتابة مكونات وظيفية قوية لتنفيذ أي مهمة ترغب في الحصول عليها وحتى تلك التي لم تخطر لك على بال.
إن إنشاء وتصحيح المكونات في هذا المشروع سهل للغاية، فما عليك سوى أن تمتلك بعض المعرفة الأساسية في لغة البرمجة بايثون وتستند على القالب الذي نقدمه.
للمزيد من التفاصيل، يُرجى الاطلاع على [دليل المكونات الوظيفية](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97).


# التحديثات
### I: تحديثات

1. ميزة حفظ الدردشة: يمكن حفظ الدردشة الحالية كملف HTML قابل للقراءة والاسترداد ببساطة عند استدعاء الوظيفة في منطقة المكونات `حفظ الدردشة الحالية` ، ويمكن استرجاع المحادثة السابقة ببساطة عند استدعاء الوظيفة في منطقة المكونات (القائمة المنسدلة) `تحميل سجل الدردشة` .
نصيحة: يمكنك النقر المباشر على `تحميل سجل الدردشة` بدون تحديد ملف لعرض ذاكرة التخزين المؤقت لسجلات HTML.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. ميزة ترجمة المقالات العلمية بواسطة Latex/Arxiv
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/002a1a75-ace0-4e6a-94e2-ec1406a746f1" height="250" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/9fdcc391-f823-464f-9322-f8719677043b" height="250" >
</div>

3. محطة فراغ (فهم نغمة المستخدم من داخل اللغة الطبيعية واستدعاء وظائف أخرى تلقائيًا)

- الخطوة 1: اكتب "بالرجاء استدعاء وظيفة ترجمة المقالة الأكاديمية من PDF وعنوان المقال هو https://openreview.net/pdf?id=rJl0r3R9KX".
- الخطوة 2: انقر فوق "محطة الفراغ".

<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/66f1b044-e9ff-4eed-9126-5d4f3668f1ed" width="500" >
</div>

4. تصميم الوظائف المتعددة القادرة على توفير وظائف قوية بواجهات بسيطة
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

5. ترجمة وإلغاء ترجمة المشاريع الأخرى مفتوحة المصدر
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" height="250" >
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" height="250" >
</div>

6. ميزة تزيين [live2d](https://github.com/fghrsh/live2d_demo) (مغلقة بشكل افتراضي، يتطلب تعديل `config.py`)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. إنتاج الصور من OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

8. تحليل وإجماع الصوت من OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

9. إصلاح أخطاء اللغة الطبيعة في Latex
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" height="200" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/476f66d9-7716-4537-b5c1-735372c25adb" height="200">
</div>

10. تغيير اللغة والموضوع
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/b6799499-b6fb-4f0c-9c8e-1b441872f4e8" width="500" >
</div>



### II: الإصدارات:
- الإصدار 3.70 (قريبًا): تحسينات لوظائف AutoGen وتصميم سلسلة من المكونات المشتقة
- الإصدار 3.60: إدخال AutoGen كأساس لوظائف الجيل الجديد
- الإصدار 3.57: دعم GLM3، نار النجوم v3، وشجرة الكلمات v4، وإصلاح خطأ الازدحام في النماذج المحلية
- الإصدار 3.56: الدعم لإضافة مزامنة الأزرار الأساسية حسب الطلب، وصفحة تجميع تقارير البيانات في ملف PDF
- الإصدار 3.55: إعادة هيكلة واجهة المستخدم الأمامية، وإضافة نافذة عائمة وشريط قائمة
- الإصدار 3.54: إضافة مترجم الكود المباشر (Code Interpreter) (قيد الانجاز)
- الإصدار 3.53: دعم اختيار موضوعات واجهة مختلفة، وزيادة الاستقرار وحل مشاكل التعارض بين المستخدمين المتعدد
- الإصدار 3.50: استخدام اللغة الطبيعية لاستدعاء جميع وظائف المشروع هذا (محطة فراغ)، ودعم تصنيف الوظائف وتحسين واجهة المستخدم وتصميم مواضيع جديدة
- الإصدار 3.49: دعم المنصات البحثية في بيدو كونفان وشجرة الكلمات
- الإصدار 3.48: دعم علي بابا, بوكما رش حتكيا, إكسونامبلومانت النار
- الإصدار 3.46: دعم محادثة نصية في الوقت الحقيقي غير مراقبة
- الإصدار 3.45: دعم تخصيص LatexChatglm النموذج التعديل
- الإصدار 3.44: دعم Azure رسميًا، وتحسين سهولة الاستخدام للواجهات الأمامية
- الإصدار 3.4: +ترجمة النصوص الكاملة للمقالات من خلال ملف PDF، +اختيار موضع المنطقة النصية، +خيار التخطيط الرأسي، +تحسينات في وظائف التداخل العديدة
- الإصدار 3.3: +وظائف متكاملة للمعلومات عبر الإنترنت
- الإصدار 3.2: دعم وظائف المكونات التي تحتوي معلمات أكثر (حفظ النص، فهم أي لغة برمجة، طلب أي تركيبة LLM في وقت واحد)
- الإصدار 3.1: دعم السؤال نحو نماذج GPT المتعددة! دعم واجهة api2d، دعم توازن الأحمال بين المفاتيح الخاصة المتعددة
- الإصدار 3.0: دعم لنماذج جات، واحدة منها لشتلس الصغيرة
- الإصدار 2.6: إعادة تصميم بنية الوظائف، وتحسين التفاعل وإضافة مزيد من الوظائف
- الإصدار 2.5: التحديث التلقائي، وحل مشكلة النص الطويل عند ملخص المشاريع الضخمة وتجاوز النصوص.
- الإصدار 2.4: (١) إضافة ميزة ترجمة المقالات الدورية. (٢) إضافة ميزة لتحويل مكان منطقة الإدخال. (٣) إضافة خيار التخطيط العمودي (vertical layout). (٤) تحسين وظائف المكونات متعددة الخيوط.
- الإصدار 2.3: تحسين التفاعل مع مواضيع متعددة
- الإصدار 2.2: دعم إعادة تحميل الوظائف المكونة حراريًا
- الإصدار 2.1: تصميم قابل للطي
- الإصدار 2.0: إدخال وحدات الوظائف المكونة
- الإصدار 1.0: الوظائف الأساسية

مجموعة المطورين GPT Academic QQ: `610599535`

- مشكلات معروفة
    - بعض ملحقات متصفح الترجمة تتداخل مع تشغيل الواجهة الأمامية لهذا البرنامج
    - يحتوي Gradio الرسمي حاليًا على عدد كبير من مشاكل التوافق. يُرجى استخدام `requirement.txt` لتثبيت Gradio.

### III: الأنساق
يمكن تغيير الأنساق بتعديل خيار `THEME` (config.py)
1. `Chuanhu-Small-and-Beautiful` [الرابط](https://github.com/GaiZhenbiao/ChuanhuChatGPT/)


### IV: فروع تطوير هذا المشروع

1. الفرع `master`: الفرع الرئيسي، إصدار مستقر
2. الفرع `frontier`: الفرع التطويري، إصدار تجريبي


### V: المراجع والفروض التعليمية

```
استخدمت العديد من التصاميم الموجودة في مشاريع ممتازة أخرى في الأكواد التالية، للمراجع عشوائية:

# ViewGradio:
https://github.com/THUD



# مُثبّت بضغطة واحدة Oobabooga:
https://github.com/oobabooga/one-click-installers

# المزيد:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
