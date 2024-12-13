import os


def init_task():
    """
    if welcome.js is in /themes folder, empty it
    """
    if os.path.exists('themes/welcome.js'):
        with open('themes/welcome.js', 'w') as f:
            f.write('')
    print('Task initialized')