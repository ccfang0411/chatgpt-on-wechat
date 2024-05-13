# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf
import qstock as qs
import pandas as pd
import plotly.express as px


@plugins.register(
    name="mystock",
    desire_priority=91,
    hidden=True,
    desc="获取大盘指数项目",
    version="0.1",
    author="ccfang",
)


class MyStock(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template() 
            logger.info("[MyStock] inited")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[MyStock]初始化异常：{e}")
            raise "[MyStock] init failed, ignore "
    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT
        ]:
            return
        content = e_context["context"].content.strip()
        logger.debug("[MyStock] on_handle_context. content: %s" % content)

        if content.startswith("大盘指数") or content.startswith("今天行情"):
            stock_index = self.get_stock_index()
            reply_type =  ReplyType.TEXT
            reply = self.create_reply(reply_type, stock_index)
            e_context["reply"] = reply
            e_context["context"].content = stock_index + "\n 基于上述数据，请你模仿脱口秀演员House口吻的点评下，要求回复需要有emoji表情，在回复中需要有前三个指数的涨跌幅，字数尽量在40个字以下"
            e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
            return
        
        if  content.startswith("老子的股票今天涨了吗"):
            stock_index = self.get_mystock()
            reply_type =  ReplyType.TEXT
            reply = self.create_reply(reply_type, stock_index)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
            return
    def _load_config_template(self):
        logger.debug("No MyStock plugin config.json, use plugins/MyStock/config.json.template")
        try:
            plugin_config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(plugin_config_path):
                with open(plugin_config_path, "r", encoding="utf-8") as f:
                    plugin_conf = json.load(f)
                    return plugin_conf
        except Exception as e:
            logger.exception(e)
    def get_stock_index(self):
        
        mystock = ["上证指数", "创业板指","沪深300","中证500","中证1000","恒生指数","恒生科技指数"]
        mystock = ["上证指数", "创业板指","沪深300"]
        #mystock_df = pd.DataFrame(mystock)
        retext =[]
        stock_rt = qs.realtime_data(code=mystock)
        for index, row in stock_rt.iterrows():
            retext.append(f"{row['名称']}, 最新: {row['最新']}, 涨跌幅: {row['涨幅']}")
        stacktime = stock_rt.iloc[0]["时间"]
        data = "🎉🎉 今日大盘指数 🎉🎉 \n" + "\n".join(retext) + "\n" + f"\n更新截止: {stacktime}"
        return data
    def get_mystock(self):
        
        mystock = ["腾讯控股", "芯片ETF","科创50","恒瑞医药","通策医疗"]
        #mystock_df = pd.DataFrame(mystock)
        retext =[]
        stock_rt = qs.realtime_data(code=mystock)
        for index, row in stock_rt.iterrows():
            retext.append(f"{row['名称']}, 最新: {row['最新']}, 涨跌幅: {row['涨幅']}")
        stacktime = stock_rt.iloc[0]["时间"]
        data = "🎉🎉 您的股票今日走势 🎉🎉\n" + "\n".join(retext) + "\n" + f"\n更新截止: {stacktime}"
        return data
        
         
    def create_reply(self, reply_type, content):
        reply = Reply()
        reply.type = reply_type
        reply.content = content
        return reply

    def handle_error(self, error, message):
        logger.error(f"{message}，错误信息：{error}")
        return message
    
    def is_valid_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def is_valid_image_url(self, url):
        try:
            response = requests.head(url)  # Using HEAD request to check the URL header
            # If the response status code is 200, the URL exists and is reachable.
            return response.status_code == 200
        except requests.RequestException as e:
            # If there's an exception such as a timeout, connection error, etc., the URL is not valid.
            return False