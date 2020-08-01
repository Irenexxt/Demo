#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 导入需要的模块
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
import matplotlib
import xlwt
import matplotlib.dates as mdates
import pylab as pl
import datetime


# In[2]:


#指定默认字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['font.family']='sans-serif'
#解决负号'-'显示为方块的问题
matplotlib.rcParams['axes.unicode_minus'] = False


# In[3]:


# 抓取网页
def get_url(url, params=None, proxies=None):
    rsp = requests.get(url, params=params, proxies=proxies)
    rsp.raise_for_status()
    return rsp.text


# In[4]:


# 从网页抓取数据，如果被远程电脑拒绝，从此步开始运行
def get_fund_data(code,per=10,sdate='',edate='',proxies=None):
    url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx'
    params = {'type': 'lsjz', 'code': code, 'page':1,'per': per, 'sdate': sdate, 'edate': edate}
    html = get_url(url, params, proxies)
    soup = BeautifulSoup(html, 'html.parser')
       # 获取总页数
    pattern=re.compile(r'pages:(.*),')
    result=re.search(pattern,html).group(1)
    pages=int(result)

    # 获取表头
    heads = []
    for head in soup.findAll("th"):
        heads.append(head.contents[0])

    # 数据存取列表
    records = []

    # 从第1页开始抓取所有页面数据
    page=1
    while page<=pages:
        params = {'type': 'lsjz', 'code': code, 'page':page,'per': per, 'sdate': sdate, 'edate': edate}
        html = get_url(url, params, proxies)
        soup = BeautifulSoup(html, 'html.parser')

        # 获取数据
        for row in soup.findAll("tbody")[0].findAll("tr"):
            row_records = []
            for record in row.findAll('td'):
                val = record.contents

                # 处理空值
                if val == []:
                    row_records.append(np.nan)
                else:
                    row_records.append(val[0])

            # 记录数据
            records.append(row_records)

        # 下一页
        page=page+1

    # 数据整理到dataframe
    np_records = np.array(records)
    data= pd.DataFrame()
    for col,col_name in enumerate(heads):
        data[col_name] = np_records[:,col]

    return data


# # 以下为主程序，替换代码运行，如果被远程拒绝，则从上一步开始运行

# In[49]:


# 主程序
if __name__ == "__main__":
    data=get_fund_data('160517',per=49,sdate='2014-01-01',edate='2020-07-17')
    # 修改数据类型
    data['净值日期']=pd.to_datetime(data['净值日期'],format='%Y/%m/%d')
    data['单位净值']=data['单位净值'].astype(float)
    data['累计净值']=data['累计净值'].astype(float)
    data['日增长率']=data['日增长率'].str.strip('%').astype(float)
    # 按照日期升序排序并重建索引
    data=data.sort_values(by='净值日期',axis=0,ascending=True).reset_index(drop=True)
    print(data)

    # 获取净值日期、单位净值、累计净值、日增长率等数据
    net_value_date = data['净值日期']
    net_asset_value = data['单位净值']
    accumulative_net_value=data['累计净值']
    daily_growth_rate = data['日增长率']

    #并作基金净值图
    fig = plt.figure()
    #坐标轴1
    ax1 = fig.add_subplot(111)
    ax1.plot(net_value_date,net_asset_value)
    ax1.plot(net_value_date,accumulative_net_value)
    ax1.set_ylabel('净值数据')
    ax1.set_xlabel('日期')
    plt.legend(loc='upper left')
    #坐标轴2
    ax2 = ax1.twinx()
    ax2.plot(net_value_date,daily_growth_rate,'green')
    ax2.set_ylabel('日增长率（%）')
    plt.legend(loc='upper right')
    plt.title('基金净值数据')
    plt.show()

    # 绘制分红配送信息图
    bonus = accumulative_net_value-net_asset_value
    plt.figure()
    plt.plot(net_value_date,bonus)
    plt.xlabel('日期')
    plt.ylabel('累计净值-单位净值')
    plt.title('基金“分红”信息')
    plt.show()

    # 日增长率分析
#    print('日增长率缺失：',sum(np.isnan(daily_growth_rate)))
    print('日增长率为正的天数：',sum(daily_growth_rate>0))
    print('日增长率为负（包含0）的天数：',sum(daily_growth_rate<=0)) 


# In[50]:


#每只基金只能run一次
data.set_index(['净值日期'],inplace=True)


# In[51]:


###step：计算布林带,数据/X轴按照升序排列（即右边为2020年最近时间）

v = Series.as_matrix(net_asset_value)
N = 125 #日移动平均计算的布林线

#平均权重
weights = np.ones(N)/N

#卷积实现移动平均
sma = np.convolve(weights,v)[N-1:-N+1]

deviation = []

lenv = len(v)
for i in range(N-1,lenv):
    dev = v[i-N+1:i+1]
    deviation.append(np.std(dev))


#两1.5标准差
deviation = 1.5 * np.array(deviation)  
#压力线
upperBB = sma + deviation  
#支撑线
lowerBB = sma - deviation

###step3：画图

v_slice = v[N-1:]

plt.plot(v_slice,'y',label = "NAV")
plt.plot(sma,'b--',label = "BOLL")
plt.plot(upperBB,'r',label = "UPR")
plt.plot(lowerBB,'g',label = "DWN")
plt.title('$sample\ BOLL$')

#plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
#plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
#plt.gcf().autofmt_xdate()
plt.legend()
plt.show()
net_value_date.count()


# In[52]:


ts=data['2019-01-01':'2020-07-17']

nav=ts.单位净值
nav_lag1=nav.shift(1)
day_lr=np.log(nav/nav_lag1)
#以W/M/SM/Q（周/月/半个月/季度）为一个时间间隔求对数收益率的波动率（var）
mon_lrvar = day_lr.resample('W-FRI').var()
me = day_lr.resample('W-FRI')
#mon_lrvar = day_lr.resample('M').var()
#me = day_lr.resample('M')
mon_lr = me.asfreq()[:]
mu = mon_lr/20+0.5*mon_lrvar
standard= mon_lrvar-mu

#画σ²-μ的图
fig,ax1 = plt.subplots()
ax2 = ax1.twinx()

ax2.plot(standard,'g-')
ax1.plot(nav,'b-')
 
ax2.set_xlabel("date")
ax2.set_ylabel("standard")
ax1.set_ylabel("nav")


fig.set_size_inches(14, 5)
plt.axhline(0, color='red', linestyle='dashed')
#plt.axhline(avemu, color='yellow', linestyle='dashed')
plt.plot(standard, marker='o')
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
plt.title('sample',verticalalignment='bottom')
plt.show()

avemu = np.mean(mu)
print('平均μ',avemu)


# # 可选:保存图片
# fig.savefig('嘉实001878.png', dpi=400, bbox_inches='tight')

# # 可选:以下程序将爬取的数据输出excel，每次更改保存路径名称

#     f = xlwt.Workbook()
# #创建一个tab
#     sheet2 = f.add_sheet('fund')
#     rowTitle = [u'DATE',u'NAV']
# #遍历向表格写入标题行信息
#     for i in range(0,len(rowTitle)):
#     # 其中的'0'表示行, 'i'表示列，0和i指定了表中的单元格，'rowTitle[i]'是向该单元格写入的内容
#         sheet2.write(0,i,rowTitle[i])
# #遍历写入表信息
#     for j in range(1,len(net_value_date)): #再遍历内层集合，j表示列数据
#         sheet2.write(j,0,net_value_date[j]) #k+1表示先去掉标题行，j表示列数据，rowdatas[k][j] 插入单元格数据
#         sheet2.write(j,1,net_asset_value[j])
#         sheet2.write(j,2,daily_growth_rate[j])
#     f.save('F:\基金定投\.xlsx')
