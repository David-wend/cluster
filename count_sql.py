# coding=utf-8

from pylab import *

mpl.rcParams["font.sans-serif"] = ["SimHei"]
mpl.rcParams["axes.unicode_minus"] = False
import sql_tool
from datetime import datetime
import csv
from pymongo import MongoClient
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

time_format = "%Y-%m-%d %H:%M:%S"

if __name__ == '__main__':

    # sql = "select news_website_id, count(*) from news group by news_website_id"
    sql = "select news_website_id, news_datetime, news_website_type from news "
    rows = sql_tool.select(sql)
    website = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}}
    tran_dic = {u"社会": 1, u"国际": 2, u"财经": 3, u"体育": 4, u"娱乐": 5, u"汽车": 6, u"科技": 7, u"军事": 8, u"综合": 9, u"其他": 10}
    type_index = [u"社会", u"国际", u"财经", u"体育", u"娱乐", u"汽车", u"科技", u"军事", u"综合", u"其他", ]
    website_index = [u"腾讯", u"网易", u"搜狐", u"新浪", u"凤凰", u"今日"]
    type_dic = {1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}, 9: {}, 10: {}}
    word_class_relative = {u"体育": u"体育", u"健康": u"其他", u"军事": u"军事", u"减肥": u"其他", u"动漫": u"其他",
                           u"历史": u"综合", u"商业": u"财经", u"国内": u"社会", u"国际": u"国际", u"头条新闻": u"社会",
                           u"奇葩": u"其他", u"娱乐": u"娱乐", u"家居": u"其他", u"情感": u"其他", u"房产": u"其他",
                           u"探索": u"综合", u"故事": u"其他", u"教育": u"综合", u"数码": u"科技", u"文化": u"综合",
                           u"旅游": u"综合", u"时尚": u"娱乐", u"星座": u"综合", u"汽车": u"汽车", u"法律": u"综合",
                           u"游戏": u"娱乐", u"生活": u"综合", u"社会": u"社会", u"科技": u"科技", u"美文": u"综合",
                           u"财经": u"财经", u"美食": u"综合"}
    print len(rows)
    for row in rows:
        try:
            if row[1].month < 10:
                time_str = str(row[1].year) + "-0" + str(row[1].month)
            else:
                time_str = str(row[1].year) + "-" + str(row[1].month)
            website[row[0]][time_str] = website[row[0]].get(time_str, 0) + 1
            type_dic[tran_dic[word_class_relative.get(row[2], u"其他")]][time_str] = type_dic[
                                                                                       tran_dic[word_class_relative.get(
                                                                                           row[2], u"其他")]].get(
                time_str, 0) + 1
        except AttributeError:
            continue

    conn = MongoClient('192.168.235.36', 27017)
    db = conn.sea_data

    mongodb_result = db.news.find()
    mongodb_num = 0
    for i in mongodb_result:
        mongodb_num += 1
        try:
            time = datetime.strptime(i["publish_time"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                time = datetime.strptime(i["publish_time"], "%Y-%m-%d %H:%M")
            except ValueError:

                match_obj = re.search(u"(\d*?)年(\d*?)月(\d*?)日", i["publish_time"], flags=0)
                # print i["publish_time"], match_obj.groups()
                time = datetime(int(match_obj.group(1)), int(match_obj.group(2)), int(match_obj.group(3)), 0, 0,
                                0, 0)
        if time.month < 10:
            time_str = str(time.year) + "-0" + str(time.month)
        else:
            time_str = str(time.year) + "-" + str(time.month)
        website[int(i["news_website_id"])][time_str] = website[int(i["news_website_id"])].get(time_str, 0) + 1
        type_dic[tran_dic[word_class_relative.get(i["news_type"], u"其他")]][time_str] = type_dic[
                                                                                           tran_dic[
                                                                                               word_class_relative.get(
                                                                                                   i["news_type"],
                                                                                                   u"其他")]].get(
            time_str,
            0) + 1

    print mongodb_num

    csvfile = file('news_web.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(['报道量', '腾讯新闻', '网易新闻', '搜狐新闻', '新浪新闻', '凤凰新闻', '今日头条'])
    all_data = []
    temp_data = []
    for i in range(2014, 2018):
        for j in range(1, 13):
            if j < 10:
                time_str = str(i) + "-0" + str(j)
            else:
                time_str = str(i) + "-" + str(j)
            temp_data.append(time_str)
    all_data.append(temp_data)

    website_flag = []
    for it in website.items():
        website_flag.append(int(it[0]))
        temp_data = []
        for i in range(2014, 2018):
            for j in range(1, 13):
                if j < 10:
                    time_str = str(i) + "-0" + str(j)
                else:
                    time_str = str(i) + "-" + str(j)
                if time_str in it[1]:
                    temp_data.append(it[1][time_str])
                else:
                    temp_data.append(0)
        all_data.append(temp_data)

    color = ["b", "g", "r", "c", "m", "y", "k", "b--", "g--", "r--", "c--", "m--", "y--", "k--"]
    num = 0
    x = range(len(all_data[0]))
    plt.figure(figsize=(8, 4))  # 创建绘图对象
    print len(all_data)
    for d in all_data[1:]:
        plt.plot(x, d, color[num], linewidth=1, label=website_index[website_flag[num] - 1])  # 在当前绘图对象绘图（X轴，Y轴，蓝色虚线，线宽度）
        plt.xticks(x, all_data[0], rotation=45)
        plt.xlabel("year-month")  # X轴标签
        plt.ylabel("news_num")  # Y轴标签
        plt.margins(0.08)
        plt.title("news'num line chart")  # 图标题
        num += 1
    plt.show()  # 显示图

    all_data = np.array(all_data).T
    writer.writerows(all_data)
    csvfile.close()

    csvfile = file('news_type.csv', 'wb')
    writer = csv.writer(csvfile)
    writer.writerow(['报道量', '社会', '国际', '财经', '体育', '娱乐', '汽车', '科技', '军事', '综合', '其他'])

    all_data = []
    temp_data = []
    for i in range(2014, 2018):
        for j in range(1, 13):
            if j < 10:
                time_str = str(i) + "-0" + str(j)
            else:
                time_str = str(i) + "-" + str(j)
            temp_data.append(time_str)
    all_data.append(temp_data)

    type_flag = []
    for it in type_dic.items():
        type_flag.append(int(it[0]))
        temp_data = []
        for i in range(2014, 2018):
            for j in range(1, 13):
                if j < 10:
                    time_str = str(i) + "-0" + str(j)
                else:
                    time_str = str(i) + "-" + str(j)
                if time_str in it[1]:
                    temp_data.append(it[1][time_str])
                else:
                    temp_data.append(0)
        all_data.append(temp_data)
    print len(all_data)

    num = 0
    x = range(len(all_data[0]))
    plt.figure(figsize=(8, 4))  # 创建绘图对象
    for d in all_data[1:]:
        # type_index[type_flag[num] - 1]
        plt.plot(x, d, color[num], linewidth=1, label="t")  # 在当前绘图对象绘图（X轴，Y轴，蓝色虚线，线宽度）
        plt.xticks(x, all_data[0], rotation=45)
        plt.xlabel("year-month")  # X轴标签
        plt.ylabel(u"报道量")  # Y轴标签
        plt.margins(0.08)
        plt.title("news'num line chart")  # 图标题
        num += 1
    plt.show()  # 显示图

    # result = sorted(it[1].items(), key=lambda x: x[0])
    # result_str = ""
    # for re_i in result:
    #     all_num += 1
    #     result_str = result_str + re_i[0] + ":" + str(re_i[1]) + " |"
    # print result_str

    all_data = np.array(all_data).T
    writer.writerows(all_data)
    csvfile.close()

# publish_time cmt_id title url photo source_url content source news_website_id news_type _id
