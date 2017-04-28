# coding=utf-8

import csv
import sql_tool
from datetime import datetime
import count
import tool
import numpy as np
import jieba.posseg as pseg
import Inverted_index
from collections import Counter
import jieba
import jieba.analyse
import remove_duplicate
from pymongo import MongoClient
import re
import sl_tool

time_format = "%Y-%m-%d %H:%M:%S"


def insert_news():
    conn, cursor = sql_tool.connect_mysql()
    sql = "select news_id, news_website_id, news_website_type, news_url, news_title, news_content, " \
          "news_datetime, news_source, news_source_url, news_image, news_author, news_comment_url_args " \
          "from news where news_id in (select news_id from yunshan_topic_news_relative) and news_id not " \
          "in (select news_id from yunshan_news) limit 9000, 4000"
    news_rows = sql_tool.select(sql)
    sql = "insert into yunshan_news values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, news_rows)


def insert_mongodb_news():
    # file_path_list = ["17-02", "17-03", "17-03-25", "17-04-20", "mlh"]
    file_path_list = ["mlh"]
    cmt_dic = {}
    cmt_re_dic = {}
    cmt_arr = []
    for tp in file_path_list:
        toot_dir = "./dict/" + tp + "/cmt_id_relative.txt"
        rows = sl_tool.get_file_lines(toot_dir)
        for row in rows:
            arr = row.split("@@@@")
            cmt_re_dic[int(arr[0])] = arr[1]
            cmt_dic[arr[1]] = int(arr[0])

    sql = "select news_id from yunshan_topic_news_relative"
    rows = sql_tool.select(sql)
    for row in rows:
        if row[0] in cmt_re_dic:
            cmt_arr.append(cmt_re_dic[row[0]])

    cmt_arr = list(set(cmt_arr))
    conn = MongoClient('192.168.235.36', 27017)
    db = conn.sea_data
    mongodb_result = db.news.find(
        {'publish_time': {"$gt": "2016-12-01 00:00:01", "$lte": "2017-04-31 00:00:00"}, 'cmt_id': {'$in': cmt_arr}})
    temp = []
    redu = set([])
    for row in mongodb_result:
        if cmt_dic[row["cmt_id"]] not in redu:
            temp.append(
                [cmt_dic[row["cmt_id"]], row["news_website_id"], row["news_type"], row["url"],
                 row["title"], row["content"], row["publish_time"], row["source"],
                 row["source_url"], row["photo"], "", row["cmt_id"]])
            redu.add(cmt_dic[row["cmt_id"]])

    print len(temp)
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_news values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_topic():
    rows = tool.get_file_lines("./dict/topic_name.txt")
    temp = []
    for row in rows:
        arr = row.split("@@")
        temp.append([int(arr[0]), arr[1], 2, 1, datetime.now(), ""])
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_topic(topic_id, topic_name, topic_hot_weight, is_hot, " \
          "topic_datetime, topic_summary) values(%s, %s, %s, %s, %s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_topic_news_relative():
    temp = []
    for line in tool.get_file_lines("./dict/topic_news_relative.txt"):
        arr = line.split("@@")
        temp.append([int(arr[0]), int(arr[1])])
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_topic_news_relative(topic_id, news_id) values(%s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_event_topic_relative():
    temp = []
    for line in tool.get_file_lines("./dict/event_topic_relative.txt"):
        arr = line.split("@@")
        temp.append([int(arr[0]), int(arr[1])])
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_event_topic_relative(event_id, topic_id) values(%s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_event():
    rows = tool.get_file_lines("./dict/event_name.txt")
    temp = []
    for row in rows:
        arr = row.split("@@")
        temp.append([int(arr[0]), arr[1], datetime.now(), ""])
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_event(event_id, event_name, " \
          "event_datetime, event_summary) values(%s, %s, %s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def update_topic_datetime():
    # 这里貌似无法直接update，只能生成语句是手动update
    sql = "select topic_id from yunshan_topic"
    topic_rows = sql_tool.select(sql)
    update_sql = "insert into yunshan_topic (`topic_id`,`topic_datetime`) values "
    for row in topic_rows:
        sql = "select news_datetime from yunshan_news where news_id in " \
              "(select news_id from yunshan_topic_news_relative where topic_id = %d) " \
              "and news_datetime != '0000-00-00 00:00:00' order by news_datetime desc limit 1" % row[0]
        datetime_rows = sql_tool.select(sql)
        try:
            new_datetime = datetime_rows[0][0].strftime("%Y-%m-%d %H:%M:%S")
            update_sql += "(%s, '%s')," % (row[0], new_datetime)
        except IndexError:
            continue
    new_sql = update_sql[:-1] + " on duplicate key update `topic_datetime`=values(`topic_datetime`)"
    sql_tool.execute(new_sql)


def update_event_datetime():
    sql = "select event_id from yunshan_event"
    event_rows = sql_tool.select(sql)
    update_sql = "insert into yunshan_event (`event_id`,`event_datetime`) values "
    for row in event_rows:
        sql = "select topic_datetime from yunshan_topic where topic_id in " \
              "(select topic_id from yunshan_event_topic_relative where event_id = %d) " \
              "and topic_datetime != '0000-00-00 00:00:00' order by topic_datetime desc limit 1" % row[0]
        datetime_rows = sql_tool.select(sql)
        try:
            new_datetime = datetime_rows[0][0].strftime("%Y-%m-%d %H:%M:%S")
            update_sql += "(%s, '%s')," % (row[0], new_datetime)
        except:
            print row[0], datetime_rows
    new_sql = update_sql[:-1] + " on duplicate key update `event_datetime`=values(`event_datetime`)"
    sql_tool.execute(new_sql)


def update_topic_img():
    sql = "select topic_id from yunshan_topic"
    topic_rows = sql_tool.select(sql)
    update_sql = "insert into yunshan_topic (`topic_id`,`topic_img_url`) values "
    for row in topic_rows:
        sql = "select news_image_url from yunshan_news where news_id in " \
              "(select news_id from yunshan_topic_news_relative where topic_id = %d) " \
              "and news_image_url != '' order by news_datetime asc limit 1" % row[0]
        img_rows = sql_tool.select(sql)
        try:
            img_url = img_rows[0][0]
            update_sql += "(%s, '%s')," % (row[0], img_url)
        except:
            print row
    new_sql = update_sql[:-1] + " on duplicate key update `topic_img_url`=values(`topic_img_url`)"
    sql_tool.execute(new_sql)


def update_event_img():
    sql = "select event_id from yunshan_event"
    topic_rows = sql_tool.select(sql)
    update_sql = "insert into yunshan_event (`event_id`,`event_img_url`) values "
    for row in topic_rows:
        sql = "select topic_img_url from yunshan_topic where topic_id in " \
              "(select topic_id from yunshan_event_topic_relative where event_id = %d) " \
              "and topic_img_url != '' order by topic_datetime asc limit 1" % row[0]
        img_rows = sql_tool.select(sql)
        try:
            img_url = img_rows[0][0]
            update_sql += "(%s, '%s')," % (row[0], img_url)
        except:
            print row
    new_sql = update_sql[:-1] + " on duplicate key update `event_img_url`=values(`event_img_url`)"
    sql_tool.execute(new_sql)


def insert_topic_evaluation_object_relative():
    sql = "select topic_id from yunshan_topic where topic_id in (select topic_id " \
          "from yunshan_event_topic_relative where event_id = 4)"
    topic_rows = sql_tool.select(sql)
    print topic_rows
    temp = []
    for row in topic_rows:
        temp.append([row[0], 9])
    conn, cursor = sql_tool.connect_mysql()
    sql = "insert into yunshan_topic_evaluation_object_relative(topic_id, evaluation_object_id) values(%s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_web_num():
    sql = "select topic_id from yunshan_topic where topic_id != 0 and topic_id != 1"
    topic_rows = sql_tool.select(sql)
    temp = []
    conn, cursor = sql_tool.connect_mysql()
    for row in topic_rows:
        arr = [int(x) for x in np.random.random(size=5) * 10]
        temp.append([row[0], arr[0], arr[1], arr[2], arr[3], arr[4]])
    sql = "insert into yunshan_web_num values(%s, %s, %s, %s, %s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_topic_keyword():
    def load_word_index_dic():
        word_dic = {}
        lines = sl_tool.get_file_lines("./word_index.txt")
        for line in lines:
            arr = line.split("@@")
            word_dic[arr[0]] = int(arr[1])
        return word_dic

    def save_word_index_dic(word_dic):
        temp_word = []
        for item in word_dic.items():
            temp_word.append(item[0] + "@@" + str(item[1]))
        sl_tool.write_file("./word_index.txt", temp_word)

    word_index_dic = load_word_index_dic()
    new_word_index_dic = {}
    word_index = len(word_index_dic)
    sql = "select topic_id from yunshan_topic"
    topic_rows = sql_tool.select(sql)
    conn, cursor = sql_tool.connect_mysql()
    for i in topic_rows:
        word_weight_dic = {}
        sql = "select news_title from yunshan_news where news_id in (select news_id from " \
              "yunshan_topic_news_relative where topic_id = %d) order by news_datetime desc" % i
        news_title_rows = sql_tool.select(sql)
        for row in news_title_rows:
            title = row[0]
            key_word_list = jieba.analyse.extract_tags(title, 5)
            for word in key_word_list:
                for ws in pseg.cut(word):
                    ws_de = ws.word.decode("utf-8")
                    if len(ws_de) > 1:
                        if ws_de in word_index_dic:
                            word_weight_dic[word_index_dic[ws_de]] = word_weight_dic.get(word_index_dic[ws_de],
                                                                                         0) / 2.0 + 2
                        else:
                            new_word_index_dic[ws_de] = word_index
                            word_index_dic[ws_de] = word_index
                            word_index += 1
                            word_weight_dic[word_index_dic[ws_de]] = 1

        temp = []
        word_weight_list = sorted(word_weight_dic.items(), key=lambda x: [1], reverse=True)
        for j in word_weight_list:
            temp.append([i, j[0], j[1]])
        sql = "insert into yunshan_topic_keyword_relative values(%s, %s, %s)"
        sql_tool.save_many_into_mysql(conn, cursor, sql, temp)

    temp = []
    for k in new_word_index_dic.items():
        temp.append([k[1], k[0]])
    sql = "insert into yunshan_keyword values(%s, %s)"
    sql_tool.save_many_into_mysql(conn, cursor, sql, temp)
    save_word_index_dic(word_index_dic)


def add_new_word(dictionary, word):
    for i in range(len(word) - 1):
        for j in range(len(word) - i - 1):
            dictionary.add_new_term(word[j:i + j + 1], word[j + 1:j + i + 2])
    return dictionary


def insert_event_key_word_relative():
    sql = "select event_id from yunshan_event"
    event_rows = sql_tool.select(sql)
    conn, cursor = sql_tool.connect_mysql()
    for i in event_rows:
        sql = "select keyword_id, weight from yunshan_topic_keyword_relative where topic_id in " \
              "(select topic_id from yunshan_event_topic_relative where event_id =%d) " % i
        keyword_rows = sql_tool.select(sql)
        temp = []
        for row in keyword_rows:
            temp.append([i, row[0], row[1]])
        sql = "insert into yunshan_event_keyword_relative values(%s, %s, %s)"
        sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def insert_comment():
    sql = "select topic_id from yunshan_topic_news_relative"
    topic_rows = sql_tool.select(sql)
    comment_set = set([])
    for topic_row in topic_rows:
        temp = []
        # sql = "select * from news_comment_emotion_relative where news_id in (select news_id from " \
        #       "yunshan_topic_news_relative where topic_id = %d) group by emotion_id " % topic_row[0]
        sql = "select news_id from yunshan_topic_news_relative where topic_id = %d" % topic_row[0]
        news_rows = sql_tool.select(sql)
        comment_tag = set([])
        for news_row in news_rows:
            # sql = "select b.news_comment_id, b.news_id, b.news_comment_content, b.news_comment_datetime, " \
            #       "b.news_comment_goodnumber, a.emotion_id from news_comment_emotion_relative as a inner join " \
            #       "news_comment as b on a.news_id = b.news_id where a.news_id=%d group by emotion_id " % news_row[0]
            sql = "select b.news_comment_id, b.news_id, b.news_comment_content, b.news_comment_datetime, " \
                  "b.news_comment_goodnumber, a.emotion_id from news_comment_emotion_relative as a inner join " \
                  "news_comment as b on a.news_id = b.news_id AND a.news_comment_id = b.news_comment_id " \
                  "where a.news_id=%d" % news_row[0]
            comment_rows = sql_tool.select(sql)
            for comment_row in comment_rows:
                if comment_row[0] not in comment_set:
                    if comment_row[5] not in comment_tag:
                        temp.append(
                            [comment_row[0], topic_row[0], news_row[0], comment_row[2],
                             datetime.strftime(comment_row[3], time_format), comment_row[4],
                             comment_row[5]])
                        comment_tag.add(comment_row[5])
                        comment_set.add(comment_row[0])

                        # print "insert into yunshan_top_comment values(%s, %s, %s, %s, %s, %s, %s)" % (
                        #     temp[-1][0], temp[-1][1], temp[-1][2], temp[-1][3], temp[-1][4], temp[-1][5], temp[-1][6])
                        # print comment_rows

        sql = "insert into yunshan_top_comment values(%s, %s, %s, %s, %s, %s, %s)"
        conn, cursor = sql_tool.connect_mysql()
        sql_tool.save_many_into_mysql(conn, cursor, sql, temp)


def merge_topic(id_i, id_js):
    # 将第二个话题合并到第一个话题
    for id_j in id_js:
        sql = "update yunshan_topic_news_relative set topic_id = %d where topic_id = %d" % (id_i, id_j)
        sql_tool.execute(sql)
        sql = "delete from yunshan_topic where topic_id = %d " % id_j
        sql_tool.execute(sql)


def merge_all_topic():
    sql = "SELECT a.topic_id, b.topic_id FROM `yunshan_topic` as a  join yunshan_topic as b where " \
          "a.topic_id < b.topic_id and a.topic_name = b.topic_name"
    rows = sql_tool.select(sql)
    for row in rows:
        id_i = row[0]
        id_j = row[1]
        # 将第二个事件合并到第一个事件
        sql = "update yunshan_topic_news_relative set topic_id = %d where topic_id = %d" % (id_i, id_j)
        sql_tool.execute(sql)
        sql = "delete from yunshan_topic where topic_id = %d " % id_j
        sql_tool.execute(sql)


def merge_event(id_i, id_js):
    # 将第二个事件合并到第一个事件
    for id_j in id_js:
        sql = "update yunshan_event_topic_relative set event_id = %d where event_id = %d" % (id_i, id_j)
        sql_tool.execute(sql)
        sql = "delete from yunshan_event where event_id = %d " % id_j
        sql_tool.execute(sql)


def merge_all_event():
    sql = "SELECT a.event_id, b.event_id FROM `yunshan_event` as a  join yunshan_event as b where " \
          "a.event_id < b.event_id and a.event_name = b.event_name"
    rows = sql_tool.select(sql)
    for row in rows:
        event_id_i = row[0]
        event_id_j = row[1]
        # 将第二个事件合并到第一个事件
        sql = "update yunshan_event_topic_relative set event_id = %d where event_id = %d" % (event_id_i, event_id_j)
        sql_tool.execute(sql)
        sql = "delete from yunshan_event where event_id = %d " % event_id_j
        sql_tool.execute(sql)


def delete_event_one(event_id):
    sql = "DELETE FROM yunshan_topic_news_relative WHERE topic_id in " \
          "(select topic_id from yunshan_event_topic_relative where event_id = %d)" % event_id
    sql_tool.execute(sql)
    sql = "DELETE FROM yunshan_topic WHERE topic_id in " \
          "(select topic_id from yunshan_event_topic_relative where event_id = %d)" % event_id
    sql_tool.execute(sql)
    sql = "DELETE FROM yunshan_event_topic_relative WHERE event_id  = %d " % event_id
    sql_tool.execute(sql)
    sql = "DELETE FROM yunshan_event WHERE event_id  = %d " % event_id
    sql_tool.execute(sql)


if __name__ == '__main__':
    pass

    # insert_topic()
    # insert_topic_news_relative()
    # insert_event()
    # insert_event_topic_relative()

    # insert_news()
    # insert_mongodb_news()
    # update_topic_img()
    # update_event_img()
    # update_topic_datetime()
    # update_event_datetime()
    # insert_topic_keyword()
    # insert_event_key_word_relative()
    # insert_web_num()
    # insert_comment()
    # merge_all_event()
    # merge_all_topic()
    # merge_event(67,[92,203,422])
    # delete_event_one(i)

    # conn = MongoClient('192.168.235.36', 27017)
    # db = conn.sea_data
    # sql = {"title": {'$regex': '.美联航.'}}
    # mongodb_result = db.news.find(sql)
    # for t in mongodb_result:
    #     print t
