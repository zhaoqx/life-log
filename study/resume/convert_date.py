from datetime import datetime, timedelta

# Excel日期序列号从1899年12月30日开始
base = datetime(1899, 12, 30)
date = base + timedelta(days=41609)
print(f'出生日期: {date.year}年{date.month}月{date.day}日')

