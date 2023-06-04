> **노트**
>
> 의존성을 설치할 때는 반드시 requirements.txt에서 **지정된 버전**을 엄격하게 선택하십시오.
> 
> `pip install -r requirements.txt`

# <img src="docs/logo.png" width="40" > GPT 학술 최적화 (GPT Academic)

**이 프로젝트가 마음에 드신다면 Star를 주세요. 추가로 유용한 학술 단축키나 기능 플러그인이 있다면 이슈나 pull request를 남기세요. 이 프로젝트에 대한 [영어 |](docs/README_EN.md)[일본어 |](docs/README_JP.md)[한국어 |](https://github.com/mldljyh/ko_gpt_academic)[러시아어 |](docs/README_RS.md)[프랑스어](docs/README_FR.md)로 된 README도 있습니다. 
GPT를 이용하여 프로젝트를 임의의 언어로 번역하려면 [`multi_language.py`](multi_language.py)를 읽고 실행하십시오. (실험적)

> **노트**
>
> 1. 파일을 읽기 위해 **빨간색**으로 표시된 기능 플러그인 (버튼) 만 지원됩니다. 일부 플러그인은 플러그인 영역의 **드롭다운 메뉴**에 있습니다. 또한 새로운 플러그인은 **가장 높은 우선순위**로 환영하며 처리합니다!
>
> 2. 이 프로젝트의 각 파일의 기능을 [`self_analysis.md`](https://github.com/binary-husky/chatgpt_academic/wiki/chatgpt-academic%E9%A1%B9%E7%9B%AE%E8%87%AA%E8%AF%91%E8%A7%A3%E6%8A%A5%E5%91%8A)에서 자세히 설명합니다. 버전이 업데이트 됨에 따라 관련된 기능 플러그인을 클릭하고 GPT를 호출하여 프로젝트의 자체 분석 보고서를 다시 생성할 수도 있습니다. 자주 묻는 질문은 [`위키`](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%B8%B8%E8%A7%81%E9%97%AE%E9%A2%98)에서 볼 수 있습니다. [설치 방법](#installation).
> 
> 3. 이 프로젝트는 국내 언어 모델 chatglm과 RWKV, 판고 등의 시도와 호환 가능합니다. 여러 개의 api-key를 지원하며 설정 파일에 "API_KEY="openai-key1,openai-key2,api2d-key3""와 같이 작성할 수 있습니다. `API_KEY`를 임시로 변경해야하는 경우 입력 영역에 임시 `API_KEY`를 입력 한 후 엔터 키를 누르면 즉시 적용됩니다. 

<div align="center">
    
기능 | 설명
--- | ---
원 키워드 | 원 키워드 및 논문 문법 오류를 찾는 기능 지원
한-영 키워드 | 한-영 키워드 지원
코드 설명 | 코드 표시, 코드 설명, 코드 생성, 코드에 주석 추가
[사용자 정의 바로 가기 키](https://www.bilibili.com/video/BV14s4y1E7jN) | 사용자 정의 바로 가기 키 지원
모듈식 설계 | 강력한[함수 플러그인](https://github.com/binary-husky/chatgpt_academic/tree/master/crazy_functions) 지원, 플러그인이 [램 업데이트](https://github.com/binary-husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E4%BB%B6%E6%8C%87%E5%8D%97)를 지원합니다.
[자체 프로그램 분석](https://www.bilibili.com/video/BV1cj411A7VW) | [함수 플러그인] [원 키 우드] 프로젝트 소스 코드의 내용을 이해하는 기능을 제공
[프로그램 분석](https://www.bilibili.com/video/BV1cj411A7VW) | [함수 플러그인] 프로젝트 트리를 분석할 수 있습니다 (Python/C/C++/Java/Lua/...)
논문 읽기, 번역 | [함수 플러그인] LaTex/PDF 논문의 전문을 읽고 요약을 생성합니다.
LaTeX 텍스트[번역](https://www.bilibili.com/video/BV1nk4y1Y7Js/), [원 키워드](https://www.bilibili.com/video/BV1FT411H7c5/) | [함수 플러그인] LaTeX 논문의 번역 또는 개량을 위해 일련의 모드를 번역할 수 있습니다.
대량의 주석 생성 | [함수 플러그인] 함수 코멘트를 대량으로 생성할 수 있습니다.
Markdown 한-영 번역 | [함수 플러그인] 위의 5 종 언어의 [README](https://github.com/binary-husky/chatgpt_academic/blob/master/docs/README_EN.md)를 볼 수 있습니다.
chat 분석 보고서 생성 | [함수 플러그인] 수행 후 요약 보고서를 자동으로 생성합니다.
[PDF 논문 번역](https://www.bilibili.com/video/BV1KT411x7Wn) | [함수 플러그인] PDF 논문이 제목 및 요약을 추출한 후 번역됩니다. (멀티 스레드)
[Arxiv 도우미](https://www.bilibili.com/video/BV1LM4y1279X) | [함수 플러그인] Arxiv 논문 URL을 입력하면 요약을 번역하고 PDF를 다운로드 할 수 있습니다.
[Google Scholar 통합 도우미](https://www.bilibili.com/video/BV19L411U7ia) | [함수 플러그인] Google Scholar 검색 페이지 URL을 제공하면 gpt가 [Related Works 작성](https://www.bilibili.com/video/BV1GP411U7Az/)을 도와줍니다.
인터넷 정보 집계+GPT | [함수 플러그인] 먼저 GPT가 인터넷에서 정보를 수집하고 질문에 대답 할 수 있도록합니다. 정보가 절대적으로 구식이 아닙니다.
수식/이미지/표 표시 | 급여, 코드 강조 기능 지원
멀티 스레드 함수 플러그인 지원 | Chatgpt를 여러 요청에서 실행하여 [대량의 텍스트](https://www.bilibili.com/video/BV1FT411H7c5/) 또는 프로그램을 처리 할 수 있습니다.
다크 그라디오 테마 시작 | 어둡게 주제를 변경하려면 브라우저 URL 끝에 ```/?__theme=dark```을 추가하면됩니다.
[다중 LLM 모델](https://www.bilibili.com/video/BV1wT411p7yf) 지원, [API2D](https://api2d.com/) 인터페이스 지원됨 | GPT3.5, GPT4, [Tsinghua ChatGLM](https://github.com/THUDM/ChatGLM-6B), [Fudan MOSS](https://github.com/OpenLMLab/MOSS)가 모두 동시에 작동하는 것처럼 느낄 수 있습니다!
LLM 모델 추가 및[huggingface 배치](https://huggingface.co/spaces/qingxu98/gpt-academic) 지원 | 새 Bing 인터페이스 (새 Bing) 추가, Clearing House [Jittorllms](https://github.com/Jittor/JittorLLMs) 지원 [LLaMA](https://github.com/facebookresearch/llama), [RWKV](https://github.com/BlinkDL/ChatRWKV) 및 [盘古α](https://openi.org.cn/pangu/)
기타 새로운 기능 (이미지 생성 등) ... | 이 문서의 끝부분을 참조하세요. ...- 모든 버튼은 functional.py를 동적으로 읽어와서 사용자 정의 기능을 자유롭게 추가할 수 있으며, 클립 보드를 해제합니다.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231975334-b4788e91-4887-412f-8b43-2b9c5f41d248.gif" width="700" >
</div>

- 검수/오타 교정
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/231980294-f374bdcb-3309-4560-b424-38ef39f04ebd.gif" width="700" >
</div>

- 출력에 수식이 포함되어 있으면 텍스와 렌더링의 형태로 동시에 표시되어 복사 및 읽기가 용이합니다.
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/230598842-1d7fcddd-815d-40ee-af60-baf488a199df.png" width="700" >
</div>

- 프로젝트 코드를 볼 시간이 없습니까? 전체 프로젝트를 chatgpt에 직접 표시하십시오
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226935232-6b6a73ce-8900-4aee-93f9-733c7e6fef53.png" width="700" >
</div>

- 다양한 대형 언어 모델 범용 요청 (ChatGLM + OpenAI-GPT3.5 + [API2D](https://api2d.com/)-GPT4)
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/232537274-deca0563-7aa6-4b5d-94a2-b7c453c47794.png" width="700" >
</div>

---
# 설치
## Installation-Method 1: Run directly (Windows, Linux or MacOS) 

1. 프로젝트 다운로드
```sh
git clone https://github.com/binary-husky/chatgpt_academic.git
cd chatgpt_academic
```

2. API_KEY 구성

`config.py`에서 API KEY 등 설정을 구성합니다. [특별한 네트워크 환경 설정](https://github.com/binary-husky/gpt_academic/issues/1) .

(P.S. 프로그램이 실행될 때, 이름이 `config_private.py`인 기밀 설정 파일이 있는지 우선적으로 확인하고 해당 설정으로 `config.py`의 동일한 이름의 설정을 덮어씁니다. 따라서 구성 읽기 논리를 이해할 수 있다면, `config.py` 옆에 `config_private.py`라는 새 구성 파일을 만들고 `config.py`의 구성을 `config_private.py`로 이동(복사)하는 것이 좋습니다. `config_private.py`는 git으로 관리되지 않으며 개인 정보를 더 안전하게 보호할 수 있습니다. P.S. 프로젝트는 또한 대부분의 옵션을 `환경 변수`를 통해 설정할 수 있으며, `docker-compose` 파일을 참조하여 환경 변수 작성 형식을 확인할 수 있습니다. 우선순위: `환경 변수` > `config_private.py` > `config.py`)


3. 의존성 설치
```sh
# (I 선택: 기존 python 경험이 있다면) (python 버전 3.9 이상, 최신 버전이 좋습니다), 참고: 공식 pip 소스 또는 알리 pip 소스 사용, 일시적인 교체 방법: python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install -r requirements.txt

# (II 선택: Python에 익숙하지 않은 경우) anaconda 사용 방법은 비슷함(https://www.bilibili.com/video/BV1rc411W7Dr):
conda create -n gptac_venv python=3.11    # anaconda 환경 만들기
conda activate gptac_venv                 # anaconda 환경 활성화
python -m pip install -r requirements.txt # 이 단계도 pip install의 단계와 동일합니다.
```

<details><summary>추가지원을 위해 Tsinghua ChatGLM / Fudan MOSS를 사용해야하는 경우 지원을 클릭하여 이 부분을 확장하세요.</summary>
<p>

[Tsinghua ChatGLM] / [Fudan MOSS]를 백엔드로 사용하려면 추가적인 종속성을 설치해야합니다 (전제 조건 : Python을 이해하고 Pytorch를 사용한 적이 있으며, 컴퓨터가 충분히 강력한 경우) :
```sh
# [선택 사항 I] Tsinghua ChatGLM을 지원합니다. Tsinghua ChatGLM에 대한 참고사항 : "Call ChatGLM fail cannot load ChatGLM parameters normally" 오류 발생시 다음 참조: 
# 1 : 기본 설치된 것들은 torch + cpu 버전입니다. cuda를 사용하려면 torch를 제거한 다음 torch + cuda를 다시 설치해야합니다.
# 2 : 모델을 로드할 수 없는 기계 구성 때문에, AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)를
# AutoTokenizer.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True)로 변경합니다.
python -m pip install -r request_llm/requirements_chatglm.txt  

# [선택 사항 II] Fudan MOSS 지원
python -m pip install -r request_llm/requirements_moss.txt
git clone https://github.com/OpenLMLab/MOSS.git request_llm/moss  # 다음 코드 줄을 실행할 때 프로젝트 루트 경로에 있어야합니다.

# [선택 사항III] AVAIL_LLM_MODELS config.py 구성 파일에 기대하는 모델이 포함되어 있는지 확인하십시오.
# 현재 지원되는 전체 모델 :
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "api2d-gpt-3.5-turbo", "gpt-4", "api2d-gpt-4", "chatglm", "newbing", "moss"] # + ["jittorllms_rwkv", "jittorllms_pangualpha", "jittorllms_llama"]
```

</p>
</details>



4. 실행
```sh
python main.py
```5. 테스트 함수 플러그인
```
- 테스트 함수 플러그인 템플릿 함수 (GPT에게 오늘의 역사에서 무슨 일이 일어났는지 대답하도록 요청)를 구현하는 데 사용할 수 있습니다. 이 함수를 기반으로 더 복잡한 기능을 구현할 수 있습니다.
    "[함수 플러그인 템플릿 데모] 오늘의 역사"를 클릭하세요.
```

## 설치 - 방법 2 : 도커 사용

1. ChatGPT 만 (대부분의 사람들이 선택하는 것을 권장합니다.)

``` sh
git clone https://github.com/binary-husky/chatgpt_academic.git  # 다운로드
cd chatgpt_academic                                 # 경로 이동
nano config.py                                      # 아무 텍스트 에디터로 config.py를 열고 "Proxy","API_KEY","WEB_PORT" (예 : 50923) 등을 구성합니다.
docker build -t gpt-academic .                      # 설치

#(마지막 단계-1 선택) Linux 환경에서는 --net=host를 사용하면 더 편리합니다.
docker run --rm -it --net=host gpt-academic
#(마지막 단계-2 선택) macOS / windows 환경에서는 -p 옵션을 사용하여 컨테이너의 포트 (예 : 50923)를 호스트의 포트로 노출해야합니다.
docker run --rm -it -e WEB_PORT=50923 -p 50923:50923 gpt-academic
```

2. ChatGPT + ChatGLM + MOSS (Docker에 익숙해야합니다.)

``` sh
#docker-compose.yml을 수정하여 계획 1 및 계획 3을 삭제하고 계획 2를 유지합니다. docker-compose.yml에서 계획 2의 구성을 수정하면 됩니다. 주석을 참조하십시오.
docker-compose up
```

3. ChatGPT + LLAMA + Pangu + RWKV (Docker에 익숙해야합니다.)
``` sh
#docker-compose.yml을 수정하여 계획 1 및 계획 2을 삭제하고 계획 3을 유지합니다. docker-compose.yml에서 계획 3의 구성을 수정하면 됩니다. 주석을 참조하십시오.
docker-compose up
```


## 설치 - 방법 3 : 다른 배치 방법

1. 리버스 프록시 URL / Microsoft Azure API 사용 방법
API_URL_REDIRECT를 `config.py`에 따라 구성하면됩니다.

2. 원격 클라우드 서버 배치 (클라우드 서버 지식과 경험이 필요합니다.)
[배치위키-1](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BA%91%E6%9C%8D%E5%8A%A1%E5%99%A8%E8%BF%9C%E7%A8%8B%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97)에 방문하십시오.

3. WSL2 사용 (Windows Subsystem for Linux 하위 시스템)
[배치 위키-2](https://github.com/binary-husky/chatgpt_academic/wiki/%E4%BD%BF%E7%94%A8WSL2%EF%BC%88Windows-Subsystem-for-Linux-%E5%AD%90%E7%B3%BB%E7%BB%9F%EF%BC%89%E9%83%A8%E7%BD%B2)에 방문하십시오.

4. 2 차 URL (예 : `http : //localhost/subpath`)에서 실행하는 방법
[FastAPI 실행 설명서] (docs / WithFastapi.md)를 참조하십시오.

5. docker-compose 실행
docker-compose.yml을 읽은 후 지시 사항에 따라 작업하십시오.
---
# 고급 사용법
## 사용자 정의 바로 가기 버튼 / 사용자 정의 함수 플러그인

1. 사용자 정의 바로 가기 버튼 (학술 바로 가기)
임의의 텍스트 편집기로 'core_functional.py'를 엽니다. 엔트리 추가, 그런 다음 프로그램을 다시 시작하면됩니다. (버튼이 이미 추가되어 보이고 접두사, 접미사가 모두 변수가 효과적으로 수정되면 프로그램을 다시 시작하지 않아도됩니다.)
예 :
```
"超级英译中": {
    # 접두사. 당신이 요구하는 것을 설명하는 데 사용됩니다. 예를 들어 번역, 코드를 설명, 다듬기 등
    "Prefix": "下面翻译成中文，然后用一个 markdown 表格逐一解释文中出现的专有名词：\n\n", 
    
    # 접미사는 입력 내용 앞뒤에 추가됩니다. 예를 들어 전위를 사용하여 입력 내용을 따옴표로 묶는데 사용할 수 있습니다.
    "Suffix": "",
},
```
<div align="center">
<img src="https://user-images.githubusercontent.com/96192199/226899272-477c2134-ed71-4326-810c-29891fe4a508.png" width="500" >
</div>

2. 사용자 지정 함수 플러그인
강력한 함수 플러그인을 작성하여 원하는 작업을 수행하십시오.
이 프로젝트의 플러그인 작성 및 디버깅 난이도는 매우 낮으며, 일부 파이썬 기본 지식만 있으면 제공된 템플릿을 모방하여 플러그인 기능을 구현할 수 있습니다. 자세한 내용은 [함수 플러그인 가이드]를 참조하십시오. (https://github.com/binary -husky/chatgpt_academic/wiki/%E5%87%BD%E6%95%B0%E6%8F%92%E 4%BB%B6%E6%8C%87%E5%8D%97).
---
# 최신 업데이트
## 새로운 기능 동향1. 대화 저장 기능. 

1. 함수 플러그인 영역에서 '현재 대화 저장'을 호출하면 현재 대화를 읽을 수 있고 복원 가능한 HTML 파일로 저장할 수 있습니다. 또한 함수 플러그인 영역(드롭다운 메뉴)에서 '대화 기록 불러오기'를 호출하면 이전 대화를 복원할 수 있습니다. 팁: 파일을 지정하지 않고 '대화 기록 불러오기'를 클릭하면 기록된 HTML 캐시를 볼 수 있으며 '모든 로컬 대화 기록 삭제'를 클릭하면 모든 HTML 캐시를 삭제할 수 있습니다.

2. 보고서 생성. 대부분의 플러그인은 실행이 끝난 후 작업 보고서를 생성합니다.

3. 모듈화 기능 설계, 간단한 인터페이스로도 강력한 기능을 지원할 수 있습니다.

4. 자체 번역이 가능한 오픈 소스 프로젝트입니다.

5. 다른 오픈 소스 프로젝트를 번역하는 것은 어렵지 않습니다.

6. [live2d](https://github.com/fghrsh/live2d_demo) 장식 기능(기본적으로 비활성화되어 있으며 `config.py`를 수정해야 합니다.)

7. MOSS 대 언어 모델 지원 추가

8. OpenAI 이미지 생성

9. OpenAI 음성 분석 및 요약

10. LaTeX 전체적인 교정 및 오류 수정

## 버전:
- version 3.5 (TODO): 자연어를 사용하여 이 프로젝트의 모든 함수 플러그인을 호출하는 기능(우선순위 높음)
- version 3.4(TODO): 로컬 대 모듈의 다중 스레드 지원 향상
- version 3.3: 인터넷 정보 종합 기능 추가
- version 3.2: 함수 플러그인이 더 많은 인수 인터페이스를 지원합니다.(대화 저장 기능, 임의의 언어 코드 해석 및 동시에 임의의 LLM 조합을 확인하는 기능)
- version 3.1: 여러 개의 GPT 모델에 대한 동시 쿼리 지원! api2d 지원, 여러 개의 apikey 로드 밸런싱 지원
- version 3.0: chatglm 및 기타 소형 llm의 지원
- version 2.6: 플러그인 구조를 재구성하여 상호 작용성을 향상시켰습니다. 더 많은 플러그인을 추가했습니다.
- version 2.5: 자체 업데이트, 전체 프로젝트를 요약할 때 텍스트가 너무 길어지고 토큰이 오버플로우되는 문제를 해결했습니다.
- version 2.4: (1) PDF 전체 번역 기능 추가; (2) 입력 영역 위치 전환 기능 추가; (3) 수직 레이아웃 옵션 추가; (4) 다중 스레드 함수 플러그인 최적화.
- version 2.3: 다중 스레드 상호 작용성 강화
- version 2.2: 함수 플러그인 히트 리로드 지원
- version 2.1: 접는 레이아웃 지원
- version 2.0: 모듈화 함수 플러그인 도입
- version 1.0: 기본 기능

gpt_academic 개발자 QQ 그룹-2 : 610599535

- 알려진 문제
    - 일부 브라우저 번역 플러그인이이 소프트웨어의 프론트 엔드 작동 방식을 방해합니다.
    - gradio 버전이 너무 높거나 낮으면 여러 가지 이상이 발생할 수 있습니다.

## 참고 및 학습 자료

```
많은 우수 프로젝트의 디자인을 참고했습니다. 주요 항목은 다음과 같습니다.

# 프로젝트 1 : Tsinghua ChatGLM-6B :
https://github.com/THUDM/ChatGLM-6B

# 프로젝트 2 : Tsinghua JittorLLMs:
https://github.com/Jittor/JittorLLMs

# 프로젝트 3 : Edge-GPT :
https://github.com/acheong08/EdgeGPT

# 프로젝트 4 : ChuanhuChatGPT:
https://github.com/GaiZhenbiao/ChuanhuChatGPT

# 프로젝트 5 : ChatPaper :
https://github.com/kaixindelele/ChatPaper

# 더 많은 :
https://github.com/gradio-app/gradio
https://github.com/fghrsh/live2d_demo
```
