


> **Nota**
>
> Este README foi traduzido pelo GPT (implementado por um plugin deste projeto) e não é 100% confiável. Por favor, verifique cuidadosamente o resultado da tradução.
>
> 7 de novembro de 2023: Ao instalar as dependências, favor selecionar as **versões especificadas** no `requirements.txt`. Comando de instalação: `pip install -r requirements.txt`.

# <div align=center><img src="logo.png" width="40"> GPT Acadêmico</div>

**Se você gosta deste projeto, por favor, dê uma estrela nele. Se você inventou atalhos de teclado ou plugins úteis, fique à vontade para criar pull requests!**
Para traduzir este projeto para qualquer idioma utilizando o GPT, leia e execute [`multi_language.py`](multi_language.py) (experimental).

> **Nota**
>
> 1. Observe que apenas os plugins (botões) marcados em **destaque** são capazes de ler arquivos, alguns plugins estão localizados no **menu suspenso** do plugin area. Também damos boas-vindas e prioridade máxima a qualquer novo plugin via PR.
>
> 2. As funcionalidades de cada arquivo deste projeto estão detalhadamente explicadas em [autoanálise `self_analysis.md`](https://github.com/binary-husky/gpt_academic/wiki/GPT‐Academic项目自译解报告). Com a iteração das versões, você também pode clicar nos plugins de funções relevantes a qualquer momento para chamar o GPT para regerar o relatório de autonálise do projeto. Perguntas frequentes [`wiki`](https://github.com/binary-husky/gpt_academic/wiki) | [Método de instalação convencional](#installation) | [Script de instalação em um clique](https://github.com/binary-husky/gpt_academic/releases) | [Explicação de configuração](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明)。
>
> 3. Este projeto é compatível e encoraja o uso de modelos de linguagem chineses, como ChatGLM. Vários api-keys podem ser usados simultaneamente, podendo ser especificados no arquivo de configuração como `API_KEY="openai-key1,openai-key2,azure-key3,api2d-key4"`. Quando precisar alterar temporariamente o `API_KEY`, insira o `API_KEY` temporário na área de entrada e pressione Enter para que ele seja efetivo.


<div align="center">

Funcionalidades (⭐= funcionalidade recentemente adicionada) | Descrição
--- | ---
⭐[Integração com novos modelos](https://github.com/binary-husky/gpt_academic/wiki/%E5%A6%82%E4%BD%95%E5%88%87%E6%8D%A2%E6%A8%A1%E5%9E%8B)！ | [Qianfan](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Nlks5zkzu) da Baidu, Wenxin e [Tongyi Qianwen](https://modelscope.cn/models/qwen/Qwen-7B-Chat/summary), [Shusheng](https://github.com/InternLM/InternLM) da Shanghai AI-Lab, [Xinghuo](https://xinghuo.xfyun.cn/) da Iflytek, [LLaMa2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf), Zhipu API, DALLE3
Aprimoramento, tradução, explicação de códigos | Aprimoramento com um clique, tradução, busca de erros gramaticais em artigos e explicação de códigos
[Atalhos de teclado personalizados](https://www.bilibili.com/video/BV14s4y1E7jN) | Suporte para atalhos de teclado personalizados
Design modular | Suporte a plugins poderosos e personalizáveis, plugins com suporte a [atualização a quente](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[Análise de código](https://www.bilibili.com/video/BV1cj411A7VW) | [Plugin] Análise instantânea da estrutura de projetos em Python/C/C++/Java/Lua/... ou [autoanálise](https://www.bilibili.com/video/BV1cj411A7VW)
Leitura de artigos, [tradução](https://www.bilibili.com/video/BV1KT411x7Wn) de artigos | [Plugin] Interpretação instantânea de artigos completos em latex/pdf e geração de resumos
Tradução completa de artigos em latex [PDF](https://www.bilibili.com/video/BV1nk4y1Y7Js/), [aprimoramento](https://www.bilibili.com/video/BV1FT411H7c5/) | [Plugin] Tradução completa ou aprimoramento de artigos em latex com um clique
Geração em lote de comentários | [Plugin] Geração em lote de comentários de funções com um clique
Tradução (inglês-chinês) de Markdown | [Plugin] Você já viu o [README](https://github.com/binary-husky/gpt_academic/blob/master/docs/README_EN.md) nas 5 línguas acima?
Criação de relatório de análise de bate-papo | [Plugin] Geração automática de relatório de resumo após a execução
Tradução [completa de artigos em PDF](https://www.bilibili.com/video/BV1KT411x7Wn) | [Plugin] Extração de título e resumo de artigos em PDF + tradução completa (multithreading)
Auxiliar Arxiv | [Plugin] Insira o URL de um artigo Arxiv para traduzir o resumo + baixar o PDF com um clique
Correção automática de artigos em latex | [Plugin] Correções gramaticais e ortográficas de artigos em latex semelhante ao Grammarly + saída PDF comparativo
Auxiliar Google Scholar | [Plugin] Insira qualquer URL da busca do Google Acadêmico e deixe o GPT [escrever trabalhos relacionados](https://www.bilibili.com/video/BV1GP411U7Az/) para você
Agregação de informações da Internet + GPT | [Plugin] Capturar informações da Internet e obter respostas de perguntas com o GPT em um clique, para que as informações nunca fiquem desatualizadas
⭐Tradução refinada de artigos do Arxiv ([Docker](https://github.com/binary-husky/gpt_academic/pkgs/container/gpt_academic_with_latex)) | [Plugin] Tradução de alta qualidade de artigos do Arxiv com um clique, a melhor ferramenta de tradução de artigos atualmente
⭐Entrada de conversa de voz em tempo real | [Plugin] Monitoramento de áudio [assíncrono](https://www.bilibili.com/video/BV1AV4y187Uy/), segmentação automática de frases, detecção automática de momentos de resposta
Exibição de fórmulas, imagens e tabelas | Exibição de fórmulas em formato tex e renderizadas simultaneamente, suporte a fórmulas e destaque de código
⭐Plugin AutoGen para vários agentes | [Plugin] Explore a emergência de múltiplos agentes com o AutoGen da Microsoft!
Ativar o tema escuro | Adicione ```/?__theme=dark``` ao final da URL para alternar para o tema escuro
Suporte a múltiplos modelos LLM | Ser atendido simultaneamente pelo GPT3.5, GPT4, [ChatGLM2](https://github.com/THUDM/ChatGLM2-6B) do Tsinghua University e [MOSS](https://github.com/OpenLMLab/MOSS) da Fudan University se sente incrível, não é mesmo?
⭐Modelo de ajuste fino ChatGLM2 | Suporte para carregar o modelo ChatGLM2 ajustado e fornecer plugins de assistência ao ajuste fino do ChatGLM2
Mais modelos LLM e suporte para [implantação pela HuggingFace](https://huggingface.co/spaces/qingxu98/gpt-academic) | Integração com a interface Newbing (Bing novo), introdução do [Jittorllms](https://github.com/Jittor/JittorLLMs) da Tsinghua University com suporte a [LLaMA](https://github.com/facebookresearch/llama) e [Panguα](https://openi.org.cn/pangu/)
⭐Pacote pip [void-terminal](https://github.com/binary-husky/void-terminal) | Chame todas as funções plugins deste projeto diretamente em Python, sem a GUI (em desenvolvimento)
⭐Plugin Terminal do Vácuo | [Plugin] Chame outros plugins deste projeto diretamente usando linguagem natural
Apresentação de mais novas funcionalidades (geração de imagens, etc.) ... | Veja no final deste documento ...

</div>


- Nova interface (altere a opção LAYOUT em `config.py` para alternar entre os "Layouts de lado a lado" e "Layout de cima para baixo")
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/d81137c3-affd-4cd1-bb5e-b15610389762" width="700" >
</div>


- Todos os botões são gerados dinamicamente através da leitura do `functional.py`, você pode adicionar funcionalidades personalizadas à vontade, liberando sua área de transferência
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- Aprimoramento/Correção
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>



- Se a saída contiver fórmulas, elas serão exibidas tanto em formato tex quanto renderizado para facilitar a cópia e a leitura.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- Não tem vontade de ver o código do projeto? O projeto inteiro está diretamente na boca do chatgpt.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- Combinação de vários modelos de linguagem (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

# Instalação
### Método de instalação I: Executar diretamente (Windows, Linux ou MacOS)

1. Baixe o projeto
```sh
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git
cd gpt_academic
```

2. Configure a API_KEY

No arquivo `config.py`, configure a API KEY e outras configurações. [Clique aqui para ver o método de configuração em redes especiais](https://github.com/binary-husky/gpt_academic/issues/1). [Página Wiki](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明).

「 O programa verificará primeiro se existe um arquivo de configuração privada chamado `config_private.py` e substituirá as configurações correspondentes no arquivo `config.py`. Se você entender essa lógica de leitura, é altamente recomendável criar um novo arquivo de configuração chamado `config_private.py` ao lado do `config.py` e copiar as configurações do `config.py` para o `config_private.py` (copiando apenas os itens de configuração que você modificou). 」

「 Suporte para configurar o projeto por meio de `variáveis de ambiente`, o formato de gravação das variáveis de ambiente pode ser encontrado no arquivo `docker-compose.yml` ou em nossa [página Wiki](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明). A prioridade de leitura das configurações é: `variáveis de ambiente` > `config_private.py` > `config.py`. 」


3. Instale as dependências
```sh
# (Opção I: Se você está familiarizado com o Python, Python>=3.9) Observação: Use o pip oficial ou o pip da Aliyun. Método temporário para alternar fontes: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (Opção II: Use o Anaconda) Os passos também são semelhantes (https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # Crie um ambiente do Anaconda
conda activate gptac_venv                 # Ative o ambiente do Anaconda
python -m pip install -r requirements.txt # Este passo é igual ao da instalação do pip
```


<details><summary>Se você quiser suporte para o ChatGLM2 do THU/ MOSS do Fudan/RWKV como backend, clique para expandir</summary>
<p>

[Opcional] Se você quiser suporte para o ChatGLM2 do THU/ MOSS do Fudan, precisará instalar dependências extras (pré-requisitos: familiarizado com o Python + já usou o PyTorch + o computador tem configuração suficiente):
```sh
# [Opcional Passo I] Suporte para ChatGLM2 do THU. Observações sobre o ChatGLM2 do THU: Se você encontrar o erro "Call ChatGLM fail 不能正常加载ChatGLM的参数" (Falha ao chamar o ChatGLM, não é possível carregar os parâmetros do ChatGLM), consulte o seguinte: 1: A versão instalada por padrão é a versão torch+cpu. Se você quiser usar a versão cuda, desinstale o torch e reinstale uma versão com torch+cuda; 2: Se a sua configuração não for suficiente para carregar o modelo, você pode modificar a precisão do modelo em request_llm/bridge_chatglm.py, alterando todas as ocorrências de AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True) para AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)
python -m pip install -r request_llms/requirements_chatglm.txt

# [Opcional Passo II] Suporte para MOSS do Fudan
python -m pip install -r request_llms/requirements_moss.txt
git clone --depth=1 https://github.com/OpenLMLab/MOSS.git request_llms/moss  # Observe que você deve estar no diretório raiz do projeto ao executar este comando

# [Opcional Passo III] Suporte para RWKV Runner
Consulte a página Wiki: https://github.com/binary-husky/gpt_academic/wiki/%E9%80%82%E9%85%8DRWKV-Runner

# [Opcional Passo IV] Verifique se o arquivo de configuração config.py contém os modelos desejados, os modelos compatíveis são os seguintes (a série jittorllms suporta apenas a solução Docker):
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. Execute
```sh
python main.py
```

### Método de instalação II: Usando o Docker

0. Implante todas as capacidades do projeto (este é um contêiner grande que inclui CUDA e LaTeX. Não recomendado se você tiver uma conexão lenta com a internet ou pouco espaço em disco)
[![fullcapacity](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml)

``` sh
# Modifique o arquivo docker-compose.yml para incluir apenas a seção 0 e excluir as outras seções. Em seguida, execute:
docker-compose up
```

1. ChatGPT + 文心一言 + spark + outros modelos online (recomendado para a maioria dos usuários)
[![basic](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml)
[![basiclatex](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml)
[![basicaudio](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml)

``` sh
# Modifique o arquivo docker-compose.yml para incluir apenas a seção 1 e excluir as outras seções. Em seguida, execute:
docker-compose up
```

Obs.: Se você precisar do plugin Latex, consulte a Wiki. Além disso, você também pode usar a seção 4 ou 0 para obter a funcionalidade do LaTeX.

2. ChatGPT + ChatGLM2 + MOSS + LLAMA2 + 通义千问 (você precisa estar familiarizado com o [Nvidia Docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#installing-on-ubuntu-and-debian) para executar este modo)
[![chatglm](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml)

``` sh
# Modifique o arquivo docker-compose.yml para incluir apenas a seção 2 e excluir as outras seções. Em seguida, execute:
docker-compose up
```


### Método de instalação III: Outros métodos de implantação
1. **Script de execução com um clique para Windows**.
Usuários do Windows que não estão familiarizados com o ambiente Python podem baixar o script de execução com um clique da [Release](https://github.com/binary-husky/gpt_academic/releases) para instalar a versão sem modelos locais.
A contribuição do script vem de [oobabooga](https://github.com/oobabooga/one-click-installers).

2. Usar APIs de terceiros, Azure, etc., 文心一言, 星火, consulte a [página Wiki](https://github.com/binary-husky/gpt_academic/wiki/项目配置说明).

3. Guia para evitar armadilhas na implantação em servidor em nuvem.
Consulte o [wiki de implantação em servidor em nuvem](https://github.com/binary-husky/gpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97).

4. Algumas novas plataformas ou métodos de implantação
    - Use Sealos [implantação com um clique](https://github.com/binary-husky/gpt_academic/issues/993).
    - Use o WSL2 (Subsistema do Windows para Linux). Consulte [wiki de implantação](https://github.com/binary-husky/gpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2).
    - Como executar em um subdiretório da URL (como `http://localhost/subpath`). Consulte [instruções de execução com o FastAPI](docs/WithFastapi.md)



# Uso Avançado
### I: Personalização de Novos Botões de Atalho (Atalhos Acadêmicos)
Abra o arquivo `core_functional.py` em qualquer editor de texto, adicione o seguinte item e reinicie o programa. (Se o botão já existir, o prefixo e o sufixo podem ser modificados a qualquer momento sem reiniciar o programa).
Por exemplo:
```
"超级英译中": {
    # Prefixo, adicionado antes do seu input. Por exemplo, usado para descrever sua solicitação, como traduzir, explicar o código, revisar, etc.
    "Prefix": "Por favor, traduza o parágrafo abaixo para o chinês e explique cada termo técnico dentro de uma tabela markdown:\n\n",

    # Sufixo, adicionado após o seu input. Por exemplo, em conjunto com o prefixo, pode-se colocar seu input entre aspas.
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

### II: Personalização de Funções Plugins
Crie poderosos plugins de função para executar tarefas que você pode e não pode imaginar.
Criar plugins neste projeto é fácil, basta seguir o modelo fornecido, desde que você tenha conhecimento básico de Python.
Consulte o [Guia dos Plugins de Função](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97) para mais detalhes.


# Atualizações
### I: Dinâmico

1. Função de salvar conversas. Chame a função "Salvar a conversa atual" na área de plugins para salvar a conversa atual em um arquivo HTML legível e recuperável. Além disso, chame a função "Carregar histórico de conversas" na área de plugins (menu suspenso) para restaurar conversas anteriores.
Dica: Se você clicar diretamente em "Carregar histórico de conversas" sem especificar o arquivo, poderá visualizar o cache do histórico do arquivo HTML.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. ⭐Tradução de artigos Latex/Arxiv⭐
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/002a1a75-ace0-4e6a-94e2-ec1406a746f1" height="250" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/9fdcc391-f823-464f-9322-f8719677043b" height="250" >
</div>

3. Terminal vazio (entendendo a intenção do usuário a partir do texto em linguagem natural e chamando automaticamente outros plugins)

- Passo 1: Digite "Por favor, chame o plugin 'Traduzir artigo PDF' e forneça o link https://openreview.net/pdf?id=rJl0r3R9KX"
- Passo 2: Clique em "Terminal vazio"

<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/66f1b044-e9ff-4eed-9126-5d4f3668f1ed" width="500" >
</div>

4. Design de recursos modular, interface simples com suporte a recursos poderosos
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

5. Tradução e interpretação de outros projetos de código aberto
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" height="250" >
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" height="250" >
</div>

6. Recursos adicionais para [live2d](https://github.com/fghrsh/live2d_demo) (desativados por padrão, requer modificação no arquivo `config.py`)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. Geração de imagens pela OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

8. Análise e resumo de áudio pela OpenAI
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

9. Correção de erros em texto e código LaTeX
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" height="200" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/476f66d9-7716-4537-b5c1-735372c25adb" height="200">
</div>

10. Alternância de idioma e tema
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/b6799499-b6fb-4f0c-9c8e-1b441872f4e8" width="500" >
</div>



### II: Versões:
- Versão 3.70 (a fazer): Melhorar o plugin AutoGen e projetar uma série de plugins relacionados.
- Versão 3.60: Introdução do AutoGen como base para a próxima geração de plugins.
- Versão 3.57: Suporte para GLM3, Starfire v3, Wenxin Yiyan v4, correção de bugs relacionados a modelos locais executados simultaneamente.
- Versão 3.56: Suporte para adicionar dinamicamente botões de função básicos e nova página de resumo em PDF.
- Versão 3.55: Reformulação da interface do usuário, introdução de janelas flutuantes e menus.
- Versão 3.54: Novo interpretador de código dinâmico (Code Interpreter) (em desenvolvimento)
- Versão 3.53: Suporte para alterar dinamicamente o tema da interface, melhorias de estabilidade e correção de conflitos entre vários usuários.
- Versão 3.50: Chamada de todas as funções de plugins deste projeto usando linguagem natural (Terminal vazio), suporte a categorização de plugins, melhorias na interface do usuário e design de novos temas.
- Versão 3.49: Suporte para Baidu Qianfan Platform e Wenxin Yiyan.
- Versão 3.48: Suporte para Alibaba DAMO Academy Tongyi Qianwen, Shanghai AI-Lab Shusheng e Xunfei Xinghuo.
- Versão 3.46: Suporte para diálogos em tempo real totalmente automáticos.
- Versão 3.45: Suporte para personalização do modelo ChatGLM2.
- Versão 3.44: Suporte oficial ao Azure, aprimoramentos na usabilidade da interface.
- Versão 3.4: Tradução completa de artigos Arxiv/Latex, correção de artigos Latex.
- Versão 3.3: Funcionalidade de consulta a informações na internet.
- Versão 3.2: Maior suporte para parâmetros de função de plugins (função de salvar conversas, interpretação de código em qualquer linguagem + perguntas sobre combinações LLM arbitrariamente).
- Versão 3.1: Suporte para fazer perguntas a modelos GPT múltiplos! Suporte para API2D, balanceamento de carga em vários APIKeys.
- Versão 3.0: Suporte para chatglm e outros pequenos modelos LLM.
- Versão 2.6: Refatoração da estrutura de plugins, melhoria na interação, adição de mais plugins.
- Versão 2.5: Auto-atualizável, resolve problemas de texto muito longo ou estouro de tokens ao resumir grandes projetos de código.
- Versão 2.4: (1) Novo recurso de tradução completa de PDF; (2) Nova função para alternar a posição da área de input; (3) Nova opção de layout vertical; (4) Melhoria dos plugins de função em várias threads.
- Versão 2.3: Melhorias na interação em várias threads.
- Versão 2.2: Suporte para recarregar plugins sem reiniciar o programa.
- Versão 2.1: Layout dobrável.
- Versão 2.0: Introdução de plugins de função modular.
- Versão 1.0: Funcionalidades básicas.

GPT Academic QQ Group: `610599535`

- Problemas conhecidos
    - Alguns plugins de tradução de navegadores podem interferir na execução deste software.
    - A biblioteca Gradio possui alguns bugs de compatibilidade conhecidos. Certifique-se de instalar o Gradio usando o arquivo `requirement.txt`.

### III: Temas
Você pode alterar o tema atualizando a opção `THEME` (config.py).
1. `Chuanhu-Small-and-Beautiful` [Link](https://github.com/GaiZhenbiao/ChuanhuChatGPT/)


### IV: Branches de Desenvolvimento deste Projeto

1. Branch `master`: Branch principal, versão estável.
2. Branch `frontier`: Branch de desenvolvimento, versão de teste.


### V: Referências para Aprendizado

```
O código referenciou muitos projetos excelentes, em ordem aleatória:

# Tsinghua ChatGLM2-6B:
https://github.com/THUDM/ChatGLM2-6B

# Tsinghua JittorLLMs:
https://github.com/Jittor/JittorLLMs

# ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Edge-GPT:
https://github.com/acheong08/EdgeGPT

# ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT



# Oobabooga instalador com um clique:
https://github.com/oobabooga/instaladores-de-um-clique

# Mais:
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
