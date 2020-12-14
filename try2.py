# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 12:45:15 2020

@author: Admin
"""
import os
import re
from urllib.request import urlopen,urlretrieve
from bs4 import BeautifulSoup
import requests
import random
import pandas as pd
import numpy as np
from myclass import Rowtext
import pysentiment2 as ps
from pysentiment2.utils import Tokenizer


main_url='https://www.sec.gov/Archives/'
main_dir=r'C:/Users/Admin/Desktop/20Python/Spyder/pre2/'
main_dir2=r'C:/Users/Admin/Desktop/20Python/Spyder/'
urlretrieve(main_url+'edgar/full-index/2016/QTR1/'+'form.idx',
            main_dir2+'form.csv')

n=10#depends on how many 10-K report do we want
with open(main_dir2+'my10-k.csv','w',encoding='utf-8') as f:
    read=open(main_dir2+'form.csv','r',encoding=('utf-8')).read()
    soup=BeautifulSoup(read,features='lxml').get_text()
    population=re.findall(r'10-K\s.+\.txt',soup)
    #10-K and 10-K/A
    link=random.sample(population, n)
    for i in link:#防止最后一行空白出个none
        if link.index(i)==len(link)-1:
            f.write(str(i))
        else:
            f.write(str(i)+'\n')
#生成10-K.csv


f=open(main_dir2+'my10-k.csv','r',encoding='utf-8').read()
L=f.split('\n')


counter=0#see below
counter2=0
#well we can see that several lines has little different length I dont know why some of them start at 95 or 96 so I have to use start
for i in L:
    start=re.search('edgar',i).start()    
    suffix=str(i[start:])
    #下载链接
    #debug(str(i[start:]))
    start2=re.search(r'000.+',i).start() 
    suffix2=str(i[start2:])
    download=requests.get(main_url+suffix).text
    
    
    dic,test=Rowtext().location(download)
    #if self, then (),if not, then .
    dic.keys()
    #the dictionary
    
    
    x=['1A','1B','7A','7','8']
    table=Rowtext.spcitems(dic,x)
    #I dont know why here is no parenthesis necessary?

    # Drop duplicates
    table = table.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
    # Display the dataframe
    try:
        assert len(table.item)>=5
        table.set_index('item', inplace=True)
        
        try:
            # Get Items
            item_1a_raw = dic['10-K'][table['start'].loc['item1a']:table['start'].loc['item1b']]
            item_7_raw = dic['10-K'][table['start'].loc['item7']:table['start'].loc['item7a']]
            item_7a_raw = dic['10-K'][table['start'].loc['item7a']:table['start'].loc['item8']]
            #我们找1a,7,7a靠的是前一个和后一个item的位置
                    
            #write down
            Rowtext.pickup(item_1a_raw,main_dir+suffix2)
            Rowtext.pickup(item_7_raw,main_dir+suffix2)
            Rowtext.pickup(item_7a_raw,main_dir+suffix2)
            
            
        except KeyError:
            print('we havent find one of the items')
            counter+=1
        except AssertionError:
            counter2+=1
            try:
                os.remove(main_dir+suffix2)
            except FileNotFoundError:
                pass
    except AssertionError:
        counter+=1
    
    
#sentiment analysis
x=sorted(os.listdir(main_dir))
X_score=pd.DataFrame(columns=['Positive','Negative','Polarity','Subjectivity','CIK'])
#Polarity= (Pos-Neg)/(Pos+Neg)
#Subjectivity= (Pos+Neg)/count(*)


#stopwords=open(r'C:\Users\Admin\Desktop\20Python\Spyder\pre2dic\StopWords_Generic.txt','r',encoding='utf-8').read()
#stopwords=stopwords.split('\n')

for i in range(len(x)):
    filename=x[i]
    document = open(main_dir+filename,'r',encoding='utf-8').read()  
    document = document.replace(r'(<.*?>.*?<.*?>)+','').replace(r'(<.*?>)+','').replace(r'(@.*?[ :])','')
    document = document.lower()
    
    #tokenize
    lm = ps.LM()
    tokens = lm.tokenize(document)
    #no stemming, no stopwords!
    #but McDonald's list contain multiple form of words
    #the results could be misleading
    scores=lm.get_score(tokens)
    scores['CIK']=filename
    X_score=X_score.append(scores,ignore_index=True)
    
X_score=X_score[X_score.Positive>5]
X_score=X_score[X_score.Negative>5]
print(X_score)
print(counter,counter2)
#counter for doesnt find, counter 2 for delete because of length.