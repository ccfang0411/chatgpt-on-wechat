# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf
#import qstock as qs
#import pandas as pd
#import plotly.express as px


@plugins.register(
    name="MyBetting",
    desire_priority=100,
    hidden=True,
    desc="股票竞猜项目",
    version="0.1",
    author="ccfang",
)


class MyBetting(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template() 
            logger.info("[MyBetting] 初始化完成..")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[MyStock]初始化异常：{e}")
            raise "[MyBetting] 初始化失败"
    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT
        ]:
            return
        
        msg: ChatMessage = e_context["context"]["msg"] #原始消息
        content = e_context["context"].content.strip()
        #if not e_context.get("isgroup", False):
        #    return  
        group_id = msg.other_user_id            # 群组id
        group_name = msg.other_user_nickname    # 群组名称
        ## todo 在特定群组生效
        logger.info("[MyBetting] on_handle_context. content: {0},group_name:{1},group_id:{2}".format(content,group_name,group_id))

        if content == "提醒下注":
            print("提醒下注...")
            #stock_index = self.get_stock_index()
            #reply_type =  ReplyType.TEXT
            #reply = self.create_reply(reply_type, stock_index)
            #e_context["reply"] = reply
            #e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
            return
        if  content == "当日结算结果":
            
            print("猜涨跌游戏 当日结算...")
            #stock_index = self.get_stock_index()
            #reply_type =  ReplyType.TEXT
            #reply = self.create_reply(reply_type, stock_index)
            #e_context["reply"] = reply
            #e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
            return
        if content == "猜涨跌游戏规则":
            helptext= """
              🎲🔮 猜涨跌游戏规则 🎲🔮 \n
            提醒下注     📢8:00提醒涨跌下注 \n
            半场提醒     ⏰11:30提醒上午场结果下注 \n
            当日结算结果  📊获取当天结算结果 \n
            我要投降     🚩当天投降,13点有效 \n
            我猜涨/跌    📉下注(涨/跌) 9点前有效 \n
            统计本周战绩  🏆统计本周战绩 \n
            统计红包收支  💸统计红包收支\n 
            """
            reply_type =  ReplyType.TEXT
            reply = self.create_reply(reply_type, helptext)
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
    """
    def get_stock_index(self):
        
        mystock = ["上证指数", "创业板指","沪深300","中证500","中证1000","恒生指数","恒生科技指数"]
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
    """
         
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