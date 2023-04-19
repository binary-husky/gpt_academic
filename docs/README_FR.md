> **Note**
>
> Ce fichier README est généré automatiquement par le plugin de traduction markdown de ce projet et n'est peut - être pas correct à 100%.
>

# <img src="logo.png" width="40" > ChatGPT Optimisation Académique

**Si vous aimez ce projet, donnez-lui une étoile; si vous avez inventé des raccourcis académiques plus utiles ou des plugins fonctionnels, n'hésitez pas à ouvrir une demande ou une demande de traction. Nous avons également un fichier README en [anglais|](docs/README_EN.md)[japonais|](docs/README_JP.md)[russe|](docs/README_RS.md)[français](docs/README_FR.md) traduit par ce projet lui-même.**

> **Note**
>
> 1. Veuillez noter que seuls les plugins de fonction signalés en **rouge** sont capables de lire les fichiers, certains plugins se trouvent dans le **menu déroulant** de la section plugin. Nous sommes également les bienvenus avec la plus haute priorité pour traiter et accepter tout nouveau PR de plugin!
>
> 2. Chaque fichier dans ce projet est expliqué en détail dans l'auto-analyse [self_analysis.md](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A). Avec l'itération des versions, vous pouvez également cliquer sur les plugins fonctionnels pertinents pour appeler GPT et générer un rapport d'auto-analyse projet mis à jour. Les questions fréquemment posées sont résumées dans le [wiki](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98).
> 

<div align="center">

Fonctionnalité | Description
--- | ---
Polissage en un clic | Prend en charge la correction en un clic et la recherche d'erreurs de syntaxe dans les documents de recherche.
Traduction Chinois-Anglais en un clic | Une touche pour traduire la partie chinoise en anglais ou celle anglaise en chinois.
Explication de code en un clic | Affiche et explique correctement le code.
[Raccourcis clavier personnalisables](https://www.bilibili.com/video/BV14s4y1E7jN) | Prend en charge les raccourcis clavier personnalisables.
[Configuration du serveur proxy](https://www.bilibili.com/video/BV1rc411W7Dr) | Prend en charge la configuration du serveur proxy.
Conception modulaire | Prend en charge la personnalisation des plugins de fonctions et des [plugins] de fonctions hiérarchiques personnalisés, et les plugins prennent en charge [la mise à jour à chaud](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97).
[Auto-analyse du programme](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugins] [Lire en un clic](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A) le code source de ce projet.
[Analyse de programme](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugins] En un clic, les projets Python/C/C++/Java/Lua/... peuvent être analysés.
Lire le document de recherche | [Plugins] Lisez le résumé de l'article en latex et générer un résumé.
Traduction et polissage de l'article complet en LaTeX | [Plugins] Une touche pour traduire ou corriger en LaTeX
Génération Commentaire de fonction en vrac | [Plugins] Lisez en un clic les fonctions et générez des commentaires de fonction.
Rapport d'analyse automatique des chats générés | [Plugins] Génère un rapport de synthèse après l'exécution.
[Assistant arxiv](https://www.bilibili.com/video/BV1LM4y1279X) | [Plugins] Entrez l'url de l'article arxiv pour traduire le résumé + télécharger le PDF en un clic
[Traduction complète des articles PDF](https://www.bilibili.com/video/BV1KT411x7Wn) | [Plugins] Extraire le titre et le résumé de l'article PDF + Traduire le texte entier (multithread)
[Aide à la recherche Google Academ](https://www.bilibili.com/video/BV19L411U7ia) | [Plugins] Donnez à GPT l'URL de n'importe quelle page de recherche Google Academ pour vous aider à sélectionner des articles intéressants
Affichage de formules/images/tableaux | Afficher la forme traduite et rendue d'une formule en même temps, plusieurs formules et surlignage du code prend en charge
Prise en charge des plugins multithread | Prise en charge de l'appel multithread de chatgpt, traitement en masse de texte ou de programmes en un clic
Activer le thème Gradio sombre [theme](https://github.com/binary-husky/chatgpt_academic/issues/173) au démarrage | Ajoutez ```/?__dark-theme=true``` à l'URL du navigateur pour basculer vers le thème sombre
[Prise en charge de plusieurs modèles LLM](https://www.bilibili.com/video/BV1wT411p7yf), [prise en charge de l'interface API2D](https://api2d.com/) | Comment cela serait-il de se faire servir par GPT3.5, GPT4 et la [ChatGLM de Tsinghua](https://github.com/THUDM/ChatGLM-6B) en même temps?
Expérience en ligne d'huggingface sans science | Après vous être connecté à huggingface, copiez [cet espace](https://huggingface.co/spaces/qingxu98/gpt-academic)
... | ...

</div>


Vous êtes un traducteur professionnel d'articles universitaires en français.

Ceci est un fichier Markdown, veuillez le traduire en français sans modifier les commandes Markdown existantes :

- Nouvelle interface (modifiable en modifiant l'option de mise en page dans config.py pour basculer entre les mises en page gauche-droite et haut-bas)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230361456-61078362-a966-4eb5-b49e-3c62ef18b860.gif" width="700" >
</div>


- Tous les boutons sont générés dynamiquement en lisant functional.py, les utilisateurs peuvent ajouter librement des fonctions personnalisées pour libérer le presse-papiers.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Correction/amélioration
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- Si la sortie contient des formules, elles seront affichées simultanément sous forme de de texte brut et de forme rendue pour faciliter la copie et la lecture.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Pas envie de lire le code du projet ? Faites votre propre démo avec ChatGPT.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Utilisation combinée de plusieurs modèles de langage sophistiqués (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

Utilisation combinée de plusieurs modèles de langage sophistiqués en version de test [huggingface](https://huggingface.co/spaces/qingxu98/academic-chatgpt-beta) (la version huggingface ne prend pas en charge Chatglm).


---

## Installation - Méthode 1 : Exécution directe (Windows, Linux or MacOS)

1. Téléchargez le projet
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. Configuration de l'API_KEY et des paramètres de proxy

Dans `config.py`, configurez les paramètres de proxy et de clé d'API OpenAI, comme indiqué ci-dessous
```
1. Si vous êtes en Chine, vous devez configurer un proxy étranger pour utiliser l'API OpenAI en toute transparence. Pour ce faire, veuillez lire attentivement le fichier config.py (1. Modifiez l'option USE_PROXY ; 2. Modifiez les paramètres de proxies comme indiqué dans les instructions).
2. Configurez votre clé API OpenAI. Vous devez vous inscrire sur le site web d'OpenAI pour obtenir une clé API. Une fois que vous avez votre clé API, vous pouvez la configurer dans le fichier config.py.
3. Tous les problèmes liés aux réseaux de proxy (temps d'attente, non-fonctionnement des proxies) sont résumés dans https://github.com/binary-husky/chatgpt_academic/issues/1.
```
(Remarque : le programme vérifie d'abord s'il existe un fichier de configuration privé nommé `config_private.py`, et utilise les configurations de celui-ci à la place de celles du fichier `config.py`. Par conséquent, si vous comprenez notre logique de lecture de configuration, nous vous recommandons fortement de créer un nouveau fichier de configuration nommé `config_private.py` à côté de `config.py` et de transférer (copier) les configurations de celui-ci dans `config_private.py`. `config_private.py` n'est pas contrôlé par git et rend vos informations personnelles plus sûres.)

3. Installation des dépendances
```sh
# (Option 1) Recommandé
python -m pip install -r requirements.txt   

# (Option 2) Si vous utilisez anaconda, les étapes sont similaires :
# (Option 2.1) conda create -n gptac_venv python=3.11
# (Option 2.2) conda activate gptac_venv
# (Option 2.3) python -m pip install -r requirements.txt

# note : Utilisez la source pip officielle ou la source pip Alibaba. D'autres sources (comme celles des universités) pourraient poser problème. Pour utiliser temporairement une autre source, utilisez :
# python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

Si vous avez besoin de soutenir ChatGLM de Tsinghua, vous devez installer plus de dépendances (si vous n'êtes pas familier avec Python ou que votre ordinateur n'est pas assez performant, nous vous recommandons de ne pas essayer) :
```sh
python -m pip install -r request_llm/requirements_chatglm.txt
```

4. Exécution
```sh
python main.py
```

5. Tester les plugins de fonctions
```
- Test Python Project Analysis
    Dans la zone de saisie, entrez `./crazy_functions/test_project/python/dqn`, puis cliquez sur "Parse Entire Python Project"
- Test d'auto-lecture du code
    Cliquez sur "[Démo multi-thread] Parser ce projet lui-même (auto-traduction de la source)"
- Test du modèle de fonctionnalité expérimentale (exige une réponse de l'IA à ce qui est arrivé aujourd'hui dans l'histoire). Vous pouvez utiliser cette fonctionnalité comme modèle pour des fonctions plus complexes.
    Cliquez sur "[Démo modèle de plugin de fonction] Histoire du Jour"
- Le menu déroulant de la zone de plugin de fonctionnalité contient plus de fonctionnalités à sélectionner.
```

## Installation - Méthode 2 : Utilisation de docker (Linux)


Vous êtes un traducteur professionnel d'articles académiques en français.

1. ChatGPT seul (recommandé pour la plupart des gens)
``` sh
# Télécharger le projet
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
# Configurer le proxy outre-mer et la clé API OpenAI
Modifier le fichier config.py avec n'importe quel éditeur de texte
# Installer
docker build -t gpt-academic .
# Exécuter
docker run --rm -it --net=host gpt-academic

# Tester les modules de fonction
## Tester la fonction modèle des modules (requiert la réponse de GPT à "qu'est-ce qui s'est passé dans l'histoire aujourd'hui ?"), vous pouvez utiliser cette fonction en tant que modèle pour implémenter des fonctions plus complexes.
Cliquez sur "[Exemple de modèle de module] Histoire d'aujourd'hui"
## Tester le résumé écrit pour le projet LaTeX
Dans la zone de saisie, tapez ./crazy_functions/test_project/latex/attention, puis cliquez sur "Lire le résumé de l'article de recherche LaTeX"
## Tester l'analyse du projet Python
Dans la zone de saisie, tapez ./crazy_functions/test_project/python/dqn, puis cliquez sur "Analyser l'ensemble du projet Python"

D'autres fonctions sont disponibles dans la liste déroulante des modules de fonction.
```

2. ChatGPT+ChatGLM (nécessite une grande connaissance de docker et une configuration informatique suffisamment puissante)
``` sh
# Modifier le dockerfile
cd docs && nano Dockerfile+ChatGLM
# Comment construire | 如何构建 （Dockerfile+ChatGLM在docs路径下，请先cd docs）
docker build -t gpt-academic --network=host -f Dockerfile+ChatGLM .
# Comment exécuter | 如何运行 (1) Directement exécuter :
docker run --rm -it --net=host --gpus=all gpt-academic
# Comment exécuter | 如何运行 (2) Je veux effectuer quelques ajustements dans le conteneur avant de lancer :
docker run --rm -it --net=host --gpus=all gpt-academic bash
```

## Installation - Méthode 3 : Autres méthodes de déploiement

1. Déploiement sur un cloud serveur distant
Veuillez consulter le [wiki de déploiement-1](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)

2. Utilisation de WSL2 (Windows Subsystem for Linux)
Veuillez consulter le [wiki de déploiement-2](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)


## Configuration de la procuration de l'installation
### Méthode 1 : Méthode conventionnelle
[Configuration de la procuration](https://github.com/binary-husky/chatgpt_academic/issues/1)

### Méthode 2 : Tutoriel pour débutant pur
[Tutoriel pour débutant pur](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E9%97%AE%E9%A2%98%E7%9A%84%E6%96%B0%E6%89%8B%E8%A7%A3%E5%86%B3%E6%96%B9%E6%B3%95%EF%BC%88%E6%96%B9%E6%B3%95%E5%8F%AA%E9%80%82%E7%94%A8%E4%BA%8E%E6%96%B0%E6%89%8B%EF%BC%89)


---

## Personnalisation des nouveaux boutons pratiques (personnalisation des raccourcis académiques)
Ouvrez le fichier `core_functional.py` avec n'importe quel éditeur de texte, ajoutez les éléments suivants, puis redémarrez le programme. (Si le bouton a déjà été ajouté avec succès et est visible, le préfixe et le suffixe pris en charge peuvent être modifiés à chaud sans avoir besoin de redémarrer le programme.)
Par exemple:
```
"Traduction Français-Chinois": {
    # Préfixe, qui sera ajouté avant votre saisie. Par exemple, pour décrire votre demande, telle que la traduction, le débogage de code, l'amélioration, etc.
    "Prefix": "Veuillez traduire le contenu ci-dessous en chinois, puis expliquer chaque terme propre mentionné dans un tableau Markdown :\n\n", 
    
    # Suffixe, qui sera ajouté après votre saisie. Par exemple, en combinaison avec un préfixe, vous pouvez mettre le contenu de votre saisie entre guillemets.
    "Suffix": "",
},
```

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

---


## Présentation de certaines fonctionnalités

### Affichage des images:

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/228737599-bf0a9d9c-1808-4f43-ae15-dfcc7af0f295.png" width="800" >
</div>


### Si un programme peut comprendre et décomposer lui-même :

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="800" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936618-9b487e4b-ab5b-4b6e-84c6-16942102e917.png" width="800" >
</div>


### Analyse de tout projet Python/Cpp quelconque :
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="800" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="800" >
</div>

### Lecture et résumé générés automatiquement pour les articles en Latex
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227504406-86ab97cd-f208-41c3-8e4a-7000e51cf980.png" width="800" >
</div>

### Génération de rapports automatique
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

### Conception de fonctionnalités modulaires
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>


### Traduction de code source en anglais

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229720562-fe6c3508-6142-4635-a83d-21eb3669baee.png" height="400" >
</div>

## À faire et planification de version :
- version 3.2+ (à faire) : Prise en charge de plus de paramètres d'interface de plugin de fonction
- version 3.1 : Prise en charge de l'interrogation simultanée de plusieurs modèles GPT ! Prise en charge de l'API2d, prise en charge de la répartition de charge de plusieurs clés API
- version 3.0 : Prise en charge de chatglm et d'autres petits llm
- version 2.6 : Réorganisation de la structure du plugin, amélioration de l'interactivité, ajout de plus de plugins
- version 2.5 : Mise à jour automatique, résolution du problème de dépassement de jeton et de texte trop long lors de la compilation du code source complet
- version 2.4 : (1) Ajout de la fonctionnalité de traduction intégrale de PDF ; (2) Ajout d'une fonctionnalité de changement de position de zone de saisie ; (3) Ajout d'une option de disposition verticale ; (4) Optimisation du plugin de fonction multi-thread.
- version 2.3 : Amélioration de l'interactivité multi-thread
- version 2.2 : Prise en charge du rechargement à chaud du plugin de fonction
- version 2.1 : Mise en page pliable
- version 2.0 : Introduction du plugin de fonction modulaire
- version 1.0 : Fonctionnalité de base

## Références et apprentissage

```
De nombreux designs d'autres projets exceptionnels ont été utilisés pour référence dans le code, notamment :

# Projet 1 : De nombreuses astuces ont été empruntées à ChuanhuChatGPT
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# Projet 2 : ChatGLM-6B de Tsinghua :
https://github.com/THUDM/ChatGLM-6B
```

