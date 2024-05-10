import qstock as qs
import pandas as pd
import plotly.express as px


# 创建股票和权重数据
mystock = ["上证指数", "创业板指","沪深300"]

#mystock_df = pd.DataFrame(mystock)
retext =[] 
stock_rt = qs.realtime_data(code=mystock)
for index, row in stock_rt.iterrows():
    retext.append(f"{row['名称']}, 最新: {row['最新']}, 涨跌幅: {row['涨幅']}")
data = "今日大盘指数\n" + "\n".join(retext)
print(data)