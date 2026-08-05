


> **Remarque**
>
> Ce README a été traduit par GPT (implémenté par le plugin de ce projet) et n'est pas fiable à 100 %. Veuillez examiner attentivement les résultats de la traduction.
>
> 7 novembre 2023 : Lors de l'installation des dépendances, veuillez choisir les versions **spécifiées** dans le fichier `requirements.txt`. Commande d'installation : `pip install -r requirements.txt`.


# <div align=center><img src="logo.png" width="40"> Optimisation académique GPT (GPT Academic)</div>

**Si vous aimez ce projet, merci de lui donner une étoile ; si vous avez inventé des raccourcis ou des plugins utiles, n'hésitez pas à envoyer des demandes d'extraction !**

Si vous aimez ce projet, veuillez lui donner une étoile.
Pour traduire ce projet dans une langue arbitraire avec GPT, lisez et exécutez [`multi_language.py`](multi_language.py) (expérimental).

> **Remarque**
>
> 1. Veuillez noter que seuls les plugins (boutons) marqués en **surbrillance** prennent en charge la lecture de fichiers, et certains plugins se trouvent dans le **menu déroulant** de la zone des plugins. De plus, nous accueillons avec la plus haute priorité les nouvelles demandes d'extraction de plugins.
>
> 2. Les fonctionnalités de chaque fichier de ce projet sont spécifiées en détail dans [le rapport d'auto-analyse `self_analysis.md`](https://github.com/binary-husky/gpt_academic/wiki/GPT‐Academic个项目自译解报告). Vous pouvez également cliquer à tout moment sur les plugins de fonctions correspondants pour appeler GPT et générer un rapport d'auto-analyse du projet. Questions fréquemment posées [wiki](https://github.com/binary-husky/gpt_academic/wiki). [Méthode d'installation standard](#installation) | [Script d'installation en un clic](https://github.com/binary-husky/gpt_academic/releases) | [Instructions de configuration](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明)..
>
> 3. Ce projet est compatible avec et recommande l'expérimentation de grands modèles de langage chinois tels que ChatGLM, etc. Prend en charge plusieurs clés API, vous pouvez les remplir dans le fichier de configuration comme `API_KEY="openai-key1,openai-key2,azure-key3,api2d-key4"`. Pour changer temporairement la clé API, entrez la clé API temporaire dans la zone de saisie, puis appuyez sur Entrée pour soumettre et activer celle-ci.


<div align="center">

Fonctionnalités (⭐ = fonctionnalité récemment ajoutée) | Description
--- | ---
⭐[Modèles acquis](https://github.com/binary-husky/gpt_academic/wiki/如何切换模型)！ | Baidu [Qianfan](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Nlks5zkzu) et Wenxin Yiyuan, [Tongyi Qianwen](https://modelscope.cn/models/qwen/Qwen-7B-Chat/summary), Shanghai AI-Lab [Shusheng](https://github.com/InternLM/InternLM), Xunfei [Xinghuo](https://xinghuo.xfyun.cn/), [LLaMa2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf), Zhifu API, DALLE3
Amélioration, traduction, explication du code | Correction, traduction, recherche d'erreurs de syntaxe dans les articles, explication du code
[Raccourcis personnalisés](https://www.bilibili.com/video/BV14s4y1E7jN) | Prise en charge de raccourcis personnalisés
Conception modulaire | Prise en charge de plugins puissants personnalisables, prise en charge de la [mise à jour à chaud](https://github.com/binary-husky/gpt_academic/wiki/函数插件指南) des plugins
[Analyse de programme](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugin] Analyse en profondeur d'un arbre de projets Python/C/C++/Java/Lua/... d'un simple clic ou [auto-analyse](https://www.bilibili.com/video/BV1cj411A7VW)
Lecture d'articles, traduction d'articles | [Plugin] Lecture automatique des articles LaTeX/PDF et génération du résumé
Traduction complète de [LaTeX](https://www.bilibili.com/video/BV1nk4y1Y7Js/) ou amélioration de leur qualité | [Plugin] Traduction ou amélioration rapide des articles LaTeX
Génération de commentaires en masse | [Plugin] Génération facile de commentaires de fonctions
Traduction [chinois-anglais](https://www.bilibili.com/video/BV1yo4y157jV/) du Markdown | [Plugin] Avez-vous vu le [README](https://github.com/binary-husky/gpt_academic/blob/master/docs/README_EN.md) dans les cinq langues ci-dessus ?
Génération de rapports d'analyse du chat | [Plugin] Génération automatique d'un rapport récapitulatif après l'exécution du chat
[Fonction de traduction complète des articles PDF](https://www.bilibili.com/video/BV1KT411x7Wn) | [Plugin] Extraction du titre et du résumé d'un article PDF, ainsi que traduction intégrale (multithreading)
Assistant Arxiv | [Plugin] Saisissez l'URL d'un article Arxiv pour traduire automatiquement le résumé et télécharger le PDF
Correction automatique d'articles LaTeX | [Plugin] Correction de la grammaire, de l'orthographe et comparaison avec le PDF correspondant, à la manière de Grammarly
Assistant Google Scholar | [Plugin] Donner l'URL d'une page de recherche Google Scholar pour obtenir de l'aide sur l'écriture des références
Agrégation d'informations sur Internet + GPT | [Plugin] Obtenez les informations de l'Internet pour répondre aux questions à l'aide de GPT, afin que les informations ne soient jamais obsolètes
⭐Traduction détaillée des articles Arxiv ([Docker](https://github.com/binary-husky/gpt_academic/pkgs/container/gpt_academic_with_latex)) | [Plugin] Traduction de haute qualité d'articles Arxiv en un clic, le meilleur outil de traduction d'articles à ce jour
⭐[Saisie orale en temps réel](https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md) | [Plugin] Écoute asynchrone de l'audio, découpage automatique et recherche automatique du meilleur moment pour répondre
Affichage des formules, images, tableaux | Affichage simultané de la forme [TeX et rendue](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png) des formules, prise en charge de la mise en évidence des formules et du code
⭐Plugin AutoGen multi-agents | [Plugin] Explorez les émergences intelligentes à plusieurs agents avec Microsoft AutoGen !
Activation du [thème sombre](https://github.com/binary-husky/gpt_academic/issues/173) | Ajouter ```/?__theme=dark``` à l'URL du navigateur pour basculer vers le thème sombre
Prise en charge de plusieurs modèles LLM | Expérimentez avec GPT 3.5, GPT4, [ChatGLM2 de Tsinghua](https://github.com/THUDM/ChatGLM2-6B), [MOSS de Fudan](https://github.com/OpenLMLab/MOSS) simultanément !
⭐Modèle ChatGLM2 fine-tuned | Chargez et utilisez un modèle fine-tuned de ChatGLM2, disponible avec un plugin d'assistance
Prise en charge de plus de modèles LLM, déploiement sur [Huggingface](https://huggingface.co/spaces/qingxu98/gpt-academic) | Ajout de l'interface de connaissance-API, support de [LLaMA](https://github.com/facebookresearch/llama) et [PanGuα](https://openi.org.cn/pangu/)
⭐Paquet pip [void-terminal](https://github.com/binary-husky/void-terminal) | Accédez à toutes les fonctions et plugins de ce projet directement depuis Python (en cours de développement)
⭐Plugin terminal du vide | [Plugin] Utilisez un langage naturel pour interagir avec les autres plugins du projet
Affichage de nouvelles fonctionnalités (génération d'images, etc.) …… | Voir à la fin de ce document ……
</div>


- Nouvelle interface (modifiez l'option LAYOUT dans `config.py` pour basculer entre la disposition "gauche-droite" et "haut-bas")
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/d81137c3-affd-4cd1-bb5e-b15610389762" width="700" >
</div>


- Tous les boutons sont générés dynamiquement en lisant `functional.py`, vous pouvez donc ajouter de nouvelles fonctionnalités personnalisées et libérer le presse-papiers.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Retouche/correction
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>



- If the output contains formulas, they will be displayed in both tex and rendered forms for easy copying and reading.

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Don't feel like looking at the project code? Just give it to ChatGPT to show off.

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Multiple large language models are mixed and used together (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4).

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

# Installation
### Method I: Run directly (Windows, Linux, or MacOS)

1. Download the project
```sh
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git
cd gpt_academic
```

2. Configure API_KEY

In `config.py`, configure the API KEY and other settings. [Click here to see methods for special network environment configurations](https://github.com/binary-husky/gpt_academic/issues/1). [Wiki page](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明).

「 The program will first check if there is a confidential configuration file named `config_private.py`, and use the configurations in that file to override the corresponding configurations in `config.py`. If you understand this logic, we strongly recommend creating a new configuration file named `config_private.py` right next to `config.py`, and move (copy) the configurations from `config.py` to `config_private.py` (only copy the configurations that you have modified). 」

「 You can also configure the project using `environment variables`. The format of the environment variables can be found in the `docker-compose.yml` file or on our [Wiki page](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明). The priority of configuration reading is: `environment variables` > `config_private.py` > `config.py`. 」

3. Install dependencies
```sh
# (Option I: If you are familiar with Python, python>=3.9) Note: Use the official pip source or the Ali pip source. Temporary change of source method: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Option II: Use Anaconda) The steps are similar (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # Create an anaconda environment
conda activate gptac_venv                 # Activate the anaconda environment
python -m pip install -r requirements.txt # This step is the same as the pip installation step
```


<details><summary>If you need to support Tsinghua ChatGLM2/Fudan MOSS/RWKV as backends, click here to expand</summary>
<p>

[Optional Steps] If you need to support Tsinghua ChatGLM2/Fudan MOSS as backends, you need to install additional dependencies (Prerequisites: Familiar with Python + Have used PyTorch + Sufficient computer configuration):
```sh
# [Optional Step I] Support Tsinghua ChatGLM2. Comment on this note: If you encounter the error "Call ChatGLM generated an error and cannot load the parameters of ChatGLM", refer to the following: 1: The default installation is the torch+cpu version. To use cuda, you need to uninstall torch and reinstall torch+cuda; 2: If the model cannot be loaded due to insufficient computer configuration, you can modify the model precision in request_llm/bridge_chatglm.py. Change AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) to AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).
python -m pip install -r request_llms/requirements_chatglm.txt

# [Optional Step II] Support Fudan MOSS
python -m pip install -r request_llms/requirements_moss.txt
git clone --depth=1 https://github.com/OpenLMLab/MOSS.git request_llms/moss  # Note: You need to be at the root directory of the project when executing this line of code

# [Optional Step III] Support RWKV Runner
Refer to the wiki: https://github.com/binary-husky/gpt_academic/wiki/%E9%80%82%E9%85%8DRWKV-Runner

# [Optional Step IV] Make sure that the AVAIL_LLM_MODELS in the config.py configuration file contains the expected models. The currently supported models are as follows (jittorllms series currently only support the docker solution):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>


4. Run
```sh
python main.py
```

### Method II: Use Docker

0. Deploy all capabilities of the project (this is a large image that includes cuda and latex. But if you have a slow internet speed or a small hard drive, it is not recommended to use this)

``` sh
# Modify the docker-compose.yml file, keep scheme 0 and delete the other schemes. Then run:
docker-compose up
```

1. ChatGPT + Wenxin Yiyu + Spark and other online models (recommended for most people)

``` sh
# Modify the docker-compose.yml file, keep scheme 1 and delete the other schemes. Then run:
docker-compose up
```

NOTE: If you need Latex plugin functionality, please refer to the Wiki. Additionally, you can also use scheme 4 or scheme 0 directly to obtain Latex functionality.

2. ChatGPT + ChatGLM2 + MOSS + LLAMA2 + Tongyi Qianwen (requires familiarity with [Nvidia Docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#installing-on-ubuntu-and-debian) runtime)

``` sh
# Modify the docker-compose.yml file, keep scheme 2 and delete the other schemes. Then run:
docker-compose up
```


### Method III: Other deployment methods
1. **One-click run script for Windows**.
Windows users who are completely unfamiliar with the Python environment can download the one-click run script without local models from the [Release](https://github.com/binary-husky/gpt_academic/releases) section.
The script was contributed by [oobabooga](https://github.com/oobabooga/one-click-installers).

2. Use third-party APIs, Azure, Wenxin Yiyu, Xinghuo, etc., see the [Wiki page](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明).

3. Pitfall guide for deploying on cloud servers.
Please visit the [cloud server remote deployment wiki](https://github.com/binary-husky/gpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97).

4. Some new deployment platforms or methods
    - Use Sealos [one-click deployment](https://github.com/binary-husky/gpt_academic/issues/993).
    - Use WSL2 (Windows Subsystem for Linux). Please visit the [deployment wiki-2](https://github.com/binary-husky/gpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)
    - How to run under a subpath (such as `http://localhost/subpath`). Please see [FastAPI running instructions](docs/WithFastapi.md)



# Utilisation avancée
### I: Personnalisation des nouveaux boutons d'accès rapide (raccourcis académiques)
Ouvrez `core_functional.py` avec n'importe quel éditeur de texte, ajoutez les entrées suivantes, puis redémarrez le programme. (Si le bouton existe déjà, le préfixe et le suffixe peuvent être modifiés à chaud sans redémarrer le programme).
Par exemple:
```
"Traduction avancée de l'anglais vers le français": {
    # Préfixe, ajouté avant votre saisie. Par exemple, utilisez-le pour décrire votre demande, telle que la traduction, l'explication du code, l'amélioration, etc.
    "Prefix": "Veuillez traduire le contenu suivant en français, puis expliquer chaque terme propre à la langue anglaise utilisé dans le texte à l'aide d'un tableau markdown : \n\n",

    # Suffixe, ajouté après votre saisie. Par exemple, en utilisant le préfixe, vous pouvez entourer votre contenu par des guillemets.
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

### II: Personnalisation des plugins de fonction
Écrivez de puissants plugins de fonction pour accomplir toutes les tâches que vous souhaitez ou ne pouvez pas imaginer.
Le développement et le débogage de ces plugins dans ce projet sont très faciles. Tant que vous avez des connaissances de base en python, vous pouvez implémenter vos propres fonctionnalités grâce à notre modèle fourni.
Veuillez consulter le [Guide des plugins de fonction](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97) pour plus de détails.


# Mises à jour
### I: Dynamique

1. Fonction de sauvegarde de conversation. Appelez `Enregistrer la conversation en cours` dans la zone des plugins fonctionnels pour enregistrer la conversation en cours sous la forme d'un fichier HTML lisible et récupérable. En outre, appelez `Charger les archives de conversation` dans la zone des plugins fonctionnels (menu déroulant) pour restaurer les conversations précédentes.
Astuce: Si aucun fichier n'est spécifié, cliquez directement sur `Charger les archives de conversation` pour afficher le cache des archives HTML.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. ⭐ Fonction de traduction des articles Latex/Arxiv ⭐
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/002a1a75-ace0-4e6a-94e2-ec1406a746f1" height="250" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/9fdcc391-f823-464f-9322-f8719677043b" height="250" >
</div>

3. Terminal du néant (comprendre l'intention de l'utilisateur à partir de la saisie en langage naturel et appeler automatiquement d'autres plugins)

- Étape 1: Saisissez "Veuillez appeler le plugin de traduction pour le document PDF, l'URL est https://openreview.net/pdf?id=rJl0r3R9KX".
- Étape 2 : Cliquez sur "Terminal du néant".

<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/66f1b044-e9ff-4eed-9126-5d4f3668f1ed" width="500" >
</div>

4. Conception de fonctionnalités modulaires, une interface simple peut prendre en charge des fonctionnalités puissantes
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

5. Traduction et interprétation d'autres projets open-source
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" height="250" >
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" height="250" >
</div>

6. Fonctionnalités supplémentaires intégrant [live2d](https://github.com/fghrsh/live2d_demo) (désactivé par défaut, nécessite des modifications dans `config.py`)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. Génération d'images par OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

8. Analyse et résumé audio par OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

9. Vérification et correction orthographique complète du document en Latex
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" height="200" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/476f66d9-7716-4537-b5c1-735372c25adb" height="200">
</div>

10. Changement de langue et de thème
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/b6799499-b6fb-4f0c-9c8e-1b441872f4e8" width="500" >
</div>



### II: Versions:
- version 3.70(tâche à accomplir) : Optimisation de la fonction AutoGen et création d'une série de plugins dérivés
- version 3.60 : Introduction d'AutoGen comme base des nouveaux plugins
- version 3.57 : Prise en charge de GLM3, Starlight v3, Zen v4 et correction de l'incompatibilité des modèles locaux
- version 3.56 : Possibilité d'ajouter dynamiquement des boutons de fonction de base et nouvelle page de synthèse des PDF
- version 3.55: Refonte de l'interface utilisateur avec fenêtres flottantes et barre de menu
- version 3.54 : Nouvel interpréteur de code dynamique (Code Interpreter) (à améliorer)
- version 3.53 : Possibilité de choisir dynamiquement différents thèmes d'interface, amélioration de la stabilité et résolution des problèmes de conflit entre utilisateurs multiples
- version 3.50 : Utiliser le langage naturel pour appeler toutes les fonctions du projet (Terminal du néant), prise en charge de la classification des plugins, amélioration de l'interface utilisateur, conception de nouveaux thèmes
- version 3.49 : Prise en charge de Baidu Qianfan et Xiaomi-Wenyiyan
- version 3.48 : Prise en charge d'Ali-DA, Shanghai AI-Lab-Shusheng et Xunfei Xinghuo
- version 3.46 : Prise en charge de la conversation audio temps réel sans intervention
- version 3.45 : Prise en charge de la personnalisation du modèle ChatGLM2
- version 3.44 : Prise en charge officielle d'Azure, amélioration de l'utilisabilité de l'interface
- version 3.4 : +traduction complète des articles Arxiv, +correction des articles Latex
- version 3.3 : +fonction d'intégration d'informations Internet
- version 3.2 : Les plugins de fonction prennent en charge plus de paramètres (fonction d'enregistrement de conversation, débogage de code de n'importe quel langage + demandes d'LLM arbitraires)
- version 3.1 : Prise en charge de l'interrogation simultanée de plusieurs modèles gpt ! Prise en charge de l'API2D, répartition de charge entre plusieurs clés API
- version 3.0 : Prise en charge de chatglm et d'autres petits llm
- version 2.6 : Refonte de la structure des plugins, amélioration de l'interactivité, ajout de nouveaux plugins
- version 2.5 : Auto-mise à jour, résolution des problèmes de dépassement de longueur de texte et de jeton pendant la consolidation de grands projets de codes sources
- version 2.4 : (1) Nouvelle fonctionnalité de traduction complète des documents PDF ; (2) Nouvelle fonctionnalité de changement de position de la zone de saisie ; (3) Nouvelle option de disposition verticale ; (4) Optimisation des plugins de fonction multithreads.
- version 2.3 : Amélioration de l'interactivité multi-threads
- version 2.2 : Prise en charge du rechargement à chaud des plugins de fonction
- version 2.1 : Mise en page pliable
- version 2.0 : Introduction de plugins de fonction modulaires
- version 1.0: Fonctionnalités de base

Groupe QQ des développeurs de GPT Academic: `610599535`

- Problèmes connus
    - Certains plugins de traduction de navigateurs peuvent nuire au fonctionnement de l'interface utilisateur de ce logiciel.
    - Gradio officiel a actuellement de nombreux bugs de compatibilité. Veuillez utiliser `requirement.txt` pour installer Gradio.

### III: Thèmes
Vous pouvez modifier le thème en modifiant l'option `THEME` (config.py).

1. `Chuanhu-Small-and-Beautiful` [Lien](https://github.com/GaiZhenbiao/ChuanhuChatGPT/)


### IV: Branches de développement de ce projet

1. Branche `master` : Branche principale, version stable
2. Branche `frontier` : Branche de développement, version de test


### V: Références et apprentissage

```
De nombreux designs de codes de projets exceptionnels ont été référencés dans le développement de ce projet, sans ordre spécifique :

# ChatGLM2-6B de l'Université Tsinghua:
https://github.com/THUDM/ChatGLM2-6B

# JittorLLMs de l'Université Tsinghua:
https://github.com/Jittor/JittorLLMs

# ChatPaper :
https://github.com/kaixindelele/ChatPaper

# Edge-GPT :
https://github.com/acheong08/EdgeGPT

# ChuanhuChatGPT :
https://github.com/GaiZhenbiao/ChuanhuChatGPT



# Oobabooga installeur en un clic :
https://github.com/oobabooga/one-click-installers

# Plus：
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
