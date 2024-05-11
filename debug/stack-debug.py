import exchange_calendars as xcals
from datetime import datetime

# 获取中国上海交易所的日历
xshg = xcals.get_calendar("XSHG")
# 判断今天是否为交易日
if xshg.is_session(datetime.utcnow().date()):
    print("今天是A股交易日")
else:
    print("今天不是A股交易日")
    
import datetime
import calendar

def get_month_and_week():
    today = datetime.date.today()
    year = today.year
    month = today.month
    first_day_of_month = today.replace(day=1)
    weekday_of_first_day = first_day_of_month.weekday()
    day_of_year = today.timetuple().tm_yday
    _, first_weekday_of_current_month = calendar.monthrange(year, month)
    day_of_month = today.day
    week_of_month = ((day_of_month + first_weekday_of_current_month - 1) // 7) + 1
    if weekday_of_first_day == 5:
        week_of_year = (day_of_year - 6) // 7 + 1
    else:
        week_of_year = day_of_year // 7 + 1
    month_info = f"{year:04d}{month:02d}"
    week_info = f"{year:04d}{week_of_year:02d}"
    return month_info, week_info

# 获取并打印今天是几月和一年中的第几周
month_info, week_info = get_month_and_week()
print(f"今天是: {month_info} 一年中的第 {week_info} 周")



import datetime
import calendar

def get_month_and_week():
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
    
    return month_info, week_info, week_of_month

# 示例用法:
month_info, week_info, week_of_month = get_month_and_week1()
print(f"年月: {month_info}, 周数: {week_info}, 当月周数: {week_of_month}")
