md = """
You can use the following Python script to rename files matching the pattern '* - 副本.tex' to '* - wushiguang.tex' in a directory:

```python
import os

# Directory containing the files
directory = 'Tex/'

for filename in os.listdir(directory):
    if filename.endswith(' - 副本.tex'):
        new_filename = filename.replace(' - 副本.tex', ' - wushiguang.tex')
        os.rename(os.path.join(directory, filename), os.path.join(directory, new_filename))
```

Replace 'Tex/' with the actual directory path where your files are located before running the script.
"""


md = """
Following code including wrapper

```python:wrapper.py
graph TD
    A[Enter Chart Definition] --> B(Preview)
    B --> C{decide}
    C --> D[Keep]
    C --> E[Edit Definition]
    E --> B
    D --> F[Save Image and Code]
    F --> B



```

<details>
<summary><b>My section header in bold</b></summary>

Any folded content here. It requires an empty line just above it.

</details>

"""

md ="""

<details>
<summary>第0份搜索结果 [源自google搜索] （汤姆·赫兰德）：</summary>
<div class="search_result">https://baike.baidu.com/item/%E6%B1%A4%E5%A7%86%C2%B7%E8%B5%AB%E5%85%B0%E5%BE%B7/3687216</div>
<div class="search_result">Title: 汤姆·赫兰德

URL Source: https://baike.baidu.com/item/%E6%B1%A4%E5%A7%86%C2%B7%E8%B5%AB%E5%85%B0%E5%BE%B7/3687216

Markdown Content:
网页新闻贴吧知道网盘图片视频地图文库资讯采购百科
百度首页
登录
注册
进入词条
全站搜索
帮助
首页
秒懂百科
特色百科
知识专题
加入百科
百科团队
权威合作
个人中心
汤姆·赫兰德
播报
讨论
上传视频
英国男演员
汤姆·赫兰德（Tom Holland），1996年6月1日出生于英国英格兰泰晤士河畔金斯顿，英国男演员。2008年，出演音乐剧《跳出我天地》而崭露头角。2010年，作为主演参加音乐剧《跳出我天地》的五周年特别演出。2012年10月11日，主演的个人首部电影《海啸奇迹》上映，并凭该电影获得第84届美国国家评论协会奖最具突破男演员奖。2016年10月15日，与查理·汉纳姆、西耶娜·米勒合作出演的电影《 ... >>>

目录
1早年经历
2演艺经历
▪影坛新星
▪角色多变
▪跨界翘楚
3个人生活
▪家庭
▪恋情
▪社交
4主要作品
▪参演电影
▪参演电视剧
▪配音作品
▪导演作品
▪杂志写真
5社会活动
6获奖记录
7人物评价
基本信息
汤姆·赫兰德（Tom Holland），1996年6月1日出生于英国英格兰泰晤士河畔金斯顿，英国男演员。 [67]
2008年，出演音乐剧《跳出我天地》而崭露头角 [1]。2010年，作为主演参加音乐剧《跳出我天地》的五周年特别演出 [2]。2012年10月11日，主演的个人首部电影《海啸奇迹》上映，并凭该电影获得第84届美国国家评论协会奖最具突破男演员奖 [3]。2016年10月15日，与查理·汉纳姆、西耶娜·米勒合作出演的电影《迷失Z城》在纽约电影节首映 [17]；2017年，主演的《蜘蛛侠：英雄归来》上映，他凭该电影获得第19届青少年选择奖最佳暑期电影男演员奖，以及第70届英国电影和电视艺术学院奖最佳新星奖。 [72]2019年，主演的电影《蜘蛛侠：英雄远征》上映 [5]；同年，凭借该电影获得第21届青少年选择奖最佳夏日电影男演员奖 [6]。2024年4月，汤姆·霍兰德主演的伦敦西区新版舞台剧《罗密欧与朱丽叶》公布演员名单。 [66]
2024年，......</div>
</details>

<details>
<summary>第1份搜索结果 [源自google搜索] （汤姆·霍兰德）：</summary>
<div class="search_result">https://zh.wikipedia.org/zh-hans/%E6%B1%A4%E5%A7%86%C2%B7%E8%B5%AB%E5%85%B0%E5%BE%B7</div>
<div class="search_result">Title: 汤姆·赫兰德

URL Source: https://zh.wikipedia.org/zh-hans/%E6%B1%A4%E5%A7%86%C2%B7%E8%B5%AB%E5%85%B0%E5%BE%B7

Published Time: 2015-06-24T01:08:01Z

Markdown Content:
| 汤姆·霍兰德
Tom Holland |
| --- |
| [![Image 19](https://upload.wikimedia.org/wikipedia/commons/thumb/3/3c/Tom_Holland_by_Gage_Skidmore.jpg/220px-Tom_Holland_by_Gage_Skidmore.jpg)](https://zh.wikipedia.org/wiki/File:Tom_Holland_by_Gage_Skidmore.jpg)

2016年在[圣地牙哥国际漫画展](https://zh.wikipedia.org/wiki/%E8%81%96%E5%9C%B0%E7%89%99%E5%93%A5%E5%9C%8B%E9%9A%9B%E6%BC%AB%E7%95%AB%E5%B1%95 "圣地牙哥国际漫画展")的霍兰德



 |
| 男演员 |
| 昵称 | 荷兰弟[\[1\]](https://zh.wikipedia.org/zh-hans/%E6%B1%A4%E5%A7%86%C2%B7%E8%B5%AB%E5%85%B0%E5%BE%B7#cite_note-1) |
| 出生 | 汤玛斯·史丹利·霍兰德
（Thomas Stanley Holland）[\[2\]](https://zh.wikipedia.org/zh-hans/%E6%B1%A4%E5%A7%86%C2%B7%E8%B5%AB%E5%85%B0%E5%BE%B7#cite_note-2)


1996年6月1日（28岁）

英国[英格兰](https://zh.wikipedia.org/wiki/%E8%8B%B1%E6%A0%BC%E8%98%AD "英格兰")[泰晤士河畔金斯顿](https://zh.wikipedia.org/wiki/%E6%B3%B0%E6%99%A4......</div>
</details>

<details>
<summary>第2份搜索结果 [源自google搜索] （为什么汤姆赫兰德被称为荷兰弟？）：</summary>
<div class="search_result">https://www.zhihu.com/question/363988307</div>
<div class="search_result">Title: 为什么汤姆赫兰德被称为荷兰弟？ - 知乎

URL Source: https://www.zhihu.com/question/363988307

Markdown Content:
要说漫威演员里面，谁是最牛的存在，不好说，各有各的看法，但要说谁是最能剧透的，毫无疑问，是我们的汤姆赫兰德荷兰弟，可以说，他算得上是把剧透给玩明白了，先后剧透了不少的电影桥段，以至于漫威后面像防贼一样防着人家荷兰弟，可大家知道吗？你永远想象不到荷兰弟的嘴巴到底有多能漏风？

![Image 9](https://pica.zhimg.com/50/v2-a0aa9972315519ec4975f974f01fc6ca_720w.jpg?source=1def8aca)

故事要回到《侏罗纪世界2》的筹备期间，当时，荷兰弟也参与了面试，计划在剧中饰演一个角色，原本，这也没啥，这都是好莱坞的传统了，可是，当时的导演胡安根本不知道荷兰弟的“风光伟绩”，于是乎，人家便屁颠屁颠把侏罗纪世界2的资料拿过来给荷兰弟，虽然，后面没有让荷兰弟出演这部电影，但导演似乎忘了他的嘴巴是开过光的。

![Image 10](https://picx.zhimg.com/50/v2-1da72b482c6a44e1826abb430d95a062_720w.jpg?source=1def8aca)

荷兰弟把剧情刻在了脑子
......</div>
</details>

<details>
<summary>第3份搜索结果 [源自google搜索] （爱戴名表被喷配不上赞达亚，荷兰弟曝近照气质大变，2）：</summary>
<div class="search_result">https://www.sohu.com/a/580380519_120702487</div>
<div class="search_result">Title: 爱戴名表被喷配不上赞达亚，荷兰弟曝近照气质大变，26岁资产惊人_蜘蛛侠_手表_罗伯特·唐尼

URL Source: https://www.sohu.com/a/580380519_120702487

Markdown Content:
2022-08-27 19:00 来源: [BEGEEL宾爵表](https://www.sohu.com/a/580380519_120702487?spm=smpc.content-abroad.content.1.1739375950559fBhgNpP)

发布于：广东省

近日，大家熟悉的荷兰弟，也就演漫威超级英雄“蜘蛛侠”而走红的英国男星汤姆·赫兰德（Tom Holland），最近在没有任何预警的情况下宣布自己暂停使用社交媒体，原因网络暴力已经严重影响到他的心理健康了。虽然自出演蜘蛛侠以来，对荷兰弟的骂声就没停过，但不可否认他确实是一位才貌双全的好演员，同时也是一位拥有高雅品味的地道英伦绅士，从他近年名表收藏的趋势也能略知一二。

![Image 37](https://p5.itc.cn/q_70/images03/20220827/86aca867047b4119ba96a59e33d2d387.jpeg)

2016年，《美国队长3：内战》上映，汤姆·赫兰德扮演的“史上最嫩”蜘蛛侠也正式登场。这个美国普通学生，由于意外被一只受过放射性感染的蜘蛛咬到，并因此获得超能力，化身邻居英雄蜘蛛侠警恶惩奸。和蜘蛛侠彼得·帕克一样，当时年仅20岁的荷兰弟无论戏里戏外的穿搭都是少年感十足，走的阳光邻家大男孩路线，手上戴的最多的就是来自卡西欧的电子表，还有来自Nixon sentry的手表，千元级别甚至是百元级。

20岁的荷兰弟走的是邻家大男孩路线

![Image 38](https://p3.itc.cn/q_70/images03/20220827/aded82ecfb1d439a8fd4741b49a8eb9b.png)

随着荷兰弟主演的《蜘蛛侠：英雄归来》上演，第三代蜘蛛侠的话痨性格和年轻活力的形象瞬间圈粉无数。荷兰弟的知名度和演艺收入都大幅度增长，他的穿衣品味也渐渐从稚嫩少年风转变成轻熟绅士风。从简单的T恤短袖搭配牛仔裤，开始向更加丰富的造型发展，其中变化最明显的就是他手腕上的表。

荷兰弟的衣品日......</div>
</details>

<details>
<summary>第4份搜索结果 [源自google搜索] （荷兰弟居然要休息一年，因演戏演到精神分裂…）：</summary>
<div class="search_result">https://www.sohu.com/a/683718058_544020</div>
<div class="search_result">Title: 荷兰弟居然要休息一年，因演戏演到精神分裂…_Holland_Tom_工作

URL Source: https://www.sohu.com/a/683718058_544020

Markdown Content:
荷兰弟居然要休息一年，因演戏演到精神分裂…\_Holland\_Tom\_工作
===============

*   [](http://www.sohu.com/?spm=smpc.content-abroad.nav.1.1739375954055TcEvWsY)
*   [新闻](http://news.sohu.com/?spm=smpc.content-abroad.nav.2.1739375954055TcEvWsY)
*   [体育](http://sports.sohu.com/?spm=smpc.content-abroad.nav.3.1739375954055TcEvWsY)
*   [汽车](http://auto.sohu.com/?spm=smpc.content-abroad.nav.4.1739375954055TcEvWsY)
*   [房产](http://www.focus.cn/?spm=smpc.content-abroad.nav.5.1739375954055TcEvWsY)
*   [旅游](http://travel.sohu.com/?spm=smpc.content-abroad.nav.6.1739375954055TcEvWsY)
*   [教育](http://learning.sohu.com/?spm=smpc.content-abroad.nav.7.1739375954055TcEvWsY)
*   [时尚](http://fashion.sohu.com/?spm=smpc.content-abroad.nav.8.1739375954055TcEvWsY)
*   [科技](http://it.sohu.com/?spm=smpc.content-abroad.nav.9.1739375954055TcEvWsY)
*   [财经](http://business.sohu.com/?spm=smpc.content-abroad.nav.10.17393759......</div>
</details>

"""
def validate_path():
    import os, sys

    os.path.dirname(__file__)
    root_dir_assume = os.path.abspath(os.path.dirname(__file__) + "/..")
    os.chdir(root_dir_assume)
    sys.path.append(root_dir_assume)


validate_path()  # validate path so you can run from base directory
from toolbox import markdown_convertion
# from shared_utils.advanced_markdown_format import markdown_convertion_for_file
from shared_utils.advanced_markdown_format import close_up_code_segment_during_stream
# with open("gpt_log/default_user/shared/2024-04-22-01-27-43.zip.extract/translated_markdown.md", "r", encoding="utf-8") as f:
    # md = f.read()
md = close_up_code_segment_during_stream(md)
html = markdown_convertion(md)
# print(html)
with open("test.html", "w", encoding="utf-8") as f:
    f.write(html)


# TODO: 列出10个经典名著
