#! .\venv\
# encoding: utf-8
# @Time   : 2023/8/30
# @Author : Spike
# @Descr   :
from comm_tools import func_box
from comm_tools import toolbox

WEB_PORT = toolbox.get_conf('WEB_PORT')
PORT = toolbox.find_free_port() if WEB_PORT <= 0 else WEB_PORT

def check_proxy_free(port):
    if not port: port = PORT
    proxy_state = func_box.Shell(f'lsof -i :{port}').read()[1].splitlines()
    if proxy_state != ["", ""]:
        print('Kill Old Server')
        for i in proxy_state[1:]:
            func_box.Shell(f'kill -9 {i.split()[1]}').read()
        import time
        time.sleep(5)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='命令行工具')
    parser.add_argument('--clear', metavar='text', help='**清理端口')
    args = parser.parse_args()
    if args.clear:
        check_proxy_free(args.clear)
    else:
        print('必须选一个带**')

if __name__ == '__main__':
    main()