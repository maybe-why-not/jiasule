#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, json, base64, sqlite3, subprocess, win32api, win32gui
from pymouse import PyMouse
from pykeyboard import PyKeyboard
from win32crypt import CryptUnprotectData
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_string(local_state):
    with open(local_state, 'r', encoding='utf-8') as f:
        s = json.load(f)['os_crypt']['encrypted_key']
    return s

def pull_the_key(base64_encrypted_key):
    encrypted_key_with_header = base64.b64decode(base64_encrypted_key)
    encrypted_key = encrypted_key_with_header[5:]
    key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return key

def decrypt_string(key, data):
    nonce, cipherbytes = data[3:15], data[15:]
    aesgcm = AESGCM(key)
    plainbytes = aesgcm.decrypt(nonce, cipherbytes, None)
    plaintext = plainbytes.decode('utf-8')
    return plaintext

def get_cookie_from_chrome(host='zoomeye.org'):
    local_state = os.environ['LOCALAPPDATA'] + r'\Google\Chrome\User Data\Local State'
    cookie_path = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Cookies"
    
    sql = "select host_key,name,encrypted_value from cookies where host_key like '%"+host+"'"

    with sqlite3.connect(cookie_path) as conn:
        cu = conn.cursor()
        res = cu.execute(sql).fetchall()
        cu.close()
        cookies = {}
        key = pull_the_key(get_string(local_state))
        for host_key, name, encrypted_value in res:
            if encrypted_value[0:3] == b'v10':
                cookies[name] = decrypt_string(key, encrypted_value)
            else:
                cookies[name] = CryptUnprotectData(encrypted_value)[1].decode()

        # print(cookies)
        return cookies

#打开新窗口
subprocess.Popen('chrome', stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0x08000000)
handle = win32gui.FindWindow(None, '新标签页 - Google Chrome')
#先获取句柄方便后续操作
#打开浏览器登录好账号
while(1):
    name = input("Are you really?[Y|N]")
    if (name == 'Y') or (name == 'y'):
        break

m = PyMouse()
k = PyKeyboard()
#这是一个单击屏幕中心并按f5的示例：
x_dim, y_dim = m.screen_size()
m.click(int(x_dim/2), int(y_dim/2), 1)
k.tap_key(k.function_keys[5])
time.sleep(1)
cookies = get_cookie_from_chrome()
print(cookies)
