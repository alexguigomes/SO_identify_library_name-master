import json
import sqlite3
import pymysql
import pandas as pd
import numpy as np
from sshtunnel import SSHTunnelForwarder
from flashtext import KeywordProcessor
from collections import Counter

def store_python_library_name():
    library_db = sqlite3.connect("D:\Code\python_code\markdown\pypi.db")
    cursor = library_db.cursor()
    cursor.execute("select * from packages")
    data = cursor.fetchall()
    library_name_list = []
    num = 0
    for i in data:
        d = {}
        d["id"] = num
        num = num + 1
        package_name = i[0]  # package name
        d["name"] = package_name
        library_name_list.append(d)
    cursor.close()
    library_db.close()
    with open('python_library_name.json', 'w', encoding='utf-8') as file:
        json.dump(library_name_list, file)

def get_python_library_name():
    with open('python_library_name.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    name_list = []
    for i in data:
        name_list.append(i["name"])
    return name_list

def get_SO_title():
    # 通过SSH连接云服务器
    server = SSHTunnelForwarder(
        ssh_address_or_host=('47.116.194.87', 22),  # 云服务器地址IP和端口port
        ssh_username='lmw',  # 云服务器登录账号admin
        ssh_password='cloudfdse',  # 云服务器登录密码password
        remote_bind_address=('localhost', 3306)  # 数据库服务地址ip,一般为localhost和端口port，一般为3306
    )
    # 云服务器开启
    server.start()
    # 云服务器上mysql数据库连接
    SO_db = pymysql.connect(host="127.0.0.1", port=server.local_bind_port, user="root", password="Cloudfdse2022+",
                         database="SECorpus_db", charset='utf8')
    cursor = SO_db.cursor()
    cursor.execute("select * from so_title limit 100,200")
    output = cursor.fetchall()
    SO_title_list = []
    for i in output:
        d = {}
        d["id"] = i[0]
        d["title"] = i[2]
        SO_title_list.append(d)
    cursor.close()
    SO_db.close()
    server.close()
    return SO_title_list

def extract_python_library(keyword_list,text_list):
    # 初始化关键字处理器
    keyword_processor = KeywordProcessor()
    # 以list方式添加关键词
    keyword_processor.add_keywords_from_list(keyword_list)
    # 读取最常使用的三方库名称数据
    file = pd.read_csv('often_use_word.csv')
    words = pd.DataFrame(file)
    words_array = np.array(words)
    words_list = words_array.tolist()
    remove_word_list = []
    for i in words_list:
        remove_word_list.append(i[0])
    result_list = []
    for i in text_list:
        temp = {}
        k1 = keyword_processor.extract_keywords(i["title"])
        k2 = []
        for k in k1:
            if k not in remove_word_list:
                k2.append(k)
        temp["text_id"] = i["id"]
        temp["python_library"] =k2
        result_list.append(temp)
    # for j in result_list:
    #     print(j["text_id"],end=':')
    #     print(j["python_library"])
    with open('SO_title_python_library.json', 'r', encoding='utf-8') as file:
        content = json.load(file)
    for item in result_list:
        content.append(item)
    with open('SO_title_python_library.json', 'w', encoding='utf-8') as file_new:
        json.dump(content, file_new)

if __name__ == '__main__':
    # store_python_library_name()
    python_library_name = get_python_library_name()
    # print(python_library_name)
    # print(len(python_library_name))
    # print(type(python_library_name))
    SO_title = get_SO_title()
    # print(SO_title)
    extract_python_library(python_library_name,SO_title)