import pandas as pd
import openpyxl
import os
import sys

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')

# 读取Excel文件的所有sheet
script_dir = os.path.dirname(os.path.abspath(__file__))
xlsx_file = os.path.join(script_dir, 'profile.xlsx')
xl = pd.ExcelFile(xlsx_file)
print('=== Sheet名称 ===')
print(xl.sheet_names)
print()

# 读取每个sheet的内容
for sheet_name in xl.sheet_names:
    print(f'=== Sheet: {sheet_name} ===')
    df = pd.read_excel(xlsx_file, sheet_name=sheet_name, header=None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    print(df.to_string())
    print()

