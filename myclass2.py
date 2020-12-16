# -*- coding: utf-8 -*-
"""
Created on Mon Dec 14 11:37:57 2020

@author: Admin
"""

import re
import pandas as pd
from bs4 import BeautifulSoup

class Rowtext(object):
    
    
    def location(self,rowtext):
        #para:urlopentext
        #return:dic with locationset
        doc_st=re.compile(r'<DOCUMENT>')
        doc_end=re.compile(r'</DOCUMENT>')
        doc_type=re.compile(r'<TYPE>[^\n]+')
        doc_st_is=[x.end() for x in doc_st.finditer(rowtext)]
        doc_end_is=[x.start() for x in doc_end.finditer(rowtext)]
        doc_types = [x[len('<TYPE>'):] for x in doc_type.findall(rowtext)]
        #store the position to a dictionary
        dictionary = {}
        for doc_type, doc_start, doc_end in zip(doc_types, doc_st_is, doc_end_is):
            #zip concatenate those three items to iterate together
            if doc_type == '10-K':
                dictionary[doc_type] = rowtext[doc_start:doc_end]
        if '10-K' not in dictionary.keys():
            raise AssertionError
        return dictionary
    
    
    def spcitems(dictionary,x):
        #para:x has to be a list,and entry has to be str and Capitalization!!!
        #return:dataframe with items position
            
        goal="|".join(x)#list to str
        regex = re.compile(r'(>(Item|ITEM)(\s|&#160;|&nbsp;)('+goal+')\.{0,1})')
        matches = regex.finditer(dictionary['10-K'])
        test_df_0 = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches],columns=['item', 'start', 'end'])
        test_df=test_df_0.copy()
        test_df['item'] = test_df.item.str.lower()
        # standarize
        
        test_df.replace('&#160;','',regex=True,inplace=True)
        test_df.replace('&nbsp;','',regex=True,inplace=True)
        test_df.replace('\n','',regex=False,inplace=True)
        test_df.replace(' ','',regex=True,inplace=True)
        test_df.replace('\.','',regex=True,inplace=True)
        test_df.replace('>','',regex=True,inplace=True)
        test_df = test_df.sort_values('start', ascending=True).drop_duplicates(subset=['item'], keep='last')
        # Drop duplicates
        return test_df
        
        
    def writedown(text,savewd):#text for write,wd for save
        #soup and write
        clean_text = BeautifulSoup(text, 'lxml')
        clean_text.prettify()
        clean_text=clean_text.get_text()
        try:
            assert len(clean_text)>100
            #too short items deleted          
            with open(savewd,'w',encoding='utf-8') as wooh:
                    wooh.write(clean_text+'\n')
        except:
            raise AssertionError