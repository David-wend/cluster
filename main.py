# coding=utf-8

import create_news_doc
import count
from datetime import datetime
import remove_duplicate


if __name__ == '__main__':
    print datetime.now()
    # 对新闻标题进行去重
    remove_duplicate.remove_duplicate()
    # 根据去重后的标题，重新生成词典
    create_news_doc.transform_doc()
    # 挖掘频繁项集
    count.get_co_name()
    # 根据频繁模式进行聚类
    count.lan_de_qi_ming()
