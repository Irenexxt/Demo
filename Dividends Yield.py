#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
from pandas import datetime
from pandas import Series, DataFrame
from sklearn.linear_model import LinearRegression
import matplotlib.pylab as plt
from matplotlib.pylab import rcParams
import matplotlib.dates as mdates
from matplotlib import pyplot
import re
import numpy as np
from statsmodels.tsa.stattools import adfuller
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# #将下载的股息率文件进行时间“升序”排序（保证最右为最近时间），然后改名，存入路径f
# #文件来源 理杏仁
# 
# 正常：zzbank 中证银行，zz500 中证500 , bx 保险 ， jiancai 建材 
# 
# 高估：szxf 消费，sh50 上证50，hs300 沪深300 
# 
# 极度高估：cyb 创业板 ，IB 证券 ，zzfinance 中证金融 ，能源 ,gongcheng 基建工程 

# In[18]:


f = r'F:\sh50.csv'


# In[19]:


#usecols 要用的数据列
data = pd.read_csv(f,usecols=[0,1,2] , header=0)
date=data['时间']
div=np.log(data['股息率(平均值)'])
nav=np.log(data['收盘点位'])

data.set_index(['时间'],inplace=True)

roldiv = div.rolling(window=12).mean()
div_diff = div-roldiv
#div_diff.dropna(inplace = True)

rolnav = nav.rolling(window=12).mean()
nav_diff = nav-rolnav
#nav_diff.dropna(inplace = True)


# In[20]:


#plot rolling statistics，最右为2020年最近时间:
fig,ax1= plt.subplots()
ax1.plot(div_diff,color = 'orange',marker='x',label='div')

#div越小越高估
plt.axhline(np.mean(div_diff)+1.5*np.std(div_diff), color='darkgreen', linestyle='-.')#低估~
plt.axhline(np.mean(div_diff)+np.std(div_diff), color='green', linestyle='dotted')#正常~均值
plt.axhline(np.mean(div_diff), color='black', linestyle='dashed')#均值
plt.axhline(np.mean(div_diff)-np.std(div_diff), color='red', linestyle='dotted')#均值~正常
plt.axhline(np.mean(div_diff)-1.5*np.std(div_diff), color='darkred', linestyle='-.')#~高估~极高估~

#nav右y轴
ax2 = ax1.twinx()
ax2.plot(nav_diff,color ='gray',label='nav')

ax1.set_xlabel("date")
ax1.set_ylabel("div")
ax2.set_ylabel("nav")

fig.set_size_inches(14, 5)
plt.legend()
plt.show()

print('总日期长度:',date.count())


# In[8]:


print(np.std(div_diff),np.mean(div_diff),np.mean(nav_diff))

df1 = pd.DataFrame(data.index,nav_diff)
df2 = pd.DataFrame(data.index,div_diff)
#print(df2)

