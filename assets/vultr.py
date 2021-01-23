#!/usr/bin/python3
# -*- coding: UTF-8 -*-


import re
import os
import shutil
from pathlib import Path

home = Path.home()

config = {"ssh_port": 0,
          "ssh_key_file": ".ssh/authorized_keys",
          "ss_port": 0,
          "ss_password": "123456"}


def load_config():
    with open(home / "vultr.config") as fd:
        for line in fd.readlines():
            split_index = line.find("=")
            config[(line[0:split_index]).strip()] = (line[split_index + 1:]).strip()


def config_ssh():
    ssh_conf = "/etc/ssh/sshd_config"
    ssh_bak = ssh_conf + ".bak"

    ssh_key_file_re = r"\#?(AuthorizedKeysFile)(?:\s+\S+)+\n"
    ssh_port_re = r"\#?(Port)\s+\d+\s*\n"
    ssh_password_allow = r"\#?(PasswordAuthentication)\s+\S+\s*\n"

    is_port_set = False
    is_key_file_set = False

    if not os.path.exists(ssh_bak):
        # create backup file
        print("back up sshd config:{}".format(ssh_bak))
        shutil.copy(ssh_conf, ssh_bak)

    with open(ssh_bak, mode='r') as fsrc, open(ssh_conf, mode='w') as fdest:
        for line in fsrc.readlines():
            if re.search(ssh_key_file_re, line) is not None:
                line = re.sub(ssh_key_file_re, "AuthorizedKeysFile {}\n".format(config["ssh_key_file"]), line)
                is_key_file_set = True

            if re.search(ssh_port_re, line) is not None:
                line = re.sub(ssh_port_re, "Port {}\n".format(config["ssh_port"]), line)
                is_port_set = True

            # close paasword authentication
            if re.search(ssh_password_allow, line) is not None and is_key_file_set:
                line = re.sub(ssh_password_allow, "PasswordAuthentication no\n", line)
            fdest.write(line)
        fdest.write("#abb")
        fsrc.close()
        fdest.close()

    if is_key_file_set and is_port_set:
        os.system("ufw disable")
        os.system("ufw allow {}".format(config["ssh_port"]))
        os.system("ufw delete allow ssh")
        os.system("ufw delete allow 22")
        os.system("ufw enable")
        os.system("sudo /etc/init.d/ssh restart")

def config_ss():
    ss_config_dir = home / "ss-config"
    ss_config_file = ss_config_dir / "6ss.json"
    ss_start_file = ss_config_dir / "6ss.sh"
    shadow_sock_config = """{{
    "server"     :"::",
    "local_port" : 1080,
    "port_password":{{
        "{ss_port}" : "{ss_password}"
    }},
    "timeout": 2048,
    "method"     : "aes-256-cfb"
}}"""

    shadow_sock_start_sh = """#!/bin/sh
sudo ssserver -d stop
sudo ssserver -c {} -d start"""

    try:
        os.makedirs(ss_config_dir)
    except FileExistsError as e:
        print("directory exists")
    ss_configf = open(ss_config_file,"w")
    ss_configf.write(shadow_sock_config.format(**config))
    ss_configf.close()

    ss_start_shf = open(ss_start_file,"w")
    ss_start_shf.write(shadow_sock_start_sh.format(ss_config_file))
    ss_start_shf.close()

    os.system("sh {}".format(ss_start_file))
    os.system("ufw allow {}".format(config["ss_port"]))

# because of  openssl  update to 1.1.0 , you must modify file:
# /usr/local/lib/python3.6/dist-packages/shadowsocks/crypto/openssl.py
# replace EVP_CIPHER_CTX_cleanup to EVP_CIPHER_CTX_reset
def modify_ss_crypto():
    ss_open_ssl_py = "/usr/local/lib/python3.6/dist-packages/shadowsocks/crypto/openssl.py"
    ss_open_ssl_py_bak = ss_open_ssl_py +".bak"
    if not os.path.exists(ss_open_ssl_py_bak):
        # create backup file
        print("back up ss openssl.py:{}".format(ss_open_ssl_py_bak))
        shutil.copy(ss_open_ssl_py, ss_open_ssl_py_bak)

    shutil.copy(ss_open_ssl_py, ss_open_ssl_py_bak)
    with open(ss_open_ssl_py_bak, mode='r') as fsrc, open(ss_open_ssl_py, mode='w') as fdest:
        for line in fsrc.readlines():
           fdest.write(line.replace("EVP_CIPHER_CTX_cleanup","EVP_CIPHER_CTX_reset"))
    fsrc.close()
    fdest.close()


load_config()
config_ssh()
modify_ss_crypto()
config_ss()
