> **Note**
>
> Ce fichier README est généré automatiquement par le plugin de traduction markdown de ce projet et n'est peut - être pas correct à 100%.
>
> During installation, please strictly select the versions **specified** in requirements.txt. 
>
> `pip install -r requirements.txt`
>

# <img src="logo.png" width="40" > Optimisation académique GPT (GPT Academic)

**Si vous aimez ce projet, veuillez lui donner une étoile. Si vous avez trouvé des raccourcis académiques ou des plugins fonctionnels plus utiles, n'hésitez pas à ouvrir une demande ou une pull request. 
Pour traduire ce projet dans une langue arbitraire avec GPT, lisez et exécutez [`multi_language.py`](multi_language.py) (expérimental).

> **Note**
>
> 1. Veuillez noter que seuls les plugins de fonctions (boutons) **en rouge** prennent en charge la lecture de fichiers. Certains plugins se trouvent dans le **menu déroulant** de la zone de plugins. De plus, nous accueillons et traitons les nouvelles pull requests pour les plugins avec **la plus haute priorité**!
>
> 2. Les fonctions de chaque fichier de ce projet sont expliquées en détail dans l'auto-analyse [`self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A). Avec l'itération des versions, vous pouvez également cliquer sur les plugins de fonctions pertinents et appeler GPT pour régénérer le rapport d'auto-analyse du projet à tout moment. Les FAQ sont résumées dans [le wiki](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98). [Méthode d'installation](#installation).
>
> 3. Ce projet est compatible avec et encourage l'utilisation de grands modèles de langage nationaux tels que chatglm, RWKV, Pangu, etc. La coexistence de plusieurs clés API est prise en charge et peut être remplie dans le fichier de configuration, tel que `API_KEY="openai-key1,openai-key2,api2d-key3"`. Lorsque vous souhaitez remplacer temporairement `API_KEY`, saisissez temporairement `API_KEY` dans la zone de saisie, puis appuyez sur Entrée pour soumettre et activer. 

<div align="center">Functionnalité | Description
--- | ---
Révision en un clic | prend en charge la révision en un clic et la recherche d'erreurs de syntaxe dans les articles
Traduction chinois-anglais en un clic | Traduction chinois-anglais en un clic
Explication de code en un clic | Affichage, explication, génération et ajout de commentaires de code
[Raccourcis personnalisés](https://www.bilibili.com/video/BV14s4y1E7jN) | prend en charge les raccourcis personnalisés
Conception modulaire | prend en charge de puissants plugins de fonction personnalisée, les plugins prennent en charge la [mise à jour à chaud](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)  
[Autoscanner](https://www.bilibili.com/video/BV1cj411A7VW) | [Plug-in de fonction] [Compréhension instantanée](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A) du code source de ce projet
[Analyse de programme](https://www.bilibili.com/video/BV1cj411A7VW) | [Plug-in de fonction] Analyse en un clic de la structure d'autres projets Python / C / C ++ / Java / Lua / ...
Lecture d'articles, [traduction](https://www.bilibili.com/video/BV1KT411x7Wn) d'articles | [Plug-in de fonction] Compréhension instantanée de l'article latex / pdf complet et génération de résumés
[Traduction](https://www.bilibili.com/video/BV1nk4y1Y7Js/) et [révision](https://www.bilibili.com/video/BV1FT411H7c5/) complets en latex | [Plug-in de fonction] traduction ou révision en un clic d'articles en latex
Génération de commentaires en masse | [Plug-in de fonction] Génération en un clic de commentaires de fonction en masse
Traduction [chinois-anglais](https://www.bilibili.com/video/BV1yo4y157jV/) en Markdown | [Plug-in de fonction] avez-vous vu la [README](https://github.com/binary-husky/chatgpt_academic/blob/master/docs/README_EN.md) pour les 5 langues ci-dessus?
Génération de rapports d'analyse de chat | [Plug-in de fonction] Génère automatiquement un rapport de résumé après l'exécution
[Traduction intégrale en pdf](https://www.bilibili.com/video/BV1KT411x7Wn) | [Plug-in de fonction] Extraction de titre et de résumé de l'article pdf + traduction intégrale (multi-thread)
[Aide à arxiv](https://www.bilibili.com/video/BV1LM4y1279X) | [Plug-in de fonction] Entrer l'url de l'article arxiv pour traduire et télécharger le résumé en un clic
[Aide à la recherche Google Scholar](https://www.bilibili.com/video/BV19L411U7ia) | [Plug-in de fonction] Donnez l'URL de la page de recherche Google Scholar, laissez GPT vous aider à [Ã©crire des ouvrages connexes](https://www.bilibili.com/video/BV1GP411U7Az/)
Aggrégation d'informations en ligne et GPT | [Plug-in de fonction] Permet à GPT de [récupérer des informations en ligne](https://www.bilibili.com/video/BV1om4y127ck), puis de répondre aux questions, afin que les informations ne soient jamais obsolètes
Affichage d'équations / images / tableaux | Fournit un affichage simultané de [la forme tex et de la forme rendue](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png), prend en charge les formules mathématiques et la coloration syntaxique du code
Prise en charge des plugins à plusieurs threads | prend en charge l'appel multithread de chatgpt, un clic pour traiter [un grand nombre d'articles](https://www.bilibili.com/video/BV1FT411H7c5/) ou de programmes
Thème gradio sombre en option de démarrage | Ajoutez```/?__theme=dark``` à la fin de l'URL du navigateur pour basculer vers le thème sombre
[Prise en charge de plusieurs modèles LLM](https://www.bilibili.com/video/BV1wT411p7yf), [API2D](https://api2d.com/) | Sera probablement très agréable d'être servi simultanément par GPT3.5, GPT4, [ChatGLM de Tsinghua](https://github.com/THUDM/ChatGLM-6B), [MOSS de Fudan](https://github.com/OpenLMLab/MOSS)
Plus de modèles LLM, déploiement de [huggingface](https://huggingface.co/spaces/qingxu98/gpt-academic) | Ajout prise en charge de l'interface Newbing (nouvelle bing), introduction du support de [Jittorllms de Tsinghua](https://github.com/Jittor/JittorLLMs), [LLaMA](https://github.com/facebookresearch/llama), [RWKV](https://github.com/BlinkDL/ChatRWKV) et [Panguα](https://openi.org.cn/pangu/)
Plus de nouvelles fonctionnalités (génération d'images, etc.) ... | Voir la fin de ce document pour plus de détails ...

</div>


- Nouvelle interface (modifier l'option LAYOUT de `config.py` pour passer d'une disposition ``gauche-droite`` à une disposition ``haut-bas``)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230361456-61078362-a966-4eb5-b49e-3c62ef18b860.gif" width="700" >
</div>- Tous les boutons sont générés dynamiquement en lisant functional.py et peuvent être facilement personnalisés pour ajouter des fonctionnalités personnalisées, ce qui facilite l'utilisation du presse-papiers.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Correction d'erreurs/lissage du texte.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- Si la sortie contient des équations, elles sont affichées à la fois sous forme de tex et sous forme rendue pour faciliter la lecture et la copie.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Pas envie de lire les codes de ce projet? Tout le projet est directement exposé par ChatGPT.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Appel à une variété de modèles de langage de grande envergure (ChatGLM + OpenAI-GPT3.5 + [API2D] (https://api2d.com/)-GPT4).
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

---
# Installation
## Installation-Method 1: running directly (Windows, Linux or MacOS)

1. Télécharger le projet
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. Configuration de la clé API

Dans `config.py`, configurez la clé API et d'autres paramètres. Consultez [Special network environment settings] (https://github.com/binary-husky/gpt_academic/issues/1).

(P.S. Lorsque le programme est exécuté, il vérifie en premier s'il existe un fichier de configuration privé nommé `config_private.py` et remplace les paramètres portant le même nom dans `config.py` par les paramètres correspondants dans `config_private.py`. Par conséquent, si vous comprenez la logique de lecture de nos configurations, nous vous recommandons vivement de créer un nouveau fichier de configuration nommé `config_private.py` à côté de `config.py` et de transférer (copier) les configurations de `config.py`. `config_private.py` n'est pas contrôlé par Git et peut garantir la sécurité de vos informations privées. P.S. Le projet prend également en charge la configuration de la plupart des options via "variables d'environnement", le format d'écriture des variables d'environnement est référencé dans le fichier `docker-compose`. Priorité de lecture: "variables d'environnement" > `config_private.py` > `config.py`)


3. Installer les dépendances
```sh
# (Option I: python users instalation) (Python version 3.9 or higher, the newer the better). Note: use official pip source or ali pip source. To temporarily change the source: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Option II: non-python users instalation) Use Anaconda, the steps are similar (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # Create anaconda env
conda activate gptac_venv                 # Activate anaconda env
python -m pip install -r requirements.txt # Same step as pip instalation
```

<details><summary>Cliquez ici pour afficher le texte si vous souhaitez prendre en charge THU ChatGLM/FDU MOSS en tant que backend.</summary>
<p>

【Optional】 Si vous souhaitez prendre en charge THU ChatGLM/FDU MOSS en tant que backend, des dépendances supplémentaires doivent être installées (prérequis: compétent en Python + utilisez Pytorch + configuration suffisante de l'ordinateur):
```sh
# 【Optional Step I】 Support THU ChatGLM. Remarque sur THU ChatGLM: Si vous rencontrez l'erreur "Appel à ChatGLM échoué, les paramètres ChatGLM ne peuvent pas être chargés normalement", reportez-vous à ce qui suit: 1: La version par défaut installée est torch+cpu, si vous souhaitez utiliser cuda, vous devez désinstaller torch et réinstaller torch+cuda; 2: Si le modèle ne peut pas être chargé en raison d'une configuration insuffisante de l'ordinateur local, vous pouvez modifier la précision du modèle dans request_llm/bridge_chatglm.py, modifier AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) par AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llm/requirements_chatglm.txt  

# 【Optional Step II】 Support FDU MOSS
python -m pip install -r request_llm/requirements_moss.txt
git clone https://github.com/OpenLMLab/MOSS.git request_llm/moss  # Note: When running this line of code, you must be in the project root path.

# 【Optional Step III】Make sure the AVAIL_LLM_MODELS in the config.py configuration file contains the desired model. Currently, all models supported are as follows (the jittorllms series currently only supports the docker scheme):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "newbing", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. Exécution
```sh
python main.py
```5. Plugin de fonction de test
```
- Fonction de modèle de plugin de test (requiert que GPT réponde à ce qui s'est passé dans l'histoire aujourd'hui), vous pouvez utiliser cette fonction comme modèle pour mettre en œuvre des fonctionnalités plus complexes.
    Cliquez sur "[Démo de modèle de plugin de fonction] Aujourd'hui dans l'histoire"
```

## Installation - Méthode 2: Utilisation de Docker

1. ChatGPT uniquement (recommandé pour la plupart des gens)

``` sh
git clone https://github.com/binary-husky/chatgpt_academic.git  # Télécharger le projet
cd chatgpt_academic                                 # Accéder au chemin
nano config.py                                      # Editez config.py avec n'importe quel éditeur de texte en configurant "Proxy", "API_KEY" et "WEB_PORT" (p. ex. 50923)
docker build -t gpt-academic .                      # Installer

# (Dernière étape - choix1) Dans un environnement Linux, l'utilisation de `--net=host` est plus facile et rapide
docker run --rm -it --net=host gpt-academic
# (Dernière étape - choix 2) Dans un environnement macOS/Windows, seule l'option -p permet d'exposer le port du récipient (p.ex. 50923) au port de l'hôte.
docker run --rm -it -e WEB_PORT=50923 -p 50923:50923 gpt-academic
```

2. ChatGPT + ChatGLM + MOSS (il faut connaître Docker)

``` sh
# Modifiez docker-compose.yml, supprimez la solution 1 et la solution 3, conservez la solution 2. Modifiez la configuration de la solution 2 dans docker-compose.yml en suivant les commentaires.
docker-compose up
```

3. ChatGPT + LLAMA + PanGu + RWKV (il faut connaître Docker)
``` sh
# Modifiez docker-compose.yml, supprimez la solution 1 et la solution 2, conservez la solution 3. Modifiez la configuration de la solution 3 dans docker-compose.yml en suivant les commentaires.
docker-compose up
```


## Installation - Méthode 3: Autres méthodes de déploiement

1. Comment utiliser une URL de proxy inversé / Microsoft Azure Cloud API
Configurez simplement API_URL_REDIRECT selon les instructions de config.py.

2. Déploiement distant sur un serveur cloud (connaissance et expérience des serveurs cloud requises)
Veuillez consulter [Wiki de déploiement-1] (https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97).

3. Utilisation de WSL2 (sous-système Windows pour Linux)
Veuillez consulter [Wiki de déploiement-2] (https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2).

4. Comment exécuter sous un sous-répertoire (tel que `http://localhost/subpath`)
Veuillez consulter les [instructions d'exécution de FastAPI] (docs/WithFastapi.md).

5. Utilisation de docker-compose
Veuillez lire docker-compose.yml, puis suivre les instructions fournies.

# Utilisation avancée
## Personnalisation de nouveaux boutons pratiques / Plugins de fonctions personnalisées

1. Personnalisation de nouveaux boutons pratiques (raccourcis académiques)
Ouvrez core_functional.py avec n'importe quel éditeur de texte, ajoutez une entrée comme suit, puis redémarrez le programme. (Si le bouton a été ajouté avec succès et est visible, le préfixe et le suffixe prennent en charge les modifications à chaud et ne nécessitent pas le redémarrage du programme pour prendre effet.)
Par exemple
```
"Super coller sens": {
    # Préfixe, sera ajouté avant votre entrée. Par exemple, pour décrire votre demande, telle que traduire, expliquer du code, faire la mise en forme, etc.
    "Prefix": "Veuillez traduire le contenu suivant en chinois, puis expliquer chaque terme proprement nommé qui y apparaît avec un tableau markdown:\n\n", 
    
    # Suffixe, sera ajouté après votre entrée. Par exemple, en utilisant le préfixe, vous pouvez entourer votre contenu d'entrée de guillemets.
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

2. Plugins de fonctions personnalisées

Écrivez des plugins de fonctions puissants pour effectuer toutes les tâches que vous souhaitez ou que vous ne pouvez pas imaginer.
Les plugins de ce projet ont une difficulté de programmation et de débogage très faible. Si vous avez des connaissances de base en Python, vous pouvez simuler la fonctionnalité de votre propre plugin en suivant le modèle que nous avons fourni.
Veuillez consulter le [Guide du plugin de fonction] (https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97) pour plus de détails.

---
# Latest Update

## Nouvelles fonctionnalités en cours de déploiement.

1. Fonction de sauvegarde de la conversation.
Appelez simplement "Enregistrer la conversation actuelle" dans la zone de plugin de fonction pour enregistrer la conversation actuelle en tant que fichier html lisible et récupérable. De plus, dans la zone de plugin de fonction (menu déroulant), appelez "Charger une archive de l'historique de la conversation" pour restaurer la conversation précédente. Astuce : cliquer directement sur "Charger une archive de l'historique de la conversation" sans spécifier de fichier permet de consulter le cache d'archive html précédent. Cliquez sur "Supprimer tous les enregistrements locaux de l'historique de la conversation" pour supprimer le cache d'archive html.

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>



2. Générer un rapport. La plupart des plugins génèrent un rapport de travail après l'exécution.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

3. Conception de fonctionnalités modulaires avec une interface simple mais capable d'une fonctionnalité puissante.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

4. C'est un projet open source qui peut "se traduire de lui-même".
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="500" >
</div>

5. Traduire d'autres projets open source n'est pas un problème.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="500" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="500" >
</div>

6. Fonction de décoration de live2d (désactivée par défaut, nécessite une modification de config.py).
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. Prise en charge du modèle de langue MOSS.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236639178-92836f37-13af-4fdd-984d-b4450fe30336.png" width="500" >
</div>

8. Génération d'images OpenAI.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

9. Analyse et synthèse vocales OpenAI.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

10. Correction de la totalité des erreurs de Latex.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" width="500" >
</div>


## Versions :
- version 3.5 (À faire) : appel de toutes les fonctions de plugin de ce projet en langage naturel (priorité élevée)
- version 3.4 (À faire) : amélioration du support multi-thread de chatglm en local
- version 3.3 : Fonctionnalité intégrée d'informations d'internet 
- version 3.2 : La fonction du plugin de fonction prend désormais en charge des interfaces de paramètres plus nombreuses (fonction de sauvegarde, décodage de n'importe quel langage de code + interrogation simultanée de n'importe quelle combinaison de LLM)
- version 3.1 : Prise en charge de l'interrogation simultanée de plusieurs modèles GPT ! Support api2d, équilibrage de charge multi-clé api.
- version 3.0 : Prise en charge de chatglm et autres LLM de petite taille.
- version 2.6 : Refonte de la structure des plugins, amélioration de l'interactivité, ajout de plus de plugins.
- version 2.5 : Auto-mise à jour, résolution des problèmes de texte trop long et de dépassement de jetons lors de la compilation du projet global.
- version 2.4 : (1) Nouvelle fonction de traduction de texte intégral PDF ; (2) Nouvelle fonction de permutation de position de la zone d'entrée ; (3) Nouvelle option de mise en page verticale ; (4) Amélioration des fonctions multi-thread de plug-in.
- version 2.3 : Amélioration de l'interactivité multithread.
- version 2.2 : Les plugins de fonctions peuvent désormais être rechargés à chaud.
- version 2.1 : Disposition pliable
- version 2.0 : Introduction de plugins de fonctions modulaires
- version 1.0 : Fonctionnalités de base

gpt_academic développeur QQ groupe-2：610599535

- Problèmes connus
    - Certains plugins de traduction de navigateur perturbent le fonctionnement de l'interface frontend de ce logiciel
    - Des versions gradio trop hautes ou trop basses provoquent de nombreuses anomalies

## Référence et apprentissage

```
De nombreux autres excellents projets ont été référencés dans le code, notamment :

# Projet 1 : ChatGLM-6B de Tsinghua :
https://github.com/THUDM/ChatGLM-6B

# Projet 2 : JittorLLMs de Tsinghua :
https://github.com/Jittor/JittorLLMs

# Projet 3 : Edge-GPT :
https://github.com/acheong08/EdgeGPT

# Projet 4 : ChuanhuChatGPT :
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# Projet 5 : ChatPaper :
https://github.com/kaixindelele/ChatPaper

# Plus :
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
```