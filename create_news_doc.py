# coding=utf-8

import Inverted_index
import doc_proccess
import tool
import sql_tool
from pymongo import MongoClient
from datetime import datetime
import re
import sl_tool
import remove_duplicate
import count


def connect_mongodb(sql):
    tool.write_file("./dict/doc.txt", [], "w")
    conn = MongoClient('192.168.235.36', 27017)
    db = conn.sea_data
    num = 0
    # sql ={'publish_time': {"$gt": "2017-03-01 00:00:00", "$lte": "2017-03-31 00:00:00"}}
    for i in db.news.find(sql):
        print i


def insert_doc_from_mongodb(sql):
    tool.write_file("./dict/doc.txt", [], "w")
    conn = MongoClient('192.168.235.36', 27017)
    db = conn.sea_data
    lasted_id = sl_tool.load_lasted_id()
    num = lasted_id["news_id"]
    temp_relative = []
    doc_str = []
    for i in db.news.find(sql):
        news_id = num
        temp_relative.append(str(num) + "@@@@" + i["cmt_id"])
        num += 1
        title = i["title"]
        content = re.split(r"\r|\n|\r\n", i["content"])[0]
        time_str = "-".join(re.split(ur"年|月", i["publish_time"].replace(u"日", " ")))
        try:
            time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except:
            try:
                time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            except:
                print time_str
                continue
        news_type = i["news_type"]
        d = doc_proccess.Doc(title, content, news_type, time, news_id)
        doc_str.append(d.__str__())
        print d.__str__()
        # print title + 'done'
    tool.write_file("./dict/doc.txt", doc_str, "w")
    tool.write_file("./dict/cmt_id_relative.txt", temp_relative, "w")
    lasted_id["news_id"] = num
    sl_tool.save_lasted_id(lasted_id)


def insert_doc_from_db(sql):
    data = sql_tool.select(sql)
    tool.write_file("./dict/doc.txt", [], "w")
    doc_str = []
    for row in data:
        news_id = row[0]
        title = row[1]
        content = re.split(r"\r|\n|\r\n", row[2])[0]
        # content = row[2].split("\n")[0]
        datetime = row[3]
        news_type = row[4]
        d = doc_proccess.Doc(title, content, news_type, datetime, news_id)
        doc_str.append(d.__str__())
        print title + 'done'
    tool.write_file("./dict/doc.txt", doc_str, "a")


def transform_doc():
    i = Inverted_index.InvertDic()
    # i.init_all_dic()
    doc_rows = tool.get_file_lines("./dict/filter_doc.txt")
    for row in doc_rows:
        try:
            temp = row.split("@@@@", 1)
            news = temp[1].split("##", 3)
            title = news[0].decode("UTF-8")
            content = news[3].decode("UTF-8")
            datetime = news[2]
            news_type = news[1].decode("UTF-8")
            doc_id = int(temp[0])
            d = doc_proccess.Doc(title, content, news_type, datetime, doc_id)
            i.update_invert_index(d, flag=0)
            print news[0] + 'done'
        except:
            print row
    i.save_all_dic()


if __name__ == '__main__':
    # news_type_list = ['军事', '体育', '科技', '娱乐', '社会', '国际', '国内', '数码']
    # news_type = '数码'
    # sql = "SELECT `news_id` , `news_title` , `news_content` , `news_datetime` , `news_website_type` FROM `news` where" \
    #       " news_datetime > '2016-12-01 00:00:00' and `news_datetime` < '2016-12-31 00:00:00' " \
    #       "order by 'news_datetime' asc "
    # insert_doc_from_db(sql)
    # sql = {'publish_time': {"$gt": "2017-04-15 00:00:01", "$lte": "2017-04-31 00:00:00"}}
    sql = {"title": {'$regex': '.美联航.'}}
    insert_doc_from_mongodb(sql)
    remove_duplicate.remove_duplicate()
    transform_doc()
    count.get_co_name()
    count.lan_de_qi_ming()
