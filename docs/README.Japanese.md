


> **注意**
>
> 此READMEはGPTによる翻訳で生成されました（このプロジェクトのプラグインによって実装されています）、翻訳結果は100%正確ではないため、注意してください。
>
> 2023年11月7日: 依存関係をインストールする際は、`requirements.txt`で**指定されたバージョン**を選択してください。 インストールコマンド: `pip install -r requirements.txt`。


# <div align=center><img src="logo.png" width="40"> GPT 学術最適化 (GPT Academic)</div>

**このプロジェクトが気に入った場合は、Starを付けてください。また、便利なショートカットキーまたはプラグインを作成した場合は、プルリクエストを歓迎します！**
GPTを使用してこのプロジェクトを任意の言語に翻訳するには、[`multi_language.py`](multi_language.py)を読み込んで実行します（実験的な機能）。

> **注意**
>
> 1. **強調された** プラグイン（ボタン）のみがファイルを読み込むことができることに注意してください。一部のプラグインは、プラグインエリアのドロップダウンメニューにあります。また、新しいプラグインのPRを歓迎し、最優先で対応します。
>
> 2. このプロジェクトの各ファイルの機能は、[自己分析レポート`self_analysis.md`](https://github.com/binary-husky/gpt_academic/wiki/GPT‐Academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E5%A0%82)で詳しく説明されています。バージョンが進化するにつれて、関連する関数プラグインをクリックして、プロジェクトの自己分析レポートをGPTで再生成することもできます。よくある質問については、[`wiki`](https://github.com/binary-husky/gpt_academic/wiki)をご覧ください。[標準的なインストール方法](#installation) | [ワンクリックインストールスクリプト](https://github.com/binary-husky/gpt_academic/releases) | [構成の説明](https://github.com/binary-husky/gpt_academic/wiki/Project-Configuration-Explain)。
>
> 3. このプロジェクトは、[ChatGLM](https://www.chatglm.dev/)などの中国製の大規模言語モデルも互換性があり、試してみることを推奨しています。複数のAPIキーを共存させることができ、設定ファイルに`API_KEY="openai-key1,openai-key2,azure-key3,api2d-key4"`のように記入できます。`API_KEY`を一時的に変更する必要がある場合は、入力エリアに一時的な`API_KEY`を入力し、Enterキーを押して提出すると有効になります。




<div align="center">

機能（⭐= 最近追加された機能） | 説明
--- | ---
⭐[新しいモデルの追加](https://github.com/binary-husky/gpt_academic/wiki/%E5%A6%82%E4%BD%95%E5%88%87%E6%8D%A2%E6%A8%A1%E5%9E%8B)！ | Baidu [Qianfan](https://cloud.baidu.com/doc/WENXINWORKSHOP/s/Nlks5zkzu)とWenxin Yiyu, [Tongyi Qianwen](https://modelscope.cn/models/qwen/Qwen-7B-Chat/summary), Shanghai AI-Lab [Shusheng](https://github.com/InternLM/InternLM), Xunfei [Xinghuo](https://xinghuo.xfyun.cn/), [LLaMa2](https://huggingface.co/meta-llama/Llama-2-7b-chat-hf), Zhantu API, DALLE3
校正、翻訳、コード解説 | 一括校正、翻訳、論文の文法エラーの検索、コードの解説
[カスタムショートカットキー](https://www.bilibili.com/video/BV14s4y1E7jN) | カスタムショートカットキーのサポート
モジュール化された設計 | カスタムでパワフルな[プラグイン](https://github.com/binary-husky/gpt_academic/tree/master/crazy_functions)のサポート、プラグインの[ホットリロード](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[プログラム解析](https://www.bilibili.com/video/BV1cj411A7VW) | [プラグイン] Python/C/C++/Java/Lua/...のプロジェクトツリーを簡単に解析するか、[自己解析](https://www.bilibili.com/video/BV1cj411A7VW)
論文の読み込み、[翻訳](https://www.bilibili.com/video/BV1KT411x7Wn) | [プラグイン] LaTeX/PDFの論文全文を翻訳して要約を作成する
LaTeX全文の[翻訳](https://www.bilibili.com/video/BV1nk4y1Y7Js/)、[校正](https://www.bilibili.com/video/BV1FT411H7c5/) | [プラグイン] LaTeX論文を翻訳や校正する
一括コメント生成 | [プラグイン] 関数コメントを一括生成する
Markdownの[日英翻訳](https://www.bilibili.com/video/BV1yo4y157jV/) | [プラグイン] 5つの言語（[英語](https://github.com/binary-husky/gpt_academic/blob/master/docs/README_EN.md)など）のREADMEをご覧になりましたか？
チャット分析レポートの生成 | [プラグイン] 実行後にサマリーレポートを自動生成する
[PDF論文全文の翻訳機能](https://www.bilibili.com/video/BV1KT411x7Wn) | [プラグイン] PDF論文のタイトルと要約を抽出し、全文を翻訳する（マルチスレッド）
[Arxivアシスタント](https://www.bilibili.com/video/BV1LM4y1279X) | [プラグイン] arxiv論文のURLを入力すると、要約を翻訳してPDFをダウンロードできます
LaTeX論文の一括校正 | [プラグイン] Grammarlyのように、LaTeX論文の文法とスペルを修正して対照PDFを出力する
[Google Scholar統合アシスタント](https://www.bilibili.com/video/BV19L411U7ia) | [プラグイン] 任意のGoogle Scholar検索ページのURLを指定して、関連資料をGPTに書かせることができます
インターネット情報の集約+GPT | [プラグイン] インターネットから情報を取得して質問に答え、情報が常に最新になるようにします
⭐Arxiv論文の詳細な翻訳 ([Docker](https://github.com/binary-husky/gpt_academic/pkgs/container/gpt_academic_with_latex)) | [プラグイン] arxiv論文を超高品質で翻訳します。最高の論文翻訳ツールです
⭐[リアルタイム音声入力](https://github.com/binary-husky/gpt_academic/blob/master/docs/use_audio.md) | [プラグイン] 非同期[音声をリッスン(https://www.bilibili.com/video/BV1AV4y187Uy/)し、自動で文章を区切り、回答のタイミングを自動で探します
公式/画像/表の表示 | 公式の[tex形式とレンダリング形式](https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png)を同時に表示し、公式とコードのハイライトをサポートします
⭐AutoGenマルチエージェントプラグイン | [プラグイン] Microsoft AutoGenを利用して、マルチエージェントのインテリジェントなエマージェンスを探索します
ダーク[テーマ](https://github.com/binary-husky/gpt_academic/issues/173)を起動 | ブラウザのURLに```/?__theme=dark```を追加すると、ダークテーマに切り替えられます
[複数のLLMモデル](https://www.bilibili.com/video/BV1wT411p7yf)のサポート | GPT3.5、GPT4、[Tsinghua ChatGLM2](https://github.com/THUDM/ChatGLM2-6B)、[Fudan MOSS](https://github.com/OpenLMLab/MOSS)などを同時に使えるのは最高の感じですよね？
⭐ChatGLM2ファインチューニングモデル | ChatGLM2ファインチューニングモデルをロードして使用することができ、ChatGLM2ファインチューニングの補助プラグインが用意されています
さらなるLLMモデルの導入、[HuggingFaceデプロイのサポート](https://huggingface.co/spaces/qingxu98/gpt-academic) | Newbingインターフェース（新しいBing）の追加、Tsinghua [Jittorllms](https://github.com/Jittor/JittorLLMs)の導入、[LLaMA](https://github.com/facebookresearch/llama)および[盤古α](https://openi.org.cn/pangu/)のサポート
⭐[void-terminal](https://github.com/binary-husky/void-terminal) pipパッケージ | GUIから独立して、Pythonから直接このプロジェクトのすべての関数プラグインを呼び出せます（開発中）
⭐Void Terminalプラグイン | [プラグイン] 自然言語で、このプロジェクトの他のプラグインを直接実行します
その他の新機能の紹介（画像生成など）...... | 末尾をご覧ください ......
</div>



- もし出力に数式が含まれている場合、TeX形式とレンダリング形式の両方で表示されます。これにより、コピーと読み取りが容易になります。

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- プロジェクトのコードを見るのがめんどくさい？プロジェクト全体を`chatgpt`に広報口頭発表してもらえるよ

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- 異なる言語モデルの組み合わせ呼び出し（ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4）

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

# インストール
### 方法I：直接実行（Windows、Linux、またはMacOS）

1. プロジェクトをダウンロード
```sh
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git
cd gpt_academic
```

2. APIキーを設定する

`config.py`でAPIキーやその他の設定を設定します。特殊なネットワーク環境の設定方法については、[こちらをクリックして確認してください](https://github.com/binary-husky/gpt_academic/issues/1)。[Wikiページ](https://github.com/binary-husky/gpt_academic/wiki/Getting-Started)も参照してください。

「プログラムは、`config.py`と同じ場所にある`config_private.py`という名前のプライベート設定ファイルが存在するかどうかを優先的にチェックし、同じ名前の設定をコピーします。この読み込みロジックを理解できる場合、`config.py`の横に`config_private.py`という名前の新しい設定ファイルを作成し、`config.py`の設定を転送（コピー）することを強くお勧めします（変更した設定項目だけをコピーします）。」

「プロジェクトを環境変数で設定することもサポートしています。環境変数の書式は、`docker-compose.yml`ファイルや[Wikiページ](https://github.com/binary-husky/gpt_academic/wiki/Getting-Started)を参考にしてください。設定の優先度は、`環境変数` > `config_private.py` > `config.py`の順です。」

3. 依存関係をインストールする
```sh
# （オプションI：Pythonに詳しい場合、Python 3.9以上）注：公式のpipソースまたは阿里pipソースを使用し、一時的なソースの変更方法は、python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/です。
python -m pip install -r requirements.txt

# （オプションII：Anacondaを使用する場合）手順は同様です (https://www.bilibili.com/video/BV1rc411W7Dr)：
conda create -n gptac_venv python=3.11    # Anaconda環境を作成
conda activate gptac_venv                 # Anaconda環境をアクティベート
python -m pip install -r requirements.txt # この手順はpipのインストール手順と同じです
```

<details><summary>清華ChatGLM2/復旦MOSS/RWKVがバックエンドとしてサポートされている場合、ここをクリックして展開してください</summary>
<p>

【オプションステップ】 清華ChatGLM2/復旦MOSSをバックエンドとしてサポートする場合は、さらに追加の依存関係をインストールする必要があります（前提条件：Pythonに精通していて、PytorchとNVIDIA GPUを使用したことがあり、十分なコンピュータの構成を持っていること）：

```sh
# 【オプションステップI】 清華ChatGLM2のサポートを追加する。 清華ChatGLM2に関する注意点： "Call ChatGLM fail 不能正常加载ChatGLM的参数" のエラーが発生した場合、次の手順を参照してください。 1: デフォルトでインストールされているのはtorch+cpu版です。CUDAを使用するにはtorchをアンインストールしてtorch+cuda版を再インストールする必要があります。 2: モデルをロードできない場合は、request_llm/bridge_chatglm.pyのモデル精度を変更できます。AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)をAutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)に変更します。
python -m pip install -r request_llms/requirements_chatglm.txt

# 【オプションステップII】 復旦MOSSのサポートを追加する
python -m pip install -r request_llms/requirements_moss.txt
git clone --depth=1 https://github.com/OpenLMLab/MOSS.git request_llms/moss  # このコマンドを実行するときは、プロジェクトのルートパスである必要があります。

# 【オプションステップIII】 RWKV Runnerのサポートを追加する
Wikiを参照してください: https://github.com/binary-husky/gpt_academic/wiki/%E9%80%82%E9%85%8DRWKV-Runner

# 【オプションステップIV】 config.py設定ファイルに、以下のすべてのモデルが含まれていることを確認します。以下のモデルがすべてサポートされています（jittorllmsはDockerのみサポートされています）：
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>

4. 実行する
```sh
python main.py
```

### 方法II：Dockerを使用する

0. プロジェクトのフルスケールデプロイ（これは、CUDAとLaTeXを含む大規模なイメージですが、ネットワーク速度が遅いまたはディスク容量が小さい場合はおすすめしません）
[![fullcapacity](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-all-capacity.yml)

```sh
# docker-compose.ymlを編集し、スキーム0を残し、その他を削除してから実行する：
docker-compose up
```

1. ChatGPT + 文心一言 + sparkなどのオンラインモデルのみを含む（ほとんどの人におすすめ）
[![basic](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-without-local-llms.yml)
[![basiclatex](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-latex.yml)
[![basicaudio](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-audio-assistant.yml)

```sh
# docker-compose.ymlを編集し、スキーム1を残し、その他を削除してから実行する：
docker-compose up
```

P.S. LaTeXプラグインの機能を使用する場合は、Wikiを参照してください。また、LaTeX機能を使用するためには、スキーム4またはスキーム0を直接使用することもできます。

2. ChatGPT + ChatGLM2 + MOSS + LLAMA2 + 通慧千問（Nvidia Dockerに精通している場合）
[![chatglm](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml/badge.svg?branch=master)](https://github.com/binary-husky/gpt_academic/actions/workflows/build-with-chatglm.yml)

```sh
# docker-compose.ymlを編集し、スキーム2を残し、その他を削除してから実行する：
docker-compose up
```


### 方法III：その他のデプロイメントオプション

1. **Windowsのワンクリック実行スクリプト**。
Python環境に詳しくないWindowsユーザーは、[リリース](https://github.com/binary-husky/gpt_academic/releases)からワンクリック実行スクリプトをダウンロードして、ローカルモデルのないバージョンをインストールできます。
スクリプトの貢献者は[oobabooga](https://github.com/oobabooga/one-click-installers)です。

2. 第三者のAPI、Azureなど、文心一言、星火などを使用するには、[Wikiページ](https://github.com/binary-husky/gpt_academic/wiki/Getting-Started)を参照してください。

3. クラウドサーバーでのリモートデプロイの回避策ガイドを参照してください。
[クラウドサーバーでのリモートデプロイの回避策ガイドwiki](https://github.com/binary-husky/gpt_academic/wiki/Getting-Started#%E4%BA%91%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC%E3%83%AA%E3%82%BC%E3%83%A0%E3%82%B5%E3%83%BC%E3%83%90%E3%81%AE%E3%83%AA%E3%83%A2%E3%83%BC%E3%83%88%E3%83%87%E3%83%97%E3%83%AD%E3%82%A4%E6%8C%87%E5%8D%97)

4. その他の新しいデプロイプラットフォームや方法
    - Sealosを使用した[ワンクリックデプロイ](https://github.com/binary-husky/gpt_academic/issues/993)
    - WSL2（Windows Subsystem for Linux）の使用方法については、[デプロイwiki-2](https://github.com/binary-husky/gpt_academic/wiki/Getting-Started)を参照してください。
    - サブパス（例：`http://localhost/subpath`）でFastAPIを実行する方法については、[FastAPIの実行方法](docs/WithFastapi.md)を参照してください。



# 高度な使用法
### I：カスタムショートカットボタンの作成（学術的なショートカットキー）
テキストエディタで`core_functional.py`を開き、次の項目を追加し、プログラムを再起動します。（ボタンが存在する場合、プレフィックスとサフィックスはホット変更に対応しており、プログラムを再起動せずに有効にすることができます。）
例：
```
"超级英译中"： {
    # プレフィックス、入力の前に追加されます。例えば、要求を記述するために使用されます。翻訳、コードの解説、校正など
    "プレフィックス"： "下記の内容を中国語に翻訳し、専門用語を一つずつマークダウンテーブルで解説してください：\n\n"、

    # サフィックス、入力の後に追加されます。プレフィックスと一緒に使用して、入力内容を引用符で囲むことができます。
    "サフィックス"： ""、
}、
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

### II：関数プラグインのカスタマイズ
自分の望む任意のタスクを実行するために、強力な関数プラグインを作成できます。
このプロジェクトのプラグインの作成とデバッグの難易度は非常に低く、一定のPythonの基礎知識があれば、提供されたテンプレートを参考に自分自身のプラグイン機能を実装することができます。
詳細については、[関数プラグインガイド](https://github.com/binary-husky/gpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)を参照してください。


# 更新
### I：ダイナミック

1. 会話の保存機能。プラグインエリアで `Save Current Conversation` を呼び出すだけで、現在の会話を読み取り可能で復旧可能なhtmlファイルとして保存できます。
また、プラグインエリア（ドロップダウンメニュー）で `Load Conversation History Archive` を呼び出すことで、以前の会話を復元できます。
ヒント：ファイルを指定せずに `Load Conversation History Archive` をクリックすると、履歴のhtmlアーカイブのキャッシュを表示することができます。
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/235222390-24a9acc0-680f-49f5-bc81-2f3161f1e049.png" width="500" >
</div>

2. ⭐Latex/Arxiv論文の翻訳機能⭐
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/002a1a75-ace0-4e6a-94e2-ec1406a746f1" height="250" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/9fdcc391-f823-464f-9322-f8719677043b" height="250" >
</div>

3. ゼロのターミナル（自然言語入力からユーザの意図を理解+他のプラグインを自動的に呼び出す）

- ステップ1：「プラグインのPDF論文の翻訳を呼び出してください、アドレスはhttps://openreview.net/pdf?id=rJl0r3R9KX」と入力します。
- ステップ2：「Zero Terminal」をクリックします。

<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/66f1b044-e9ff-4eed-9126-5d4f3668f1ed" width="500" >
</div>

4. モジュール化された機能設計、シンプルなインターフェイスで強力な機能をサポートする
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>

5. 他のオープンソースプロジェクトの翻訳
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" height="250" >
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" height="250" >
</div>

6. [live2d](https://github.com/fghrsh/live2d_demo)のデコレーション機能（デフォルトでは無効で、`config.py`を変更する必要があります）
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/236432361-67739153-73e8-43fe-8111-b61296edabd9.png" width="500" >
</div>

7. OpenAI画像生成
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/bc7ab234-ad90-48a0-8d62-f703d9e74665" width="500" >
</div>

8. OpenAIオーディオ解析と要約
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/709ccf95-3aee-498a-934a-e1c22d3d5d5b" width="500" >
</div>

9. Latex全体の校正と修正
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/651ccd98-02c9-4464-91e1-77a6b7d1b033" height="200" > ===>
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/476f66d9-7716-4537-b5c1-735372c25adb" height="200">
</div>

10. 言語、テーマの切り替え
<div align="center">
<img src="https://github.com/binary-husky/gpt_academic/assets/96192199/b6799499-b6fb-4f0c-9c8e-1b441872f4e8" width="500" >
</div>



### II：バージョン:
- version 3.70（todo）: AutoGenプラグインのテーマを最適化し、一連の派生プラグインを設計する
- version 3.60: AutoGenを次世代プラグインの基盤として導入
- version 3.57: GLM3、星火v3、文心一言v4をサポート、ローカルモデルの並行バグを修正
- version 3.56: 基本機能ボタンを動的に追加、新しい報告書PDF集約ページ
- version 3.55: フロントエンドのデザインを再構築し、浮動ウィンドウとメニューバーを導入
- version 3.54: 新しい動的コードインタプリタ（Code Interpreter）の追加（未完成）
- version 3.53: 異なるテーマを動的に選択できるように、安定性の向上と複数ユーザの競合問題の解決
- version 3.50: 自然言語でこのプロジェクトのすべての関数プラグインを呼び出すことができるようになりました（ゼロのターミナル）プラグインの分類をサポートし、UIを改善し、新しいテーマを設計
- version 3.49: Baidu Qianfanプラットフォームと文心一言をサポート
- version 3.48: Alibaba DAMO Academy Tongyi Qianwen、Shanghai AI-Lab Shusheng、Xunfei Xinghuoをサポート
- version 3.46: 完全なオートモードのリアルタイム音声対話をサポート
- version 3.45: カスタムChatGLM2ファインチューニングモデルをサポート
- version 3.44: 公式にAzureをサポート、UIの使いやすさを最適化
- version 3.4: +arxiv論文の翻訳、latex論文の校閲機能
- version 3.3: +インターネット情報の総合機能
- version 3.2: 関数プラグインがさらに多くのパラメータインターフェースをサポート（会話の保存機能、任意の言語のコードの解釈、同時に任意のLLMの組み合わせを尋ねる）
- version 3.1: 複数のgptモデルに同時に質問できるようにサポートされました！ api2dをサポートし、複数のapikeyの負荷分散をサポートしました
- version 3.0: chatglmと他の小さなllmのサポート
- version 2.6: プラグインの構造を再構築し、対話性を高め、より多くのプラグインを追加しました
- version 2.5: 自己更新、ソースコード全体の要約時のテキストの長さ、トークンのオーバーフローの問題を解決しました
- version 2.4: (1)新しいPDF全文翻訳機能を追加しました。(2)入力エリアの位置を切り替えるための新しい機能を追加しました。(3)垂直レイアウトオプションを追加しました。(4)マルチスレッド関数プラグインを最適化しました。
- version 2.3: マルチスレッドの対話を強化しました
- version 2.2: 関数プラグインのホットリロードをサポート
- version 2.1: 折りたたみ式のレイアウト
- version 2.0: モジュール化された関数プラグインの導入
- version 1.0: 基本機能

GPT Academic開発者QQグループ：`610599535`

-既知の問題
    - 一部のブラウザ翻訳プラグインがこのソフトウェアのフロントエンドの実行を妨げる
    - 公式Gradioには互換性の問題があり、必ず`requirement.txt`を使用してGradioをインストールしてください

### III：テーマ
`THEME`オプション（`config.py`）を変更することで、テーマを変更できます
1. `Chuanhu-Small-and-Beautiful` [リンク](https://github.com/GaiZhenbiao/ChuanhuChatGPT/)


### IV：本プロジェクトの開発ブランチ

1. `master`ブランチ：メインブランチ、安定版
2. `frontier`ブランチ：開発ブランチ、テスト版


### V：参考と学習

```
コードの中には、他の優れたプロジェクトのデザインを参考にしたものが多く含まれています。順序は問いません：

# 清華ChatGLM2-6B:
https://github.com/THUDM/ChatGLM2-6B

# 清華JittorLLMs:
https://github.com/Jittor/JittorLLMs

# ChatPaper:
https://github.com/kaixindelele/ChatPaper

# Edge-GPT:
https://github.com/acheong08/EdgeGPT

# ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT



# Oobaboogaワンクリックインストーラー：
https://github.com/oobabooga/one-click-installers

# その他：
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
