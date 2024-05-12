# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf
import datetime
import calendar
import qstock as qs
import pandas as pd
import plotly.express as px
import pymysql
import uuid
players = ["泉总","超总"]



@plugins.register(
    name="MyBetting",
    desire_priority=1,
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
        #group_name ="2024工作计划群"
        from_user_id = msg.actual_user_id       # 发送者id
        from_user_nickname = msg.actual_user_nickname  # 发送者昵称 聊天群名称
        ## todo 在特定群组生效
        logger.info("[MyBetting] on_handle_context. content: {0},group_name:{1},group_id:{2},from_user_id:{3},from_user_nickname:{4}".format(content,group_name,group_id,from_user_id,from_user_nickname))

        if content == "提醒下注":
            
            banker = self.get_banker(group_name)
            self.insert_stock_guessing(group_name,group_id,banker)
            text="本周是你({0})的主场赶紧下注,帮忙改写下要多一些emoji，谐幽默点，'(@{0})'里的不要变,字数保持在40字以下".format(banker)
            print(banker)
            e_context["context"].content = text
            e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
      
        if content == "我猜涨" or content == "我猜跌":
            banker = self.get_banker(group_name)
            print(banker)
            if not self.is_time_between("8:00", "9:00"):
                text = "下注时间8点到9点，当前不在下注时间，不能下注，帮忙改写下要多一些emoji,口气严厉点，但意思不要变,字数保持在40字以下"
                e_context["context"].content = text
                e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
                return
            if from_user_nickname != banker:
                text = "不是你的场，严禁投注,帮忙改写下要多一些emoji,口气严厉点，但意思不要变,字数保持在40字以下"
                e_context["context"].content = text
                e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
                return
            if content == "我猜涨":
                banke_bet = "涨"
                _,_,day = self.get_month_and_week()
                sql = "update stock_guessing set banke_bet = '{2}' where group_name = '{0}' and match_date = '{1}'".format(group_name,day,banke_bet)
                self.execute_sql(sql)
                text = "你的投注已经收到,猜涨这个是一个好主意，帮忙改写下要多一些emoji,谐幽默点，但意思不要变,字数保持在40字以下"
                e_context["context"].content = text
                e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
                return
            if content == "我猜跌":
                banke_bet = "跌"
                _,_,day = self.get_month_and_week()
                sql = "update stock_guessing set banke_bet = '{2}' where group_name = '{0}' and match_date = '{1}'".format(group_name,day,banke_bet)
                self.execute_sql(sql)
                text = "你的投注已经收到,猜跌这个是一个糟糕的想法，帮忙改写下要多一些emoji,谐幽默点，但意思不要变,字数保持在40字以下"
                e_context["context"].content = text
                e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
                return
        if content == "我投降":
            if not self.is_time_between("8:00","12:59"):
                text = "投降时间8点到12点，当前不在投降时间，不能投降，帮忙改写下要多一些emoji,口气严厉点，但意思不要变,字数保持在40字以下"
                e_context["context"].content = text
                e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
                return
            loser = from_user_nickname
            _,_,day = self.get_month_and_week()
            winner = [i for i in players if i != loser][0]
            sql = "update stock_guessing set winner = '{2}', guessing_status = 1 where group_name = '{0}' and match_date = '{1}'".format(group_name,day,winner)
            self.execute_sql(sql)
            text = "(@{1})投降这是一个明智决定，先提前恭喜(@{0})获胜，帮忙改写下要多一些emoji,谐幽默点，但意思不要变,字数保持在40字以下".format(winner,loser)
            e_context["context"].content = text
            e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
            return
            
        if  content == "当日结果":
            if not self.is_time_between("15:01","23:59"):
                text = "结果时间15点到23点，当前不在结果时间，不能获取结果，帮忙改写下要多一些emoji,口气严厉点，但意思不要变,字数保持在40字以下"
                e_context["context"].content = text
                e_context.action = EventAction.BREAK  # 事件结束，并跳过处理context的默认逻辑
                return
            result,resultstr,retext =self.get_stock_result()
            banker = self.get_banker(group_name)
            text= self.update_stock_result(banker,resultstr,group_name)
            e_context["context"].content = retext+text+"基于各指数表现和猜涨跌结果,帮忙改写下要多一些emoji,谐幽默点，但意思不要变,在回复中需要有前三个指数的涨跌幅,'(@{0})'里的不要变,忽略历史记录信息,字数保持在50字以下"
            e_context.action = EventAction.BREAK  # 事件结束，进入默认处理逻辑
            return
        if content == "猜涨跌游戏规则":
            helptext= "  🎲🔮 猜涨跌游戏规则 🎲🔮 \n"
            helptext = helptext+ "提醒下注     📢8:00提醒涨跌下注\n"
            helptext = helptext+ "半场提醒     ⏰11:30提醒上午场结果下注\n"
            helptext = helptext+ "当日结果  📊获取当天结算结果\n"
            helptext = helptext+ "我要投降     🚩当天投降,13点有效\n"
            helptext = helptext+ "我猜涨/跌    📉下注(涨/跌) 9点前有效\n"
            helptext = helptext+ "统计本周战绩  🏆统计本周战绩 \n"
            helptext = helptext+ "统计红包收支  💸统计红包收支"
            reply_type =  ReplyType.TEXT
            reply = self.create_reply(reply_type, helptext)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
            return
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
    def get_stock_result(self):
        mystock = ["上证指数", "创业板指","沪深300"]
        result_int = 0
        retext = ""
        stock_rt = qs.realtime_data(code=mystock)
        for index, row in stock_rt.iterrows():
            stock_name = row["名称"]
            stock_change = row["涨幅"]
            if stock_change > 0:
                result_int = result_int + 1
            elif stock_change == 0:
                if row["最新"] > row["今开"]:
                    result_int = result_int + 1
                else:
                    result_int = result_int - 1
            else:
                result_int = result_int - 1
        for index, row in stock_rt.iterrows():
            retext = retext+ f"{row['名称']}, 涨跌幅: {row['涨幅']}"
        if result_int:
            return True,"涨",retext
        else:
            return False,"跌",retext
    def update_stock_result(self,banker,resultstr,group_name):
        group_name = "2024工作计划群"
        _,_,day = self.get_month_and_week()
        sql = "select winner from stock_guessing where group_name = '{0}' and match_date = '{1}' and guessing_status = 1".format(group_name,day)
        result =self.execute_sql(sql)
        if result:
            winner = result[0][0]
            loser = [i for i in players if i != winner][0]
            return "{1}中途投降，恭喜(@{0})获胜".format(winner,loser)
        
        sql = "select winner from stock_guessing where group_name = '{0}' and match_date = '{1}' and guessing_status = 2".format(group_name,day)
        result =self.execute_sql(sql)
        if result:
            winner = result[0][0]
            return "精彩的比赛，恭喜(@{0})获胜".format(banker)
        
        sql = "select banke_bet from stock_guessing where group_name = '{0}' and match_date = '{1}' and guessing_status = 0".format(group_name,day)
        result =self.execute_sql(sql)
        if result:
            dbbanke_bet = result[0][0]
            if dbbanke_bet == resultstr:
                sql = "update stock_guessing set winner = '{2}', guessing_status = 2 where group_name = '{0}' and match_date = '{1}'".format(group_name,day,banker)
                self.execute_sql(sql)
                return "精彩的比赛，恭喜(@{0})获胜".format(banker)
            else:
                winner = [i for i in players if i != banker][0]
                sql = "update stock_guessing set winner = '{2}', guessing_status = 2 where group_name = '{0}' and match_date = '{1}'".format(group_name,day,winner)
                self.execute_sql(sql)
                return "精彩的比赛,恭喜(@{0})获胜".format(banker)
        return "精彩的比赛"
    def  insert_stock_guessing(self,group_name,group_id,banker):
        month_info,week_info,day = self.get_month_and_week()
        sql = "select * from stock_guessing where group_name = '{0}' and match_date = '{1}'".format(group_name,day)
        result =self.execute_sql(sql)
        if result:
            return
        else:
            uuid_str = str(uuid.uuid1())
            sql = f"insert into stock_guessing(guessing_id,group_name,group_id,banker,guessing_status,match_date,match_week,match_month) values('{uuid_str}','{group_name}','{group_id}','{banker}',0,'{day}','{week_info}','{month_info}')"
            self.execute_sql(sql)
            
        
                
            
    def get_month_and_week(self):
        now = datetime.datetime.now()
        year, week_of_year, weekday_of_first_day = now.isocalendar()
        month = now.month
        day_of_month = now.day
        first_day_of_month = now.replace(day=1)
        _, last_day_of_month = calendar.monthrange(year, month)
        week_of_month = (day_of_month + weekday_of_first_day - 1) // 7 + 1
        if weekday_of_first_day == 6 and day_of_month <= 7:
            week_of_month = 0
        
        month_info = now.strftime("%Y%m")
        week_info = f"{year:04d}{week_of_year:02d}"
        
        return int(month_info), int(week_info), now.strftime("%Y-%m-%d")

    
    def get_banker(self,group_name):
        """获取当前下注者"""
        month_info, week_info,_ = self.get_month_and_week()
        sql = "SELECT banker FROM stock_guessing WHERE match_week='{0}' and group_name ='{1}' order by id desc limit 1 ".format(week_info,group_name)
        print(sql)
        result = self.execute_sql(sql)
        if result:
            banker = result[0][0]
        else:
            sql = "SELECT banker FROM stock_guessing WHERE match_week='{0}' and group_name ='{1}' order by id desc limit 1 ".format((week_info-1),group_name)
            result = self.execute_sql(sql)
            if result:
                banker = result[0][0]
                banker = [i for i in players if i != banker][0]
                
            else:
                banker = players[0]
        return banker
    def is_time_between(self,start_time, end_time):
        # 获取当前时间
        now = datetime.datetime.now().time()
        
        # 将字符串表示的时间转换为时间对象
        start_time = datetime.datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.datetime.strptime(end_time, "%H:%M").time()

        # 判断当前时间是否在指定范围内
        return start_time <= now <= end_time

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


    def execute_sql(self,sql):
        # 连接到数据库
        print(sql)
        conn = pymysql.connect(
            host='192.168.3.253',
            user='root',
            password='123456',
            database='wechat',
            charset='utf8mb4'
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                conn.commit()
                if cursor.description is not None:
                    result = cursor.fetchall()
                else:
                    result = None

                return result

        except Exception as e:
            print("Error:", e)
            conn.rollback()
        finally:
            conn.close()