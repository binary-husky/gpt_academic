> **Nota**
>
> Ao instalar as dependências, por favor, selecione rigorosamente as versões **especificadas** no arquivo requirements.txt.
>
> `pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/`
>

# <img src="logo.png" width="40" > Otimização acadêmica GPT (GPT Academic)

**Se você gostou deste projeto, por favor dê um Star. Se você criou atalhos acadêmicos mais úteis ou plugins funcionais, sinta-se livre para abrir uma issue ou pull request. Nós também temos um README em [Inglês|](README_EN.md)[日本語|](README_JP.md)[한국어|](https://github.com/mldljyh/ko_gpt_academic)[Русский|](README_RS.md)[Français](README_FR.md) traduzidos por este próprio projeto.
Para traduzir este projeto para qualquer idioma com o GPT, leia e execute [`multi_language.py`](multi_language.py) (experimental).

> **Nota**
>
> 1. Por favor, preste atenção que somente os plugins de funções (botões) com a cor **vermelha** podem ler arquivos. Alguns plugins estão localizados no **menu suspenso** na área de plugins. Além disso, nós damos as boas-vindas com a **maior prioridade** e gerenciamos quaisquer novos plugins PR!
>
> 2. As funções de cada arquivo neste projeto são detalhadas em [`self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A), auto-análises do projeto geradas pelo GPT também estão podem ser chamadas a qualquer momento ao clicar nos plugins relacionados. As perguntas frequentes estão resumidas no [`wiki`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98). [Instruções de Instalação](#installation).
>
> 3. Este projeto é compatível com e incentiva o uso de modelos de linguagem nacionais, como chatglm e RWKV, Pangolin, etc. Suporta a coexistência de várias chaves de API e pode ser preenchido no arquivo de configuração como `API_KEY="openai-key1,openai-key2,api2d-key3"`. Quando precisar alterar temporariamente o `API_KEY`, basta digitar o `API_KEY` temporário na área de entrada e pressionar Enter para que ele entre em vigor. 

<div align="center">Funcionalidade | Descrição
--- | ---
Um clique de polimento | Suporte a um clique polimento, um clique encontrar erros de gramática no artigo
Tradução chinês-inglês de um clique | Tradução chinês-inglês de um clique
Explicação de código de um único clique | Exibir código, explicar código, gerar código, adicionar comentários ao código
[Teclas de atalho personalizadas](https://www.bilibili.com/video/BV14s4y1E7jN) | Suporte a atalhos personalizados
Projeto modular | Suporte para poderosos plugins[de função personalizada](https://github.com/binary-husky/chatgpt_academic/tree/master/crazy_functions), os plugins suportam[hot-reload](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[Análise automática do programa](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugin de função][um clique para entender](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A) o código-fonte do projeto
[Análise do programa](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugin de função] Um clique pode analisar a árvore de projetos do Python/C/C++/Java/Lua/...
Leitura de artigos, [tradução](https://www.bilibili.com/video/BV1KT411x7Wn) de artigos | [Plugin de função] um clique para interpretar o resumo de artigos LaTeX/PDF e gerar resumo
Tradução completa LATEX, polimento|[Plugin de função] Uma clique para traduzir ou polir um artigo LATEX
Geração em lote de comentários | [Plugin de função] Um clique gera comentários de função em lote
[Tradução chinês-inglês](https://www.bilibili.com/video/BV1yo4y157jV/) markdown | [Plugin de função] Você viu o README em 5 linguagens acima?
Relatório de análise de chat | [Plugin de função] Gera automaticamente um resumo após a execução
[Funcionalidade de tradução de artigos completos em PDF](https://www.bilibili.com/video/BV1KT411x7Wn) | [Plugin de função] Extrai o título e o resumo do artigo PDF e traduz o artigo completo (multithread)
Assistente arXiv | [Plugin de função] Insira o url do artigo arXiv para traduzir o resumo + baixar PDF
Assistente de integração acadêmica do Google | [Plugin de função] Dê qualquer URL de página de pesquisa acadêmica do Google e deixe o GPT escrever[trabalhos relacionados](https://www.bilibili.com/video/BV1GP411U7Az/)
Agregação de informações da Internet + GPT | [Plugin de função] Um clique para obter informações do GPT através da Internet e depois responde a perguntas para informações nunca ficarem desatualizadas
Exibição de fórmulas/imagem/tabela | Pode exibir simultaneamente a forma de renderização e[TEX] das fórmulas, suporte a fórmulas e realce de código
Suporte de plugins de várias linhas | Suporte a várias chamadas em linha do chatgpt, um clique para processamento[de massa de texto](https://www.bilibili.com/video/BV1FT411H7c5/) ou programa
Tema gradio escuro | Adicione ``` /?__theme=dark``` ao final da url do navegador para ativar o tema escuro
[Suporte para vários modelos LLM](https://www.bilibili.com/video/BV1wT411p7yf), suporte para a nova interface API2D | A sensação de ser atendido simultaneamente por GPT3.5, GPT4, [Chatglm THU](https://github.com/THUDM/ChatGLM-6B), [Moss Fudan](https://github.com/OpenLMLab/MOSS) deve ser ótima, certo?
Mais modelos LLM incorporados, suporte para a implantação[huggingface](https://huggingface.co/spaces/qingxu98/gpt-academic) | Adicione interface Newbing (New Bing), suporte [JittorLLMs](https://github.com/Jittor/JittorLLMs) THU Introdução ao suporte do LLaMA, RWKV e Pan Gu Alpha
Mais recursos novos mostrados (geração de imagens, etc.) ... | Consulte o final deste documento ...  

</div>

- Nova interface (Modifique a opção LAYOUT em `config.py` para alternar entre o layout esquerdo/direito e o layout superior/inferior)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230361456-61078362-a966-4eb5-b49e-3c62ef18b860.gif" width="700" >
</div>- All buttons are dynamically generated by reading functional.py, and you can add custom functions at will, liberating the clipboard

<div align="center">
<img src = "https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700">
</div>

- Proofreading/errors correction


<div align="center">
<img src = "https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700">
</div>

- If the output contains formulas, it will be displayed in both tex and rendering format at the same time, which is convenient for copying and reading


<div align="center">
<img src = "https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700">
</div>

- Don't want to read the project code? Just show the whole project to chatgpt


<div align="center">
<img src = "https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700">
</div>

- Mix the use of multiple large language models (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)


<div align="center">
<img src = "https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700">
</div>

---
# Instalação
## Installation-Method 1: Run directly (Windows, Linux or MacOS)

1. Download the project

```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. Configure the API KEY

In `config.py`, configure API KEY and other settings, [Special Network Environment Settings] (https://github.com/binary-husky/gpt_academic/issues/1).

(P.S. When the program runs, it will first check whether there is a private configuration file named `config_private.py`, and use the configuration in it to cover the configuration with the same name in `config.py`. Therefore, if you can understand our configuration reading logic, we strongly recommend that you create a new configuration file named `config_private.py` next to `config.py`, and transfer (copy) the configuration in `config.py` to `config_private.py`. `config_private.py` is not controlled by git and can make your privacy information more secure. P.S. The project also supports configuring most options through `environment variables`. The writing format of environment variables is referenced to the `docker-compose` file. Reading priority: `environment variable` > `config_private.py` > `config.py`)


3. Install dependencies

```sh
# (Option I: for those familiar with python)(python version is 3.9 or above, the newer the better), note: use the official pip source or the Alibaba pip source. Temporary solution for changing source: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Option II: for those who are unfamiliar with python) use anaconda, the steps are also similar (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # create anaconda environment
conda activate gptac_venv                 # activate anaconda environment
python -m pip install -r requirements.txt # This step is the same as the pip installation step
```

<details><summary>If you need to support Tsinghua ChatGLM / Fudan MOSS as the backend, click to expand here</summary>
<p>

[Optional Step] If you need to support Tsinghua ChatGLM / Fudan MOSS as the backend, you need to install more dependencies (prerequisite: familiar with Python + used Pytorch + computer configuration is strong):
```sh
# 【Optional Step I】support Tsinghua ChatGLM。Tsinghua ChatGLM Note: If you encounter a "Call ChatGLM fails cannot load ChatGLM parameters normally" error, refer to the following: 1: The default installed is torch+cpu version, and using cuda requires uninstalling torch and reinstalling torch+cuda; 2: If the model cannot be loaded due to insufficient computer configuration, you can modify the model accuracy in request_llm/bridge_chatglm.py and change AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) to AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llm/requirements_chatglm.txt

# 【Optional Step II】support Fudan MOSS
python -m pip install -r request_llm/requirements_moss.txt
git clone https://github.com/OpenLMLab/MOSS.git request_llm/moss  # Note: When executing this line of code, you must be in the project root path

# 【Optional Step III】Make sure that the AVAIL_LLM_MODELS in the config.py configuration file contains the expected model. Currently, all supported models are as follows (jittorllms series currently only supports docker solutions):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "newbing", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>


4. Run

```sh
python main.py
```5. Plugin de Função de Teste
```
- Função de modelo de plug-in de teste (exige que o GPT responda ao que aconteceu hoje na história), você pode usar esta função como modelo para implementar funções mais complexas
    Clique em "[Função de plug-in de modelo de demonstração] O que aconteceu hoje na história?"
```

## Instalação - Método 2: Usando o Docker

1. Apenas ChatGPT (recomendado para a maioria das pessoas)

``` sh
git clone https://github.com/binary-husky/chatgpt_academic.git  # Baixar o projeto
cd chatgpt_academic                                 # Entrar no caminho
nano config.py                                       # Editar config.py com qualquer editor de texto configurando "Proxy", "API_KEY" e "WEB_PORT" (por exemplo, 50923), etc.
docker build -t gpt-academic .                      # Instale

# (Ùltima etapa - escolha 1) Dentro do ambiente Linux, é mais fácil e rápido usar `--net=host`
docker run --rm -it --net=host gpt-academic
# (Última etapa - escolha 2) Em ambientes macOS/windows, você só pode usar a opção -p para expor a porta do contêiner (por exemplo, 50923) para a porta no host
docker run --rm -it -e WEB_PORT=50923 -p 50923:50923 gpt-academic
```

2. ChatGPT + ChatGLM + MOSS (conhecimento de Docker necessário)

``` sh
# Edite o arquivo docker-compose.yml, remova as soluções 1 e 3, mantenha a solução 2, e siga as instruções nos comentários do arquivo
docker-compose up
```

3. ChatGPT + LLAMA + Pangu + RWKV (conhecimento de Docker necessário)
``` sh
# Edite o arquivo docker-compose.yml, remova as soluções 1 e 2, mantenha a solução 3, e siga as instruções nos comentários do arquivo 
docker-compose up
```


## Instalação - Método 3: Outros Métodos de Implantação

1. Como usar URLs de proxy inverso/microsoft Azure API
Basta configurar o API_URL_REDIRECT de acordo com as instruções em `config.py`.

2. Implantação em servidores em nuvem remotos (requer conhecimento e experiência de servidores em nuvem)
Acesse [Wiki de implementação remota do servidor em nuvem](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)

3. Usando a WSL2 (sub-sistema do Windows para Linux)
Acesse [Wiki da implantação da WSL2](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)

4. Como executar em um subdiretório (ex. `http://localhost/subpath`)
Acesse [Instruções de execução FastAPI](docs/WithFastapi.md)

5. Execute usando o docker-compose
Leia o arquivo docker-compose.yml e siga as instruções.

# Uso Avançado
## Customize novos botões de acesso rápido / plug-ins de função personalizados

1. Personalizar novos botões de acesso rápido (atalhos acadêmicos)
Abra `core_functional.py` em qualquer editor de texto e adicione os seguintes itens e reinicie o programa (Se o botão já foi adicionado e pode ser visto, prefixos e sufixos são compatíveis com modificações em tempo real e não exigem reinício do programa para ter efeito.)
Por exemplo,
```
"Super Eng:": {
  # Prefixo, será adicionado antes da sua entrada. Por exemplo, para descrever sua solicitação, como tradução, explicação de código, polimento, etc.
  "Prefix": "Por favor, traduza o seguinte conteúdo para chinês e use uma tabela em Markdown para explicar termos próprios no texto: \n \n",

  # Sufixo, será adicionado após a sua entrada. Por exemplo, emparelhado com o prefixo, pode colocar sua entrada entre aspas.
  "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

2. Personalizar plug-ins de função

Escreva plug-ins de função poderosos para executar tarefas que você deseja e não pensava possível.
A dificuldade geral de escrever e depurar plug-ins neste projeto é baixa e, se você tem algum conhecimento básico de python, pode implementar suas próprias funções sobre o modelo que fornecemos.
Para mais detalhes, consulte o [Guia do plug-in de função.](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97).

---
# Última atualização
## Novas funções dinâmicas.1. Função de salvamento de diálogo. Ao chamar o plug-in de função "Salvar diálogo atual", é possível salvar o diálogo atual em um arquivo html legível e reversível. Além disso, ao chamar o plug-in de função "Carregar arquivo de histórico de diálogo" no menu suspenso da área de plug-in, é possível restaurar uma conversa anterior. Dica: clicar em "Carregar arquivo de histórico de diálogo" sem especificar um arquivo permite visualizar o cache do arquivo html de histórico. Clicar em "Excluir todo o registro de histórico de diálogo local" permite excluir todo o cache de arquivo html. 
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>


2. Geração de relatório. A maioria dos plug-ins gera um relatório de trabalho após a conclusão da execução.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

3. Design modular de funcionalidades, com interfaces simples, mas suporte a recursos poderosos
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

4. Este é um projeto de código aberto que é capaz de "auto-traduzir-se".
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="500" >
</div>

5. A tradução de outros projetos de código aberto é simples.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="500" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="500" >
</div>

6. Recursos decorativos para o [live2d](https://github.com/fghrsh/live2d_demo) (desativados por padrão, é necessário modificar o arquivo `config.py`)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. Suporte ao modelo de linguagem MOSS
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236639178-92836f37-13af-4fdd-984d-b4450fe30336.png" width="500" >
</div>

8. Geração de imagens pelo OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

9. Análise e resumo de áudio pelo OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

10. Revisão e correção de erros de texto em Latex.
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" width="500" >
</div>

## Versão:
- Versão 3.5(Todo): Usar linguagem natural para chamar todas as funções do projeto (prioridade alta)
- Versão 3.4(Todo): Melhorar o suporte à multithread para o chatglm local
- Versão 3.3: +Funções integradas de internet
- Versão 3.2: Suporte a mais interfaces de parâmetros de plug-in (função de salvar diálogo, interpretação de códigos de várias linguagens, perguntas de combinações LLM arbitrárias ao mesmo tempo)
- Versão 3.1: Suporte a perguntas a vários modelos de gpt simultaneamente! Suporte para api2d e balanceamento de carga para várias chaves api
- Versão 3.0: Suporte ao chatglm e outros LLMs de pequeno porte
- Versão 2.6: Refatoração da estrutura de plug-in, melhoria da interatividade e adição de mais plug-ins
- Versão 2.5: Autoatualização, resolvendo problemas de token de texto excessivamente longo e estouro ao compilar grandes projetos
- Versão 2.4: (1) Adição de funcionalidade de tradução de texto completo em PDF; (2) Adição de funcionalidade de mudança de posição da área de entrada; (3) Adição de opção de layout vertical; (4) Otimização de plug-ins de multithread.
- Versão 2.3: Melhoria da interatividade de multithread
- Versão 2.2: Suporte à recarga a quente de plug-ins
- Versão 2.1: Layout dobrável
- Versão 2.0: Introdução de plug-ins de função modular
- Versão 1.0: Funcionalidades básicasgpt_academic desenvolvedores QQ grupo-2: 610599535

- Problemas conhecidos
    - Extensões de tradução de alguns navegadores podem interferir na execução do front-end deste software
    - Uma versão muito alta ou muito baixa do Gradio pode causar vários erros

## Referências e Aprendizado

```
Foi feita referência a muitos projetos excelentes em código, principalmente:

# Projeto1: ChatGLM-6B da Tsinghua:
https://github.com/THUDM/ChatGLM-6B

# Projeto2: JittorLLMs da Tsinghua:
https://github.com/Jittor/JittorLLMs

# Projeto3: Edge-GPT:
https://github.com/acheong08/EdgeGPT

# Projeto4: ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# Projeto5: ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Mais:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
```