# encoding: utf-8
# @Time   : 2024/1/17
# @Author : Spike
# @Descr   : from https://github.com/mufeng510/Free-ChatGPT-API @mufeng510
import os.path

import requests
import random
import string
import time
import re
import json
from os import path


class PandoraServer:

    def __init__(self, base_host):
        self.base_host = base_host

    def get_access_token(self, username, password):
        payload = {'username': username, 'password': password}
        resp = requests.post(self.base_host + '/api/auth/login', data=payload)
        if resp.status_code == 200:
            print('Login success: {}'.format(username))
            return resp.json().get('access_token')
        else:
            err_str = resp.text.replace('\n', '').replace('\r', '').strip()
            print('Login failed: {}, {}'.format(username, err_str))
            return None

    def get_share_token(self, unique_name, access_token, expires_in):
        data = {'unique_name': unique_name, 'access_token': access_token, 'expires_in': expires_in}
        resp = requests.post(self.base_host + '/api/token/register', data=data)
        if resp.status_code == 200:
            share_token = resp.json().get('token_key')
            print('share token: {}'.format(share_token))
            return share_token
        else:
            err_str = resp.text.replace('\n', '').replace('\r', '').strip()
            print('share token failed: {}'.format(err_str))
            return None

    def read_pool_token(self, pool_token_file):
        # 如果已有pool token则更新, 没有则生成。
        if path.exists(pool_token_file):
            with open(pool_token_file, 'r', encoding='utf-8') as f:
                pool_token = f.read().strip()
            if (re.compile(r'pk-[0-9a-zA-Z_\-]{43}').match(pool_token)):
                print('已存在: pool token: {}'.format(pool_token))
                return pool_token
            else:
                print('pool token: 格式不正确，将重新生成')
                return ""
        else:
            return ""

    def update_pool_token(self, share_token_keys, pool_token, pool_token_file):
        filtered_tokens = [token for token in share_token_keys if re.match(r'fk-[0-9a-zA-Z_\-]{43}', token)]
        if not filtered_tokens:
            print('无可用账号，请检查后重试')
            return

        data = {'share_tokens': '\n'.join(filtered_tokens), 'pool_token': pool_token}
        resp = requests.post(self.base_host + '/api/pool/update', data=data)
        if resp.status_code == 200:
            result = resp.json()
            print('pool token 更新结果: count:{} pool_token:{}'.format(result['count'], result['pool_token']))
            with open(pool_token_file, 'w', encoding='utf-8') as f:
                f.write(result['pool_token'])
        else:
            print('pool token 更新失败')

    def save_tokens(self, tokens_file, access_token_keys):
        tokens_data = {f"user-{i + 1}": {"token": token, "shared": True, "show_user_info": False} for i, token in
                       enumerate(access_token_keys)}
        with open(tokens_file, 'w', encoding='utf-8') as f:
            json.dump(tokens_data, f, indent=2)

    def generate_random_string(self, length):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for _ in range(length))

    def read_credentials(self, credentials_file):
        with open(credentials_file, 'r', encoding='utf-8') as f:
            credentials = [line.strip().split(',', 1) for line in f if ',' in line]
        return credentials

    def get_sees_keys(self, username, password):
        payload = {'username': username, 'password': password, 'prompt': 'login'}
        resp = requests.post(self.base_host + '/api/auth/platform/login',
                             data=payload, verify=False).json()
        sess_key = resp['login_info']['user']['session']['sensitive_id']
        return sess_key

    def reader_save_sees(self, user_profile):
        interval = "----"
        with open(user_profile, 'r') as f:
            user_content = f.read()
        if interval not in user_content:
            interval = ','
        new_content = ''
        for u in user_content.splitlines():
            username = u.split(interval)[0]
            password = u.split(interval)[1]
            sees_key = self.get_sees_keys(username, password)
            print(f'{username} {interval} {sees_key}')
            new_content += f"{interval}".join([username, password, sees_key]) + '\n'
        new_file = os.path.join(os.path.dirname(user_profile), 'reader_sees.txt')
        with open(new_file, 'w') as f:
            f.write(new_content + '\n')
        print(f'Done: {new_file}')


if __name__ == '__main__':
    base_host = 'http://127.0.0.1:8181/qqrr1233333r'
    pandora = PandoraServer(base_host)
    pandora.reader_save_sees('../users_data/test.key')