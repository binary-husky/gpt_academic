#! .\venv\
# encoding: utf-8
# @Time   : 2023/9/2
# @Author : Spike
# @Descr   :
import re
import json

from comm_tools import func_box


class QQDocs:

    def __init__(self):
        self.file_info_header = {
            'Host': 'docs.qq.com',
            # 'Cookie': 'RK=uGvhhCQ0zj; ptcz=99c50f94a55160ab18fc6eb8f096b3f8ba5ff39929bd1050b651976e22690272; pac_uid=0_53b2f679b8958; iip=0; pgv_pvid=3226633567; eas_sid=S1Y6E7m5q5G980D7p3Y0V6r1i9; _hjSessionUser_2765497=eyJpZCI6ImE2ZmVkYzQ3LWUxYTItNTNkZC05MjQyLTdjMGE0NTFkNGVjMyIsImNyZWF0ZWQiOjE2NzY5NzM5MjIxNDksImV4aXN0aW5nIjpmYWxzZX0=; _ga=GA1.2.672540206.1676973925; fingerprint=25068f269dc748cfa1f72b18c9bb567485; traceid=5c93285746; TOK=5c932857469d443e; hashkey=5c932857; pgv_info=ssid=s1566934721485879; low_login_enable=1; uin=o2411123479; skey=@RLRg3Do1o; luin=o2411123479; lskey=00010000028f61e566ebc077aaf94f4d0d3710de98d0c5aa880aef892ca4b6f9fb91e1d00a68532db2764d7c; p_uin=o2411123479; pt4_token=lz-mBvVtcG*phwWovBO2jlUnS*sDLRURsHwxK9pjL8A_; p_skey=AvdKkMELItneZVvg5zevEmFZYlTK9f1x08ha*sR69-w_; p_luin=o2411123479; p_lskey=000400009940d03062ae753a92f6c2a73f81f94bca33f37c6706df4546a5aa32d7d81e61dd0fcdaa2207fca4; uid=144115211492590730; utype=qq; vfwebqq=addce68ddab2c5a4e3220b3eaef97ef878695bfe5bf61074af22048b997fd3f31f7885037d12d55e; DOC_QQ_APPID=101458937; DOC_QQ_OPENID=7F1531B5C41FFEB3ED1AC333D7FC65DC; env_id=gray-pct50; gray_user=true; DOC_SID=6709e087993a4c13a8f4fb4959847db0e6ec453fe1924b549847b98a9e814ce5; SID=6709e087993a4c13a8f4fb4959847db0e6ec453fe1924b549847b98a9e814ce5; uid_key=EOP1mMQHGixKNE9lMWNNYmtpejZHZEVZNUNrSzE4WHpXcWVCdjYyYTFHTG9rK2l5ZFVzPSJISVFQZGMRpDexb8grhGKnpwXwY4nhwrKrS%2FjKVVKPaBjNBpA%2Fst%2BPOBtPPPCvpU7xEdHxZNhXKvAGgvuahRO05oQi4C8Mzl0%2BKPTH36gG; optimal_cdn_domain=docs2.gtimg.com; loginTime=1693665288205; tgw_l7_route=cc6311fb2d0a9056eacc27e331f5e16a',
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Microsoft Edge";v="116"',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.62',
            'referer': 'https://docs.qq.com/',
            'accept-language': 'en-US,en;q=0.9,ja;q=0.8',
        }
        self.file_info_params = {
            'noEscape': '1',
            'id': 'DS0VIVXZ4TGZIdERw',
            'normal': '1',
            'outformat': '1',
            'startrow': '0',
            'endrow': '60',
            'wb': '1',
            'nowb': '0',
            'callback': 'clientVarsCallback',
        }
        self.file_info_url = 'https://docs.qq.com/dop-api/opendoc'
        self.re_pattern = re.compile(rf'{re.escape(self.file_info_params["callback"])}\((.*?)\)')
        self.file_info_dict = {
            'file_tag': '',
            'file_name': '',
            'file_type': ''
        }


    def get_file_info(self):
        response = requests.get(self.file_info_url, params=self.file_info_params,
                                headers=self.file_info_header,
                                verify=False)
        json_resp = self.re_pattern.findall(response.text)
        if json_resp:
            print(json_resp[0])





import requests

qqdocs = QQDocs()


qqdocs.get_file_info()



