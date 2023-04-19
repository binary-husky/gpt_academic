> **Note**
>
> このReadmeファイルは、このプロジェクトのmarkdown翻訳プラグインによって自動的に生成されたもので、100%正確ではない可能性があります。
>

# <img src="logo.png" width="40" > ChatGPT 学術最適化

**このプロジェクトが好きだったら、スターをつけてください。もし、より使いやすい学術用のショートカットキーまたはファンクションプラグインを発明した場合は、issueを発行するかpull requestを作成してください。また、このプロジェクト自体によって翻訳されたREADMEは[英語説明書|](docs/README_EN.md)[日本語説明書|](docs/README_JP.md)[ロシア語説明書|](docs/README_RS.md)[フランス語説明書](docs/README_FR.md)もあります。**

> **注意事項**
>
> 1. **赤色**のラベルが付いているファンクションプラグイン（ボタン）のみファイルを読み込めます。一部のプラグインはプラグインエリアのドロップダウンメニューにあります。新しいプラグインのPRを歓迎いたします！
>
> 2. このプロジェクトの各ファイルの機能は`self_analysis.md`（自己解析レポート）で詳しく説明されています。バージョンが追加されると、関連するファンクションプラグインをクリックして、GPTを呼び出して自己解析レポートを再生成することができます。一般的な質問は`wiki`にまとめられています。(`https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98`)


<div align="center">
    
機能 | 説明
--- | ---
ワンクリック整形 | 論文の文法エラーを一括で正確に修正できます。
ワンクリック日英翻訳 | 日英翻訳には、ワンクリックで対応できます。
ワンクリックコード説明 | コードの正しい表示と説明が可能です。
[カスタムショートカットキー](https://www.bilibili.com/video/BV14s4y1E7jN) | カスタムショートカットキーをサポートします。
[プロキシサーバーの設定](https://www.bilibili.com/video/BV1rc411W7Dr) | プロキシサーバーの設定をサポートします。
モジュラーデザイン | カスタム高階関数プラグインと[関数プラグイン]、プラグイン[ホット更新]のサポートが可能です。詳細は[こちら](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)
[自己プログラム解析](https://www.bilibili.com/video/BV1cj411A7VW) | [関数プラグイン][ワンクリック理解](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A)このプロジェクトのソースコード
[プログラム解析機能](https://www.bilibili.com/video/BV1cj411A7VW) | [関数プラグイン] ワンクリックで別のPython/C/C++/Java/Lua/...プロジェクトツリーを解析できます。
論文読解 | [関数プラグイン] LaTeX論文の全文をワンクリックで解読し、要約を生成します。
LaTeX全文翻訳、整形 | [関数プラグイン] ワンクリックでLaTeX論文を翻訳または整形できます。
注釈生成 | [関数プラグイン] ワンクリックで関数の注釈を大量に生成できます。
チャット分析レポート生成 | [関数プラグイン] 実行後、まとめレポートを自動生成します。
[arxivヘルパー](https://www.bilibili.com/video/BV1LM4y1279X) | [関数プラグイン] 入力したarxivの記事URLで要約をワンクリック翻訳+PDFダウンロードができます。
[PDF論文全文翻訳機能](https://www.bilibili.com/video/BV1KT411x7Wn) | [関数プラグイン] PDF論文タイトルと要約を抽出し、全文を翻訳します（マルチスレッド）。
[Google Scholar Integratorヘルパー](https://www.bilibili.com/video/BV19L411U7ia) | [関数プラグイン] 任意のGoogle Scholar検索ページURLを指定すると、gptが興味深い記事を選択します。
数式/画像/テーブル表示 | 数式のTex形式とレンダリング形式を同時に表示できます。数式、コードのハイライトをサポートしています。
マルチスレッド関数プラグインサポート | ChatGPTをマルチスレッドで呼び出すことができ、大量のテキストやプログラムを簡単に処理できます。
ダークグラジオ[テーマ](https://github.com/binary-husky/chatgpt_academic/issues/173)の起動 | 「/?__dark-theme=true」というURLをブラウザに追加することで、ダークテーマに切り替えることができます。
[多数のLLMモデル](https://www.bilibili.com/video/BV1wT411p7yf)をサポート、[API2D](https://api2d.com/)インターフェースをサポート | GPT3.5、GPT4、[清華ChatGLM](https://github.com/THUDM/ChatGLM-6B)による同時サポートは、とても素晴らしいですね！
huggingface免科学上网[オンライン版](https://huggingface.co/spaces/qingxu98/gpt-academic) | huggingfaceにログイン後、[このスペース](https://huggingface.co/spaces/qingxu98/gpt-academic)をコピーしてください。
...... | ......


</div>


- 新しいインターフェース（config.pyのLAYOUTオプションを変更するだけで、「左右レイアウト」と「上下レイアウト」を切り替えることができます）
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230361456-61078362-a966-4eb5-b49e-3c62ef18b860.gif" width="700" >
</div>


- すべてのボタンは、functional.pyを読み込んで動的に生成されます。カスタム機能を自由に追加して、クリップボードを解放します
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- 色を修正/修正
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- 出力に数式が含まれている場合、TeX形式とレンダリング形式の両方が表示され、コピーと読み取りが容易になります
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- プロジェクトのコードを見るのが面倒？chatgptに整備されたプロジェクトを直接与えましょう
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- 多数の大規模言語モデルの混合呼び出し(ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

多数の大規模言語モデルの混合呼び出し[huggingfaceテスト版](https://huggingface.co/spaces/qingxu98/academic-chatgpt-beta)(huggigface版はchatglmをサポートしていません)


---

## インストール-方法1：直接運転 (Windows、LinuxまたはMacOS)

1. プロジェクトをダウンロードします。
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. API_KEYとプロキシ設定を構成する

`config.py`で、海外のProxyとOpenAI API KEYを構成して説明します。
```
1.あなたが中国にいる場合、OpenAI APIをスムーズに使用するには海外プロキシを設定する必要があります。構成の詳細については、config.py（1.その中のUSE_PROXYをTrueに変更し、2.手順に従ってプロキシを変更する）を詳細に読んでください。
2. OpenAI API KEYを構成する。OpenAIのウェブサイトでAPI KEYを取得してください。一旦API KEYを手に入れると、config.pyファイルで設定するだけです。
3.プロキシネットワークに関連する問題(ネットワークタイムアウト、プロキシが動作しない）をhttps://github.com/binary-husky/chatgpt_academic/issues/1にまとめました。
```
(P.S. プログラム実行時にconfig.pyの隣にconfig_private.pyという名前のプライバシー設定ファイルを作成し、同じ名前の設定を上書きするconfig_private.pyが存在するかどうかを優先的に確認します。そのため、私たちの構成読み取りロジックを理解できる場合は、config.pyの隣にconfig_private.pyという名前の新しい設定ファイルを作成し、その中のconfig.pyから設定を移動してください。config_private.pyはgitで保守されていないため、プライバシー情報をより安全にすることができます。)

3. 依存関係をインストールします。
```sh
# 選択肢があります。
python -m pip install -r requirements.txt


# (選択肢2) もしAnacondaを使用する場合、手順は同様です：
# (選択肢2.1) conda create -n gptac_venv python=3.11
# (選択肢2.2) conda activate gptac_venv
# (選択肢2.3) python -m pip install -r requirements.txt

# 注: 公式のpipソースまたはAlibabaのpipソースを使用してください。 別のpipソース（例：一部の大学のpip）は問題が発生する可能性があります。 一時的なソースの切り替え方法： 
# python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

もしあなたが清華ChatGLMをサポートする必要がある場合、さらに多くの依存関係をインストールする必要があります（Pythonに慣れない方やコンピューターの設定が十分でない方は、試みないことをお勧めします）：
```sh
python -m pip install -r request_llm/requirements_chatglm.txt
```

4. 実行
```sh
python main.py
```

5. 関数プラグインのテスト
```
- Pythonプロジェクト分析のテスト
    入力欄に `./crazy_functions/test_project/python/dqn` と入力し、「Pythonプロジェクト全体の解析」をクリックします。
- 自己コード解読のテスト
    「[マルチスレッドデモ] このプロジェクト自体を解析します（ソースを翻訳して解読します）」をクリックします。
- 実験的な機能テンプレート関数のテスト（GPTが「今日の歴史」に何が起こったかを回答することが求められます）。この関数をテンプレートとして使用して、より複雑な機能を実装できます。
    「[関数プラグインテンプレートデモ] 今日の歴史」をクリックします。
- 関数プラグインエリアのドロップダウンメニューには他にも選択肢があります。
```

## インストール方法2：Dockerを使用する（Linux）

1. ChatGPTのみ（大多数の人にお勧めです）
``` sh
# プロジェクトのダウンロード
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
# 海外プロキシとOpenAI API KEYの設定
config.pyを任意のテキストエディタで編集する
# インストール
docker build -t gpt-academic .
# 実行
docker run --rm -it --net=host gpt-academic

# 関数プラグインのテスト
## 関数プラグインテンプレート関数のテスト（GPTが「今日の歴史」に何が起こったかを回答することが求められます）。この関数をテンプレートとして使用して、より複雑な機能を実装できます。
「[関数プラグインテンプレートデモ] 今日の歴史」をクリックします。
## Latexプロジェクトの要約を書くテスト
入力欄に./crazy_functions/test_project/latex/attentionと入力し、「テックス論文を読んで要約を書く」をクリックします。
## Pythonプロジェクト分析のテスト
入力欄に./crazy_functions/test_project/python/dqnと入力し、[Pythonプロジェクトの全解析]をクリックします。

関数プラグインエリアのドロップダウンメニューには他にも選択肢があります。
```

2. ChatGPT + ChatGLM（Dockerに非常に詳しい人+十分なコンピューター設定が必要）



```sh
# Dockerfileの編集
cd docs && nano Dockerfile+ChatGLM
# ビルド方法
docker build -t gpt-academic --network=host -f Dockerfile+ChatGLM .
# 実行方法 (1) 直接実行: 
docker run --rm -it --net=host --gpus=all gpt-academic
# 実行方法 (2) コンテナに入って調整する:
docker run --rm -it --net=host --gpus=all gpt-academic bash
```

## インストール方法3：その他のデプロイ方法

1. クラウドサーバーデプロイ
[デプロイwiki-1](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)

2. WSL2を使用 (Windows Subsystem for Linux)
[デプロイwiki-2](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)


## インストール-プロキシ設定
1. 通常の方法
[プロキシを設定する](https://github.com/binary-husky/chatgpt_academic/issues/1)

2. 初心者向けチュートリアル
[初心者向けチュートリアル](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BB%A3%E7%90%86%E8%BD%AF%E4%BB%B6%E9%97%AE%E9%A2%98%E7%9A%84%E6%96%B0%E6%89%8B%E8%A7%A3%E5%86%B3%E6%96%B9%E6%B3%95%EF%BC%88%E6%96%B9%E6%B3%95%E5%8F%AA%E9%80%82%E7%94%A8%E4%BA%8E%E6%96%B0%E6%89%8B%EF%BC%89)


---

## カスタムボタンの追加(学術ショートカットキー)

`core_functional.py`を任意のテキストエディタで開き、以下のエントリーを追加し、プログラムを再起動してください。(ボタンが追加されて表示される場合、前置詞と後置詞はホット編集がサポートされているため、プログラムを再起動せずに即座に有効になります。)

例:
```
"超级英译中": {
    # 前置詞 - あなたの要求を説明するために使用されます。翻訳、コードの説明、編集など。
    "Prefix": "以下のコンテンツを中国語に翻訳して、マークダウンテーブルを使用して専門用語を説明してください。\n\n", 
    
    # 後置詞 - プレフィックスと共に使用すると、入力内容を引用符で囲むことができます。
    "Suffix": "",
},
```

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>


---

## いくつかの機能の例

### 画像表示：

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/228737599-bf0a9d9c-1808-4f43-ae15-dfcc7af0f295.png" width="800" >
</div>


### プログラムが自己解析できる場合：

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936850-c77d7183-0749-4c1c-9875-fd4891842d0c.png" width="800" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226936618-9b487e4b-ab5b-4b6e-84c6-16942102e917.png" width="800" >
</div>

### 他のPython/Cppプロジェクトの解析：

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="800" >
</div>

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226969067-968a27c1-1b9c-486b-8b81-ab2de8d3f88a.png" width="800" >
</div>

### Latex論文の一括読解と要約生成

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227504406-86ab97cd-f208-41c3-8e4a-7000e51cf980.png" width="800" >
</div>

### 自動報告生成

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/227503770-fe29ce2c-53fd-47b0-b0ff-93805f0c2ff4.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504617-7a497bb3-0a2a-4b50-9a8a-95ae60ea7afd.png" height="300" >
<img src="https://user-images.githubusercontent.com/96192199/227504005-efeaefe0-b687-49d0-bf95-2d7b7e66c348.png" height="300" >
</div>

### モジュール化された機能デザイン

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229288270-093643c1-0018-487a-81e6-1d7809b6e90f.png" height="400" >
<img src="https://user-images.githubusercontent.com/96192199/227504931-19955f78-45cd-4d1c-adac-e71e50957915.png" height="400" >
</div>


### ソースコードの英語翻訳

<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/229720562-fe6c3508-6142-4635-a83d-21eb3669baee.png" height="400" >
</div>

## Todo およびバージョン計画:
- version 3.2+ (todo): 関数プラグインがより多くのパラメーターインターフェースをサポートするようになります。
- version 3.1: 複数のgptモデルを同時にクエリし、api2dをサポートし、複数のapikeyの負荷分散をサポートします。
- version 3.0: chatglmおよび他の小型llmのサポート
- version 2.6: プラグイン構造を再構成し、相互作用性を高め、より多くのプラグインを追加しました。
- version 2.5: 自己更新。総括的な大規模プロジェクトのソースコードをまとめた場合、テキストが長すぎる、トークンがオーバーフローする問題を解決します。
- version 2.4: (1)PDF全文翻訳機能を追加。(2)入力エリアの位置を切り替える機能を追加。(3)垂直レイアウトオプションを追加。(4)マルチスレッド関数プラグインの最適化。
- version 2.3: 多スレッドの相互作用性を向上させました。
- version 2.2: 関数プラグインでホットリロードをサポート
- version 2.1: 折りたたみ式レイアウト
- version 2.0: モジュール化された関数プラグインを導入
- version 1.0: 基本機能

## 参考および学習


以下は中国語のマークダウンファイルです。日本語に翻訳してください。既存のマークダウンコマンドを変更しないでください：

```
多くの優秀なプロジェクトの設計を参考にしています。主なものは以下の通りです：

# 参考プロジェクト1：ChuanhuChatGPTから多くのテクニックを借用
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# 参考プロジェクト2：清華ChatGLM-6B：
https://github.com/THUDM/ChatGLM-6B
```

