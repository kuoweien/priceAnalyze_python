#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct  9 16:41:53 2021

@author: weien
"""

import pandas as pd
import json
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import warnings
from base64 import b64encode
from json import dumps
warnings.filterwarnings('ignore')



def tidyDfandgetPrice(itemfile):#整理pchome
    df=pd.read_csv(itemfile)
    df_tidy=df[{'Id','Name','isCombine'}]
    
    price=df['Price']
    
    raw_price=[]
    discount_price=[]
    for i in range(len(price)):
        temp_raw=int((price.str.split(',')[i][0]).split(':')[1])
        
        temp_discount=int((price.str.split(',')[i][1]).split(':')[1])
        if temp_raw==0:
            raw_price.append(temp_discount)
        elif temp_raw!=0:
            raw_price.append(temp_raw)
        discount_price.append(temp_discount)
    
    df_tidy['RawPrice']=raw_price
    df_tidy['DiscountPrice']=discount_price
    df_tidy['DiscountPercent']=round((df_tidy['DiscountPrice']/df_tidy['RawPrice'])*100)
    df_tidy['Shop']='PChome'
    
    
    return df_tidy

def momoShoptidyDfandgetPrice(itemfile):#整理ｍｏｍｏ
    df=pd.read_csv(itemfile)
    df_tidy=df[{'title','price','amount'}]    
    df_tidy=df_tidy.rename(columns={'title':'Name'})
    df_tidy=df_tidy.rename(columns={'price':'RawPrice'})
    df_tidy=df_tidy.rename(columns={'amount':'DiscountPrice'})
    df_tidy['RawPrice']=df_tidy['RawPrice'].fillna(df_tidy['DiscountPrice'])
    df_tidy['DiscountPercent']=round((df_tidy['DiscountPrice']/df_tidy['RawPrice'])*100)
    df_tidy['Shop']='momo'
    
    return df_tidy

#算四分位數
def measureIQR(list):    
    q1 = np.quantile(list, 0.25) #美國的四分位數
    q3 = np.quantile(list, 0.75)
    return q1,q3

def getSameProductName(name_list):
    same_product=[]
    dict_result = Counter(name_list)
    for key, value in dict_result.items():
             if value>=2:
                 same_product.append(key)
    return same_product

def getLowerPriceinSameProduct(df_type,product_name):
    minprice_message=''
    for i in range(len(product_name)):
        price_list=df_type[df_type['Name'] == product_name[i]]['DiscountPrice']    
        if len(set(price_list))==1:
            minprice_message=minprice_message+product_name[i]+': Same Prize'+'\n'
        if len(set(price_list))!=1:
            minprice_message=minprice_message+ product_name[i]+': '+min(price_list)+'\n'
    return minprice_message

#keyboard name整理(排除組合價)
def getnotCombineProduct(df):
    df_noCombine=df[df['isCombine']==0]
    return df_noCombine

#算四分位,刪除outlier的產品
def deleteExcludeOutlierPrice(df):
    discountprice=df['DiscountPrice']
    q1,q3=measureIQR(discountprice)
    iqr = q3-q1
    lowest_bound= q1-1.5*iqr #最小值
    highest_bound= q3+1.5*iqr #最大值
    df_excludeOutlier=df[(df['DiscountPrice']<=highest_bound) & (df['DiscountPrice']>=lowest_bound)]
    return q1,q3,df_excludeOutlier

def sortNormalProductbyPrice(df,q1,q3): #售價排序 並只return需要顯示之欄位
    df_normalprice=df[(df['DiscountPrice']<=q3) & (df['DiscountPrice']>=q1)]
    df_normalprice_increase=df_normalprice.sort_values(['DiscountPrice'],ascending=True)
    df_normalprice_increase=df_normalprice_increase[{'Name','RawPrice','DiscountPrice','DiscountPercent','Shop'}]
    df_normalprice_decrease=df_normalprice.sort_values(['DiscountPrice'],ascending=False)
    df_normalprice_decrease=df_normalprice_increase[{'Name','RawPrice','DiscountPrice','DiscountPercent','Shop'}]
    return df_normalprice_increase,df_normalprice_decrease

def sortNormalProductbyDiscountpercent(df,q1,q3): #折扣比例排序 #目前沒用到
    df_normalprice=df[(df['DiscountPrice']<=q3) & (df['DiscountPrice']>=q1)]
    df_normalprice_increase=df_normalprice.sort_values(['DiscountPercent'],ascending=True)
    df_normalprice_decrease=df_normalprice.sort_values(['DiscountPercent'],ascending=False)
    return df_normalprice_increase,df_normalprice_decrease


#取價格最低的 並只return需要顯示之欄位
def getLowestPrice(df):
    df_price_min=df[df['DiscountPrice']==df['DiscountPrice'].min()]
    df_price_min=df_price_min[{'Name','RawPrice','DiscountPrice','DiscountPercent','Shop'}]
    return df_price_min

#取折數最低的 並只return需要顯示之欄位
def getLowestDiscountpercent(df):
    df_discountpercent_min=df[df['DiscountPercent']==df['DiscountPercent'].min()] 
    df_discountpercent_min=df_discountpercent_min[{'Name','RawPrice','DiscountPrice','DiscountPercent','Shop'}]

    return df_discountpercent_min

def getBrandName(df): #找出品牌名 ＃目前沒用到
    brand_list=[]
    for i in range(len(df['Name'])):
        brand=df['Name'].str.split(' ')[i][0]
        if '【' in brand:
            brand=brand.split('】')[1]
        brand_list.append(brand)
    df['Brand']=brand_list
    
    return df



#圖轉base64並放入json字串
def imageTransfertoJson(imageName): 
    with open(imageName, 'rb') as jpg_file:
        byte_content = jpg_file.read()
    
    base64_bytes = b64encode(byte_content)
    base64_string = base64_bytes.decode('utf-8' )
        
    return base64_string

#dataframe轉成json
def dataframeTransfertoJson(df): 
    #df_price_decrease=pd.read_csv(df)
    js = df.to_json(orient = 'records')
    
    return js
 
    

#整理csv檔/pchome and momo
df_keyboard_pchome=tidyDfandgetPrice('keyboard_pchome.csv') #收到的pchome csv檔
df_keyboard_momo=momoShoptidyDfandgetPrice('keyboard_momo.csv') #收到的momo csv檔

df_keyboard=df_keyboard_pchome.append(df_keyboard_momo) #兩個電商的相加
df_keyboard['isCombine']=df_keyboard['isCombine'].fillna(0) #momo的isCombine是空值，給予其值
df_keyboard_excludeCombine=getnotCombineProduct(df_keyboard)#排除組合價
keyboard_q1,keyboard_q3,df_keyboard_excludeoutlier=deleteExcludeOutlierPrice(df_keyboard_excludeCombine) #計算四分位並排除outlier
print('鍵盤主要價格:${}$-${}'.format(int(keyboard_q1),int(keyboard_q3)))


#產出價格25-75區間的箱型圖
keyboard_discountprice=df_keyboard_excludeoutlier['DiscountPrice']
labels='Computer Price','Mouse Price','Keyboard Price'
plt.title('Boxplot of Product')
plt.ylabel('Price')
plt.boxplot(keyboard_discountprice)
plt.xticks([1],['Keyboard'])
plt.show()
plt.savefig('Keyboard_NormalPrice.png')


#取正常售價並根據價格,折扣數來排序
df_keyboard_sortincrease_byprice,df_keyboard_sortdecrease_byprice=sortNormalProductbyPrice(df_keyboard_excludeoutlier,keyboard_q1,keyboard_q3)

#取推薦商品
df_lowestbyprice=getLowestPrice(df_keyboard_sortincrease_byprice)#價格最低
df_lowestbydiscountpercent=getLowestDiscountpercent(df_keyboard_sortincrease_byprice) #折扣最多



#轉成json檔
base64_boxplot=imageTransfertoJson('Keyboard_NormalPrice.png')
js_price_decrease=dataframeTransfertoJson(df_keyboard_sortdecrease_byprice)
js_price_increase=dataframeTransfertoJson(df_keyboard_sortincrease_byprice)
js_recommand_lowest=dataframeTransfertoJson(df_lowestbyprice)
js_recommand_discount=dataframeTransfertoJson(df_lowestbydiscountpercent)
 
#組成json格式   
alljson='{'+'"boxplot":'+'"'+'data:image/png;base64,'+base64_boxplot+'",'+'"normalPrice25":'+str(keyboard_q3)+',"narmalPrice75":'+str(keyboard_q1)+','+'"table_normal_decrease":'+js_price_decrease+','+'"table_normal_increase":'+js_price_increase+','+'"table_recommand_lowest":'+js_recommand_lowest+','+'"table_recommand_discount":'+js_recommand_discount+'}'

with open('analyzePrice.json', 'w') as json_file: #Json檔儲存為analyzePrice.json
    json_file.write(alljson)









