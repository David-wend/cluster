# coding=utf-8
__author__ = 'david'
import sl_tool
import math

'''
news_gather
similarity_limit;新闻聚类相似度基础阈值
worddir:单词权重词典
flagdir:单词词性词典
speechdir:词性权重词典

'''
similarity_limit = 3.0
speechdir = sl_tool.get_speech_dic()
termdir, flagdir = sl_tool.get_term_dir()
word_class_relative = {u"体育": u"体育", u"健康": u"其他", u"军事": u"军事", u"减肥": u"其他", u"动漫": u"其他",
                       u"历史": u"综合", u"商业": u"财经", u"国内": u"社会", u"国际": u"国际", u"头条新闻": u" 社会",
                       u"奇葩": u"其他", u"娱乐": u"娱乐", u"家居": u"其他", u"情感": u"其他", u"房产": u"其他",
                       u"探索": u"综合", u"故事": u"其他", u"教育": u"综合", u"数码": u"科技", u"文化": u"综合",
                       u"旅游": u"综合", u"时尚": u"娱乐", u"星座": u"综合", u"汽车": u"汽车", u"法律": u"综合",
                       u"游戏": u"娱乐", u"生活": u"综合", u"社会": u"社会", u"科技": u"科技", u"美文": u"综合",
                       u"财经": u"财经", u"美食": u"综合"}

normal_event_relative = {u'社会': 1, u'国际': 2, u'财经': 3, u'体育': 4, u'娱乐': 5,
                         u'汽车': 6, u'科技': 7, u'军事': 8, u'综合': 9, u'其他': 10}

classification = {0: "自然灾害", 1: "事故灾难", 2: "公共卫生", 3: "社会安全", 4: "经济危机", 5: "无法分类"}

'''
comfirm_event
keyword_num=10:事件保留的关键词数
topKeywordNum=50:事件抽取的关键词数
'''
keyword_num = 5
topKeywordNum = 50

'''
event_relative
iterate_num_max:主题迭代聚类次数最大值
DF_TE:主题与事件聚类时距离数组
DF_TT:主题与主题聚类时距离数组
alpha_TE:主题与事件聚类时的距离因子，距离等于=词典规模*距离因子
alpha_TT:主题与主题聚类时的距离因子
'''

iterate_num_max = 10
# 以下为无热点的参数
# DF_TE=[3+x*0.5 for x in range(8)]
# DF_TT=[3+x*0.6 for x in range(8)]
# alpha_TE=1.2
# alpha_TT=1.4

# 以下为有热点的参数
DF_TE = [4 + x * 0.2 for x in range(8)]
DF_TT = [3 + x * 0.3 for x in range(8)]
alpha_TE = 0.4
alpha_TT = 1.1
log_values = [math.log(x, 2) for x in range(1, 100)]

# summary
stop_word = sl_tool.get_stop_word()
