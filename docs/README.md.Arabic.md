> **ملاحظة**
>
> عند تثبيت الاعتماديات، يُرجى اختيار الإصدارات التي تم تحديدها بشكل صارم في requirements.txt.
> 
> `pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`

# <img src="logo.png" width="40" > تحسين أداء GPT الأكاديمي 

**إذا كنت تحب هذا المشروع، يُرجى إعطاؤه نجمة. إذا كنت قد ابتكرت اختصارات أكاديمية أو إضافات وظيفية أكثر فائدة، يُرجى فتح مشكلة (issue) أو طلب إدراج (pull request). نحن أيضًا نملك README باللغات [الإنجليزية](README_EN.md)، [اليابانية](README_JP.md)، [الكورية](https://github.com/mldljyh/ko_gpt_academic)، [الروسية](README_RS.md) و [الفرنسية](README_FR.md) التي تم ترجمتها بواسطة هذا المشروع نفسه. لترجمة هذا المشروع إلى أي لغة باستخدام GPT، يرجى قراءة [`multi_language.py`](multi_language.py) (تجريبي).

> **ملاحظة**
>
> 1. يُرجى ملاحظة أنه يمكن للإضافات (الأزرار) المحددة باللون الأحمر فقط دعم قراءة الملفات، وبعض الإضافات موجودة في قائمة منسدلة في منطقة الإضافات. بالإضافة إلى ذلك، فإننا نرحب بأي طلبات سحب (pull requests) لإضافة أية إضافات جديدة بذات الأهمية القصوى!
>
> 2. تفصيلات وظيفة كل ملف في هذا المشروع توضح بشكلٍ كاملٍ في التقرير التفسيري الخاص بنفس البرنامج الذي تُمكَّن من تجديده من خلال النقر على إضافات وظيفية ذات الصلة. تتضمن ملخص للأسئلة الشائعة في ال[`wiki`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98). [طرق التثبيت](#installation).
> 
> 3. يدعم هذا المشروع إمكانية التجربة والاستخدام السابق للغة الصينية الكبيرة chatglm و RWKV وفضائيات التكوين وغيرها. يمكن دمج مفاتيح API متعددة في ملف التكوين بإدخال `API_KEY="openai-key1,openai-key2,api2d-key3"`. إذا كنت بحاجة لتغير API_KEY مؤقتًا، يمكنك إدخال API_KEY المؤقت في منطقة الإدخال والضغط على زر الإرسال.الوظيفة | الوصف
--- | ---
تحسين بنقرة واحدة | دعم تحسين بنقرة واحدة، بحث بنقرة واحدة عن أخطاء اللغة في الأوراق البحثية
تحويل اللغة بنقرة واحدة بين الصينية والإنجليزية | تحويل اللغة بنقرة واحدة بين الصينية والإنجليزية
شرح البرنامج بكود بنقرة واحدة | عرض الكود و شرحه و توليد الكود و أضافة تعليقات إلى الكود
إختصارات الأزرار المخصصة | دعم إختصارات الأزرار المخصصة
تصميم نموذجي مرن | دعم المكونات الوظيفية المخصصة الفعالة ، دعم تحديث البرنامج الوظيفي
تحليل البرنامج الذاتي | [مكون فعال] [فهم بنقرة واحدة](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A) لكود المصدر لهذا المشروع
تحليل البرنامج | [مكون فعال] يمكن تحليل شجرة مشاريع Python / C / C++ / Java / Lua /...
قراءة، ترجمة الأوراق البحثية | [مكون فعال] يمكن فهم أوراق اللاتكس/ PDF و توليد مختصر
ترجمة او تحسين مخطوطات لاتكس | [مكون فعال] ترجمة الخطوط إلى اللغة الإنجليزية أو تحسينها
توليد تعليقات بكميات كبيرة | [مكون فعال] توليد تعليقات الدوال بنقرة واحدة
ترجمة إلى العربية والصينية على Markdown | [مكون فعال] هل رأيت README بخمس لغات في الأعلى؟
تحليل التحليل التقريري للدردشات | [مكون فعال] إنشاء تقرير ملخص
ترجمة النص الكامل لأوراق البحثية PDF | [مكون فعال] استخراج العنوان وملخص الأوراق البحثية الحديثة وترجمة نص الورقة الكامل (متعدد الخطوط)
مساعد Arxiv | [مكون فعال] إدخال URL لمقال على arxiv يمكنك الترجمة وتنزيل ملخص الورقة البحثية بنقرة واحدة
مساعد للبحث الأكاديمي في جوجل | [مكون فعال] إعطاء أي رابط من صفحة بحث علمية لـ google scholar، اسمح لـ GPT بمساعدتك في كتابة relatedworks
دمج معلومات الإنترنت وGPT | [مكون فعال] دعم جلب المعلومات من الإنترنت بواسطة GPT قبل الإجابة على الأسئلة وجعل المعلومات لا تموت أبدًا
عرض الرموز الرياضية / الصور / الجداول | يمكن عرض رموز اللغات المبرمجة والنماذج المرئية للمعلومات، يدعم أيضًا رموز لغات البرمجة وتضليل الأكواد
دعم مكونات وظيفية متعددة الخطوط | دعم استدعاء متعدد الخطوط لـChatgpt ، وتحليل كمية كبيرة من النصوص أو البرامج عند الضغط على زر واحد
تشغيل موضوع gradio الليلي | يمكن تغيير مظهر gradio الإضافية داكن المظهر عن طريق إضافة `/?__theme=dark` في نهاية عنوان الرابط في المتصفح
دعم المزيد من نماذج LLM | يتم خدمتها بنفس الوقت من قبل GPT3.5 و GPT4 و宝贵的ChatGLM من جامعة تسينغهوا و MOSS. بالتأكيد سوف يشعر بالرضا ، أليس كذلك؟
دعم المزيد من الوظائف | دعم واجهات Line Bing الجديدة ، ودعم البرنامج الوظيفي لجامعة تسينغهوا ، و LLAMS القائم على Jittor الذي يساعد على الدراسات الزمنية للسوائل ، و RWKV و Pangu؟
إظهار مزيد من الوظائف الجديدة (إنشاء الصور إلخ) ... | يرجى الرجوع إلى نهاية هذا الوثيقة ...أنت مترجم أكاديمي محترف.

- يتم إنشاء جميع الأزرار ديناميكيًا من خلال قراءة functional.py ، ويمكن إضافة وظائف مخصصة حسب الرغبة ، مما يحرر حافظة النسخ
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- تلميع / تصحيح
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- إذا كان الإخراج يحتوي على معادلات ، فسيتم عرضها في نفس الوقت على شكل Tex و Rendering ، وذلك لتسهيل النسخ والقراءة.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- لا يرغب في رؤية كود المشروع؟ يمكنك تقديم المشروع بأكمله بمجرد تحديث chatgpt 
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- مزيج من العديد من لغات النموذج اللغوي (ChatGLM + OpenAI-GPT3.5 + [API2D] (https://api2d.com/)-GPT4) 
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

---
# التثبيت
## التركيب - الطريقة 1: تشغيل مباشر (نظام تشغيل Windows و Linux أو MacOS)

1. تحميل المشروع
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. تكوين API_KEY

في `config.py` ، قم بتكوين مفتاح API وإعدادات أخرى ، [عمليات تكوين الشبكة الخاصة] (https://github.com/binary-husky/gpt_academic/issues/1).

(ملاحظة: عند تشغيل البرنامج ، سيتم فحص وجود ملف تكوين خاص يسمى `config_private.py` أولاً ، وسيتم استخدام التكوين الموجود في الملف لتغطية التكوين في `config.py`. لذلك ، إذا كنت تفهم منطق قراءة التكوين لدينا ، فإننا نوصي بشدة بإنشاء ملف تكوين جديد يسمى `config_private.py` بجوار `config.py` وتحويل (نسخ) التكوين من `config.py` إلى `config_private.py`. `config_private.py` لا يخضع للتحكم بواسطة git ، مما يجعل معلومات خصوصيتك أكثر أمانًا. ملاحظة تمكين هذا المشروع الدعم أيضًا لإعداد معظم الخيارات باستخدام "متغيرات البيئة" ، على التنسيق الذي يتم استخدامه في ملف `docker-compose`. ترتيب القراءة: "متغيرات البيئة" > "config_private.py" > "config.py")

3. تثبيت الأدوات اللازمة
```sh
# (الخيار I: إذا كنت تعرف python بشكل جيد). (إصدار البايثون 3.9 أعلى ، كلما كان أحدث كان الأفضل) ، ملاحظة: استخدام مصدر pip الرسمي أو مصدر ali pip فقط ، طريقة تغيير المصدر المؤقت: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (الخيار II: إذا لم يكن لديك خبرة في Python) فيمكنك استخدام anaconda فالتعليمات مشابهة (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # إنشاء بيئة anaconda
conda activate gptac_venv                 # تنشيط بيئة anaconda
python -m pip install -r requirements.txt # هذه الخطوة مشابهة لخطوة pip الأولى
```

<details><summary>إذا كنت تحتاج إلى دعم ChatGLM الخاص بجامعة Tsinghua/Fudan MOSS كخلفية ، يرجى النقر على هذا الرابط لفتح هذا القسم</summary>
<p>

【خطوات اختيارية】 إذا كنت تحتاج إلى دعم ChatGLM الخاص بجامعة Tsinghua/Fudan MOSS كخلفية ، فيجب تثبيت المزيد من الأدوات (الشروط الأساسية: إتقان Python + Pytorch + تهيئة قوية للكمبيوتر):
```sh
# 【خطوة اختيارية I】 دعم ChatGLM جامعة Tsinghua. ملاحظة ChatGLM جامعة Tsinghua: إذا واجهت خطأ "Call ChatGLM fail لا يمكن تحميل معلمات ChatGLM بشكل صحيح" ، يرجى الرجوع إلى ما يلي: 1: الإصدار الافتراضي في الأعلى هو torch + cpu ؛ للاستخدام cuda يجب إلغاء تثبيت torch وإعادة تثبيت torch + cuda. 2: إذا كانت القدرة على تحميل النموذج غير كافية بسبب عدم كفاية تكوين جهاز الكمبيوتر المحلي ، فيمكن تغيير دقة النموذج في request_llm / bridge_chatglm.py وتعديل AutoTokenizer.from_pretrained ("THUDM / chatglm-6b" ، trust_remote_code = True) إلى AutoTokenizer.from_pretrained ("THUDM / chatglm-6b-int4" ، trust_remote_code = True)
python -m pip install -r request_llm/requirements_chatglm.txt  

# 【خطوة اختيارية II】 دعم Fudan MOSS
python -m pip install -r request_llm/requirements_moss.txt
git clone https://github.com/OpenLMLab/MOSS.git request_llm/moss  # ملاحظة: يجب أن يتم تنفيذ هذا السطر أثناء وجودك في مسار المشروع الرئيسي

# 【خطوة اختيارية III】 تأكد من أن ملف config.py يتضمن AVAIL_LLM_MODELS النموذج المطلوب ، والقائمة الكاملة للنماذج المدعومة حاليًا كما يلي (سلسلة jittorllms_series لا تزال تدعم الحلول المحدودة لصنع الحاويات فقط):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "newbing", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. تشغيل البرنامج
```sh
python main.py
```5. تعديل إضافة مكونات الوظائف المختبرة

```
- وظيفة قالب مكونات وظيفة الاختبار (تتطلب إجابة GPT على ما حدث في مثال الماضي) ، يمكنك استخدام هذه الوظيفة كنموذج لتنفيذ وظائف أكثر تعقيدًا بناءً على هذا القالب
انقر فوق "[عرض أمثلة قوالب مكونات الوظائف الاختبارية] في الماضي المنشور"

```

## التثبيت-الطريقة 2: باستخدام Docker

1. فقط ChatGPT (مستحسن للغالبية العظمى من الأشخاص)

``` sh
git clone https://github.com/binary-husky/chatgpt_academic.git  #تحميل المشروع
cd chatgpt_academic                                 # قم بالتحويل إلى المسار
nano config.py                                      # التحرير "Proxy" ، "API_KEY" ثم "WEB_PORT" (على سبيل المثال 50923) وغيرها
docker build -t gpt-academic .                      # </span>التثبيت

#(الخطوة الأخيرة - الخيار 1) في بيئة Linux ، استخدم `--net=host` </span> لتوفير الوقت والجهد
docker run --rm -it --net=host gpt-academic
#(الخطوة الأخيرة - الخيار 2) في macOS / بيئات Windows ، يمكن فقط استخدام خيار -p لتعريض منفذ الحاوية (على سبيل المثال 50923) إلى منفذ المضيف
docker run --rm -it -e WEB_PORT=50923 -p 50923:50923 gpt-academic
```

2. ChatGPT + ChatGLM + MOSS ( يتطلب المطلع دراية جيدة ب Docker)

``` sh
حرر docker-compose.yml وقم بحذف الخطوة 1 والخطوة 3 والاحتفاظ بالخطوة 2. بعد ذلك ، قم بتعديل Docker-Compose.yml في الخطوة 2 وأعد الرجوع </span>إلى التعليمات الموجودة في الجزء التعليمي ، وسيتم تشغيل البرنامج بنجاح. 
docker-compose up
```

3. ChatGPT + LLAMA + Pangu + RWKV (يتطلب المطلع دراية جيدة ب Docker)
``` sh
حرر docker-compose.yml وقم بحذف الخطوة 1 والخطوة 2 والاحتفاظ بالخطوة 3. بعد ذلك ، قم بتعديل Docker-Compose.yml في الخطوة 3 وأعد الرجوع </span> إلى التعليمات الموجودة في </div>الدليل ، وسيتم تشغيل البرنامج بنجاح.

docker-compose up
```


## التثبيت-الطريقة 3: لتثبيت بطرق أخرى

1. كيفية استخدام "الاستجابة لعنوان URL / خادم Azure API" بأولوية دعم لـ config.py

قم بتكوين API_URL_REDIRECT كما هو مذكور في "config.py".

2. الإخفاء التحتي لخادم السحابة البعيد (يلزم معرفة خبراء خادم السحابة وتجربة)

يرجى زيارة الموقع [Hidden Wiki-1] (https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)


3. استخدام WSL2 (نظام Windows Subsystem for Linux الفرعي)
يرجى زيارة الصفحة [Hidden Wiki-2] (https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)

4. تشغيله في عنوان URL من المستوى الثاني (مثل` http://localhost/subpath`) </ </div>span> الإجراء الذي صفه FastAPI ، يرجى الرجوع إلى إرشادات التشغيل في الوثائق  (docs/WithFastapi.md)

5. تشغيل باستخدام docker-compose
يرجى قراءة docker-compose.yml ، ثم تنفيذ الإجراءات وفقًا لتلميحاته للاستخدام المتقدم 

# التحديث الأخير
## ميزات جديدة ديناميكية</div>

1. وظيفة حفظ الحوار. يمكنك حفظ الحوار الحالي كملف قابل للقراءة والاسترجاع بتنفيذ "حفظ الحوار الحالي" في مكون الوظائف، بالإضافة إلى ذلك، يمكنك استعادة الدردشة السابقة عن طريق تنفيذ "تحميل أرشيف الحوار" من قائمة السحب المنسدلة في مكون الوظائف. تلميح: يمكنك النقر على "تحميل أرشيف الحوار" مباشرة دون تحديد ملف لرؤية ذاكرة التخزين المؤقت لأرشيف HTML السابق. كما يمكنك النقر على "حذف كل سجلات الحوار المحلية" لحذف كل ذاكرة التخزين المؤقت لأرشيف HTML.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. إنشاء تقرير. يقوم معظم المكونات بإنشاء تقارير عمل بعد الانتهاء من التنفيذ.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

3. تصميم الوظائف المتكاملة والملاحة البسيطة تتيح واجهة بسيطة يمكنها توفير وظائف قوية.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

4. هذا هو مشروع مفتوح المصدر قادر على "ترجمة نفسه بنفسه".
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="500" >
</div>

5. ترجمة مشاريع مفتوحة المصدر بسهولة.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="500" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="500" >
</div>

6. اضافة ميزات صغيرة لتزيين [live2d] (https://github.com/fghrsh/live2d_demo) (معطلة افتراضيًا ، يجب تعديل `config.py`).
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. دعم نموذج اللغة الكبرى MOSS.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236639178-92836f37-13af-4fdd-984d-b4450fe30336.png" width="500" >
</div>

8. إنشاء صور OpenAI.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

9. تحليل وملخص الصوت من OpenAI.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

10. تصحيح كامل للخطأ والأخطاء الصرفية الكاملة في Latex.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" width="500" >
</div>


##الإصدار:
- Version 3.5 (Pending): استدعاء الوظائف المكونة لهذا المشروع بلغة طبيعية (أولوية عالية)
- الإصدار 3.4 (قيد التنفيذ): دعم متعدد الخطوط ل chatglm الذاتي الترميز.
- الإصدار 3.3: + وظيفة معلومات شاملة للإنترنت
- إصدار 3.2: دعم واجهة مستخدم مطورة لوظائف المكونات الإضافية (حفظ الحوار، قراءة أي كود ثنائي، السؤال عن أي توصيل LLM).
- إصدار 3.1: دعم تعدد نماذج GPT في نفس الوقت! دعم api2d، دعم توازن حمل مفاتيح الواجهة البرمجية.
- الإصدار 3.0: الدعم chatglm و أجهزة الصغرى LLM الأخرى.
- الإصدار 2.6: إعادة تصميم هيكل المكونات، وتحسين التفاعلية، وإضافة المزيد من الوظائف المكونة.
- الإصدار 2.5: الحصول على تحديث ذاتي، وحل مشاكل النص الطويل عند استخلاص مشاريع كبيرة.
- الإصدار 2.4: (1) إضافة وظيفة ترجمة PDF بالكامل. (2) وظيفة تحويل موقع الإدخال (3) خيار التخطيط الرأسي (4) تحسين وظائف المكونات بتعدد الخطوط.
- إصدار 2.3: تعزيز التفاعلية متعددة الخطوط
- إصدار 2.2: دعم إعادة التحميل الساخن لوظائف المكونات
- الإصدار 2.1: تقدم نافذة مقسمة الطي
- إصدار 2.0: الدعم النمطي لوظائف المكونات
- الإصدار 1.0: الوظائف الأساسية.gpt_academic مطوري QQ مجموعة -2: 610599535

- المشاكل المعروفة:
    - تداخل بعض إضافات ترجمة المتصفح مع تشغيل واجهة برمجية التطبيقات الأمامية لهذا البرنامج
    - إصدار gradio عالي أو منخفض قد يؤدي إلى أنواع مختلفة من الأخطاء

## الإشارات والتعلم

```
تم الاستشهاد بتصميم العديد من المشاريع الممتازة الأخرى في الرمز ، بما في ذلك:

# مشروع 1: تسلية تشاتجلم-6B في جامعة تسينغهوا:
https://github.com/THUDM/ChatGLM-6B

# مشروع 2: جيتور جامعة تسينغهوا:
https://github.com/Jittor/JittorLLMs

# مشروع 3: إيدج غبت:
https://github.com/acheong08/EdgeGPT

# مشروع 4: تشوانهو تشات جي بي تي:
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# مشروع 5: ورقة تشات:
https://github.com/kaixindelele/ChatPaper

# مزيد من المعلومات:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
```