import json
import pymysql
import pandas as pd
from sshtunnel import SSHTunnelForwarder
from flashtext import KeywordProcessor
from collections import Counter

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
    cursor.execute("select * from so_title limit 0,1000")
    output = cursor.fetchall()
    SO_title_list = []
    for i in output:
        d = {}
        d["id"] = i[0]
        d["title"] = i[2]
        SO_title_list.append(d)
    cursor.execute("select * from so_title limit 9000,10000")
    output = cursor.fetchall()
    for i in output:
        d = {}
        d["id"] = i[0]
        d["title"] = i[2]
        SO_title_list.append(d)
    cursor.execute("select * from so_title limit 20000,21000")
    output = cursor.fetchall()
    for i in output:
        d = {}
        d["id"] = i[0]
        d["title"] = i[2]
        SO_title_list.append(d)
    cursor.close()
    SO_db.close()
    server.close()
    return SO_title_list

def often_use_words(keyword_list,text_list):
    # 初始化关键字处理器
    keyword_processor = KeywordProcessor()
    # 以list方式添加关键词
    keyword_processor.add_keywords_from_list(keyword_list)
    result_list = []
    for i in text_list:
        k = keyword_processor.extract_keywords(i["title"])
        result_list.append(k)
    word_list = []
    for j in result_list:
        for k in j:
            word_list.append(k)
    result = Counter(word_list)
    result = result.most_common(len(result))
    often_use_words = []
    for item in result:
        if(item[1]>4):
            often_use_words.append(item[0])
    return often_use_words

if __name__ == '__main__':
    python_library_name = get_python_library_name()
    SO_title = get_SO_title()
    words = often_use_words(python_library_name,SO_title)
    # print(words)
    # print(len(words))
    data = pd.DataFrame(data=words)
    data.to_csv('often_use_word.csv',index=False)
