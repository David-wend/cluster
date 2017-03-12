#coding=utf8
from __future__ import division
import tool
from datetime import datetime
import jieba.analyse
import pandas as pd
from pandas import DataFrame
from pandas import Series
import numpy as np
import jieba.posseg as pseg
import math
class term:

    def __init__(self,name, id, flag,create_time,count,freq):
        '''

        :param name:    词条名
        :param id:      词条ID
        :param flag:    词条词性
        :param create_time:  第一次使用时间
        :param high_time:   频数最高的时间
        :param close_time:  最后出现的时间
        :param std:   标准差
        :param mean:   均值
        :param count:   频数
        :param freq:    频率
        :param time_freq:   时间频率（存在时间/持续时间）
        :param continued_days   持续时间
        :param exist_days   存在时间
        :return:
        '''

        self.name=name
        self.id = id
        self.flag = flag
        self.stop_word = False
        self.create_time=create_time
        self.high_time=0
        self.close_time=0
        self.std=0
        self.mean=0
        self.count=count
        self.freq=freq
        self.time_freq=0
        self.continued_days=0
        self.exist_days=0

    def printInfo(self):
        temp_arr=[self.name,str(self.id),self.flag,str(self.create_time),str(self.high_time),str(self.close_time),
                  str(self.std),str(self.mean),str(self.count),str(self.freq),str(self.time_freq),str(self.continued_days),
                  str(self.exist_days)]
        temp_str='\t'.join(temp_arr)
        return temp_str

    def statistics(self,rows):
        '''统计词语分布信息

        :param rows:
        :return:
        '''

        # 统计每天词频
        exist_days=0
        delta=rows[len(rows)-1,0]-self.create_time
        temp_dataframe=DataFrame(np.zeros(delta.days+1),index=pd.date_range(self.create_time,rows[len(rows)-1,0]))
        for row in rows:
            if self.id in row[1]:
                try:
                    temp_dataframe.ix[row[0]][0]+=1
                except:
                    print row[0],"error"

        # 去除没有出现该词的时间
        for i in temp_dataframe.index[::-1]:
            if temp_dataframe.ix[i][0]==0:
                temp_dataframe=temp_dataframe.drop(i)
            else:
                exist_days+=1
                # temp_dataframe=temp_dataframe.resample('2D',how='sum')

        delta=temp_dataframe.index[-1]-temp_dataframe.index[0]
        self.exist_days=exist_days
        self.continued_days=delta.days+1
        self.time_freq=self.exist_days/self.continued_days
        self.high_time=np.argmax(temp_dataframe[0])
        self.close_time=temp_dataframe.index[-1]
        self.std=np.std(temp_dataframe[0])
        self.mean=np.mean(temp_dataframe[0])


def pseg_word(rows):
    '''切分标题并转换为数字表示,并保留分词信息

    :param
        rows：新闻列表

    :return
        word_num_arr：新闻标题分词数字版
        count：统计词典
        word_2_tag：分词标号词典，{'单词':词号}
        tag_2_flag：分词词性数组，tag_2_flag[词号]==词性
        tag_2_word：分词标号数组，tag_2_word[词号]==单词
        flag_2_weight：词性权重词典，{'词性'：权重}

    '''
    all_word_num=0 # 总频数
    count={} # 统计词典 值为对应个数
    wordcount=0 # 词标号
    word_2_tag={} # 分词标号词典
    tag_2_flag=[] # 分词词性数组
    tag_2_word=[] # 分词标号数组
    word_num_arr=[]

    for line in rows:

        word_fillter=[]
        for i in pseg.cut(line[5]):
            # if str(i.word) not in stop_word:
            all_word_num+=1
            if str(i.word) not in count:
                count[str(i.word)]=1
                word_2_tag[str(i.word)]=wordcount
                tag_2_word.append(str(i.word))
                tag_2_flag.append(str(i.flag))
                word_fillter.append(wordcount)
                wordcount=wordcount+1
            elif str(i.word) in count:
                count[str(i.word)] = count[str(i.word)] + 1
                word_fillter.append(word_2_tag[str(i.word)])

        # 只保留年月日
        if line[11].hour!=0 or line[11].minute!=0 or line[11].second!=0:
            new_datetime=datetime(line[11].year,line[11].month,line[11].day,0,0,0)
            print new_datetime,"change date"
        else:
            new_datetime=line[11]

        word_num_arr.append([new_datetime,word_fillter,len(word_fillter)])
    return np.array(word_num_arr),count,word_2_tag,tag_2_flag,tag_2_word,all_word_num


def count_weight(s_file_path,t_file_path):
    all_arr=[]
    fre_limit=int(math.sqrt(45000))
    with open(s_file_path) as ifile:
        for line in ifile:
            arr=line.split('\t',13)
            count=int(arr[8])
            temp_weight=abs(count-fre_limit)
            if temp_weight==0:
                temp_weight=1
            if count>12:
                weight=(float(arr[6])*float(arr[11]))/(float(arr[7])*float(arr[12]))-math.log(temp_weight,2)
            else:
                weight=((float(arr[6])*float(arr[11]))/(float(arr[7])*float(arr[12]))-math.log(temp_weight,2))/2
            all_arr.append([arr[0],arr[2],float(weight),int(arr[8])]) # name flag weight count

    c_arr=[]
    for i in all_arr:
        c_arr.append(float(i[2]))
    std=np.std(c_arr)
    mean=np.mean(c_arr)
    b_arr=[]
    for i in c_arr:
        b_arr.append(round((i-mean)/(std*20),3))

    w=open(t_file_path,'w+')
    for i in range(len(all_arr)):
        w.write(str(all_arr[i][0])+'\t'+str(all_arr[i][1])+'\t'+
                    str(all_arr[i][2])+'\t'+str(all_arr[i][3])+'\t'+str(b_arr[i])+'\n')


if __name__ == '__main__':
    term_list=[]
    sql='select * from news limit 50000 '
    rows=tool.select(sql)
    rows,count,word_2_tag,tag_2_flag,tag_2_word,all_word_num=pseg_word(rows)
    rows=DataFrame(rows,columns=['time','num_str','lenth']).sort_values(by='time')
    rows=np.array(rows)

    for i in np.arange(len(tag_2_word)):
        for j in np.arange(0, len(rows)):
            if rows[j][2]>0 and i in rows[j][1]:
                rows[j][2]-=1
                count_num=count[tag_2_word[i]]
                temp_term=term(tag_2_word[i],i,tag_2_flag[i],rows[j][0],count_num,count_num/all_word_num)
                temp_term.statistics(rows[j:,:])
                term_list.append(temp_term)
                break

    outline=[]
    for term in term_list:
        outline.append(term.printInfo())
    tool.writeFile('../Data/term.txt',outline)
    count_weight('../Data/term.txt','../data/weight.txt')









