#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成视频剧本PDF文档
使用reportlab生成彩色PDF文档
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import os
import sys

# 注册中文字体（如果系统有的话）
try:
    # 尝试使用系统中的中文字体
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',  # 黑体
        'C:/Windows/Fonts/simsun.ttc',  # 宋体
    ]
    
    chinese_font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            chinese_font = font_path
            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
            print(f"已注册字体: {font_path}")
            break
    
    if not chinese_font:
        # 如果没有找到中文字体，使用默认字体
        print("警告: 未找到中文字体，将使用默认字体")
        chinese_font = 'Helvetica'
except Exception as e:
    print(f"字体注册失败: {e}")
    chinese_font = 'Helvetica'

# 创建样式
styles = getSampleStyleSheet()

# 标题样式
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='ChineseFont' if chinese_font else 'Helvetica-Bold'
)

# 章节标题样式
section_style = ParagraphStyle(
    'CustomSection',
    parent=styles['Heading2'],
    fontSize=18,
    textColor=colors.HexColor('#2196F3'),
    spaceAfter=20,
    spaceBefore=20,
    fontName='ChineseFont' if chinese_font else 'Helvetica-Bold'
)

# 小节标题样式
subsection_style = ParagraphStyle(
    'CustomSubsection',
    parent=styles['Heading3'],
    fontSize=14,
    textColor=colors.HexColor('#1976D2'),
    spaceAfter=12,
    fontName='ChineseFont' if chinese_font else 'Helvetica-Bold'
)

# 正文样式
body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=11,
    textColor=colors.HexColor('#333333'),
    spaceAfter=8,
    leading=16,
    alignment=TA_JUSTIFY,
    fontName='ChineseFont' if chinese_font else 'Helvetica'
)

# 代码样式
code_style = ParagraphStyle(
    'CodeStyle',
    parent=styles['Code'],
    fontSize=9,
    textColor=colors.HexColor('#d63384'),
    backColor=colors.HexColor('#f8f9fa'),
    leading=14,
    fontName='Courier'
)

# 列表项样式
bullet_style = ParagraphStyle(
    'BulletStyle',
    parent=styles['Bullet'],
    fontSize=11,
    textColor=colors.HexColor('#333333'),
    spaceAfter=8,
    fontName='ChineseFont' if chinese_font else 'Helvetica'
)

def create_pdf():
    """生成PDF文档"""
    
    # 创建文档
    pdf_file = 'docs/视频剧本.pdf'
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 内容列表
    story = []
    
    # 封面
    story.append(Paragraph("多传感器厨房空气监测系统", title_style))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("基于Arduino的多传感器物联网项目", styles['Title']))
    story.append(Spacer(1, 2*cm))
    
    # 项目信息
    info_data = [
        ['项目名称', '多传感器厨房空气监测系统'],
        ['实验类型', 'Arduino + 多传感器 + Python Web应用'],
        ['录制时长', '20-25分钟'],
        ['传感器数量', '4个（DHT11、MQ7、MQ135、声音）'],
        ['创建日期', '2025-01-22'],
        ['版本', 'v2.0 - 多传感器增强版']
    ]
    
    info_table = Table(info_data, colWidths=[5*cm, 10*cm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if chinese_font else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(info_table)
    
    story.append(PageBreak())
    
    # 第一部分：实验介绍
    story.append(Paragraph("第一部分：实验介绍（2分钟）", section_style))
    
    story.append(Paragraph("开场白", subsection_style))
    story.append(Paragraph(
        "大家好！欢迎来到今天的科学实验视频。今天我们要进行的是一个基于Arduino的厨房空气质量监测实验。"
        "厨房是我们每天都要接触的重要区域，但是在烹饪过程中会产生油烟、一氧化碳、PM2.5等有害物质。"
        "如何实时监测厨房的空气质量，并及时发现问题呢？这就是我们今天要解决的课题。",
        body_style
    ))
    
    story.append(Paragraph("实验目标", subsection_style))
    story.append(Paragraph(
        "通过今天的实验，我们将学习：",
        body_style
    ))
    
    goals = [
        "硬件知识：Arduino开发板、多种传感器的工作原理（温湿度、CO、空气质量、声音）",
        "编程技能：如何编写Arduino多传感器代码，如何开发Web服务器",
        "系统集成：如何将多个硬件和软件完美结合",
        "数据分析：如何实时监控、存储和分析多维度传感器数据"
    ]
    
    for goal in goals:
        story.append(Paragraph(f"• {goal}", bullet_style))
    
    story.append(Spacer(1, 1*cm))
    
    # 第二部分：器材介绍
    story.append(PageBreak())
    story.append(Paragraph("第二部分：器材介绍（4分钟）- 多传感器系统", section_style))
    
    story.append(Paragraph("核心组件 - Arduino UNO R4 WiFi", subsection_style))
    story.append(Paragraph(
        "Arduino UNO R4 WiFi开发板是本次实验的核心。这是Arduino UNO R4的升级版本，搭载了WiFi模块。"
        "它有14个数字I/O引脚、6个模拟输入引脚、内置WiFi功能以及内置LED矩阵显示器。"
        "这款板子的特色是集成了WiFi模块，可以直接从Arduino发送数据到网络，而不需要额外的WiFi模块。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("传感器模块1 - DHT11温湿度传感器", subsection_style))
    story.append(Paragraph(
        "DHT11是一款数字温湿度传感器。它可以同时测量温度范围0-50°C（精度±2°C）"
        "和湿度范围20-90%RH（精度±5%RH）。它通过一个引脚发送数字信号，比模拟传感器更稳定、更准确。"
        "传感器有4个引脚：VCC（电源正极接5V）、GND（电源负极接地）、DATA（数据引脚接D2）、NC（不连接）。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("传感器模块2 - MQ7一氧化碳传感器", subsection_style))
    story.append(Paragraph(
        "MQ7是厨房安全监测的关键传感器，检测一氧化碳浓度（0-1000 ppm）。"
        "工作原理是电化学原理，通过检测CO气体分子引起的电阻变化。这是厨房安全监测的重中之重，"
        "因为一氧化碳是无色、无味、无臭的剧毒气体。连接方式：VCC接5V，GND接GND，A0接Arduino A0。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("传感器模块3 - MQ135空气质量传感器", subsection_style))
    story.append(Paragraph(
        "MQ135是综合型空气质量传感器，能检测氨气、苯、酒精、烟雾、CO2等多种有害气体。"
        "检测范围10-1000 ppm，对厨房油烟、烟尘有很高的灵敏度。能够有效监测烹饪时产生的各种有害气体和烟雾。"
        "连接方式：VCC接5V，GND接GND，A0接Arduino A1。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("传感器模块4 - 声音传感器", subsection_style))
    story.append(Paragraph(
        "声音传感器用于检测环境噪音，在厨房监测中有独特作用。主要应用：判断油烟机是否开启、"
        "监测烹饪噪音水平、判断异常噪音、结合其他传感器数据综合判断厨房活动状态。"
        "连接方式：VCC接5V，GND接GND，OUT接Arduino A2。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("辅助材料", subsection_style))
    story.append(Paragraph(
        "还需要面包板（用于快速连接电路，不需要焊接）、跳线（用于连接各个组件）、"
        "USB数据线（给Arduino供电和编程）以及PC或笔记本电脑（用于编程和运行Web服务器）。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("软件环境", subsection_style))
    story.append(Paragraph(
        "软件方面需要Arduino IDE（用于编写和上传Arduino代码）、Python 3.8+（用于运行Web服务器）、"
        "Flask（Python的Web框架）以及浏览器（用于查看监控界面）。",
        body_style
    ))
    
    # 第三部分：科学原理
    story.append(PageBreak())
    story.append(Paragraph("第三部分：科学原理（5分钟）- 多传感器工作原理", section_style))
    
    story.append(Paragraph("DHT11温湿度传感器工作原理", subsection_style))
    story.append(Paragraph(
        "DHT11传感器内部有两个关键元件：温度敏感元件（NTC热敏电阻）和湿度敏感元件（高分子聚合物）。"
        "温度测量通过电阻值随温度变化，湿度测量通过聚合物薄膜吸收水蒸气后电阻率变化。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("MQ7一氧化碳传感器工作原理", subsection_style))
    story.append(Paragraph(
        "MQ7使用电化学原理：传感器内部有一层特殊的金属氧化物半导体。"
        "当环境中存在一氧化碳（CO）时，CO分子会吸附在半导体表面，改变半导体的电导率。"
        "这是厨房安全监测的重中之重，因为一氧化碳是无色、无味、无臭的剧毒气体。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("MQ135空气质量传感器工作原理", subsection_style))
    story.append(Paragraph(
        "MQ135使用金属氧化物半导体技术，对多种有害气体都有反应：氨气、苯、酒精、烟雾、CO2等。"
        "通过加热器和感测层的组合工作，不同气体吸附后产生不同的电导率变化。"
        "能够有效监测厨房烹饪时产生的油烟、燃气泄漏、烹饪烟雾。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("声音传感器工作原理", subsection_style))
    story.append(Paragraph(
        "声音传感器使用麦克风元件接收声波，声波振动转换为电信号，"
        "通过运放电路放大信号，输出模拟电压值。主要应用：判断油烟机是否开启、"
        "监测烹饪噪音水平、结合其他传感器数据综合判断厨房活动状态。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("数据采集与传输", subsection_style))
    story.append(Paragraph(
        "系统工作流程：",
        body_style
    ))
    
    steps = [
        "第一步：多传感器数据采集 - 4个传感器同时采集数据（温湿度、CO、空气质量、声音）",
        "第二步：数据处理 - Arduino接收到所有传感器数据后进行处理和格式化，转换为JSON格式",
        "第三步：数据传输 - Arduino通过WiFi将多维度数据发送到PC的Web服务器"
    ]
    
    for i, step in enumerate(steps, 1):
        story.append(Paragraph(f"{i}. {step}", bullet_style))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("系统架构优势", subsection_style))
    advantages = [
        "全方位监测：4个传感器5个维度的数据，多角度保障厨房安全",
        "实时性：数据每5秒更新一次",
        "数据融合：综合分析多个传感器，提高判断准确度",
        "可视化：通过图表直观展示多维度趋势",
        "远程访问：手机、平板都可以访问",
        "数据持久化：所有数据存储在SQLite数据库中"
    ]
    
    for adv in advantages:
        story.append(Paragraph(f"• {adv}", bullet_style))
    
    # 第四部分：硬件搭建
    story.append(PageBreak())
    story.append(Paragraph("第四部分：硬件搭建（5分钟）- 多传感器接线", section_style))
    
    story.append(Paragraph("多传感器接线步骤", subsection_style))
    
    wiring_steps = [
        "DHT11温湿度传感器：VCC→5V，GND→GND，DATA→D2",
        "MQ7一氧化碳传感器：VCC→5V，GND→GND，A0→Arduino A0",
        "MQ135空气质量传感器：VCC→5V，GND→GND，A0→Arduino A1",
        "声音传感器：VCC→5V，GND→GND，OUT→Arduino A2",
        "检查接线 - 确认所有导线都插稳了，没有短路现象"
    ]
    
    for i, step in enumerate(wiring_steps, 1):
        story.append(Paragraph(f"{i}. {step}", bullet_style))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("完整接线示意图", subsection_style))
    
    # 创建接线图表格（多传感器版本）
    wiring_table_data = [
        ['Arduino引脚', '传感器连接'],
        ['5V', '→ 所有传感器VCC（并联）'],
        ['GND', '→ 所有传感器GND（并联）'],
        ['D2', '→ DHT11 DATA'],
        ['A0', '→ MQ7 A0'],
        ['A1', '→ MQ135 A0'],
        ['A2', '→ 声音传感器OUT']
    ]
    
    wiring_table = Table(wiring_table_data, colWidths=[8*cm, 7*cm])
    wiring_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2196F3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if chinese_font else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(wiring_table)
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph(
        "接线原则：红色接5V，黑色接GND，信号线根据代码连接到指定引脚。",
        body_style
    ))
    
    story.append(Paragraph("硬件检查清单", subsection_style))
    checklist = [
        "Arduino已连接电源（USB指示灯亮起）",
        "DHT11传感器已正确连接",
        "所有导线插接牢固",
        "没有短路现象"
    ]
    
    for item in checklist:
        story.append(Paragraph(f"☐ {item}", bullet_style))
    
    # 第五部分：软件开发
    story.append(PageBreak())
    story.append(Paragraph("第五部分：软件开发（4分钟）", section_style))
    
    story.append(Paragraph("Arduino代码开发 - 包含库文件", subsection_style))
    
    story.append(Paragraph(
        "包含必要的库文件：",
        body_style
    ))
    
    story.append(Paragraph(
        "#include \"ArduinoGraphics.h\"<br/>"
        "#include \"Arduino_LED_Matrix.h\"<br/>"
        "#include &lt;DHT.h&gt;<br/>"
        "#include &lt;WiFiS3.h&gt;",
        code_style
    ))
    
    story.append(Paragraph(
        "这些库分别用于LED矩阵显示、读取DHT11传感器和WiFi连接。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Arduino代码开发 - 配置和主循环", subsection_style))
    
    story.append(Paragraph(
        "定义配置参数（WiFi名称、密码、服务器IP等），然后在setup中初始化各个组件，"
        "在loop中不断读取数据、发送数据、显示数据。代码逻辑清晰：2秒读取一次传感器数据，"
        "5秒发送一次数据到服务器，LED矩阵实时显示当前值。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("Python Web服务器开发", subsection_style))
    story.append(Paragraph(
        "创建Flask应用，实现三个关键功能：",
        body_style
    ))
    
    server_features = [
        "数据接收API - 接收Arduino发送的数据并存储到SQLite数据库",
        "数据展示API - 提供当前数据和历史数据的查询接口",
        "Web界面 - 使用HTML + JavaScript + Chart.js制作美观的监控面板"
    ]
    
    for feature in server_features:
        story.append(Paragraph(f"• {feature}", bullet_style))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("代码上传和测试", subsection_style))
    
    upload_steps = [
        "选择开发板：工具 → 开发板 → Arduino UNO R4 WiFi",
        "选择端口：工具 → 端口 → 选择你的USB端口",
        "上传代码：点击上传按钮",
        "启动Python服务器：cd src/python 然后 python sensor_web_server.py",
        "访问界面：浏览器打开 http://localhost:5000"
    ]
    
    for i, step in enumerate(upload_steps, 1):
        story.append(Paragraph(f"{i}. {step}", bullet_style))
    
    # 第六部分：结果展示
    story.append(PageBreak())
    story.append(Paragraph("第六部分：结果展示（3分钟）- 多传感器数据展示", section_style))
    
    story.append(Paragraph("实时数据监控", subsection_style))
    story.append(Paragraph(
        "监控界面显示多组数据卡片：温湿度数据（温度、湿度）、气体检测数据（一氧化碳CO、空气质量）、"
        "环境监测数据（声音强度）、系统状态（传感器状态4/4正常运行）。"
        "界面采用现代化卡片式设计，用不同颜色标识不同传感器，数据清晰易懂。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("历史趋势分析", subsection_style))
    story.append(Paragraph(
        "使用Chart.js绘制多个历史趋势图：环境监测图（温度、湿度曲线）、气体浓度趋势图（一氧化碳、空气质量）、"
        "声音监测图（噪音水平曲线）。所有图表实时更新，展示最近50条数据记录。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("LED矩阵显示", subsection_style))
    story.append(Paragraph(
        "Arduino上的LED矩阵循环显示多个数据：温度T:25.3C、湿度H:60.2%、一氧化碳CO:015 ppm、"
        "空气质量AQ:085。信息滚动显示，让用户快速了解关键数据。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("手机远程访问", subsection_style))
    story.append(Paragraph(
        "在手机浏览器输入相同的IP地址，界面自动适配手机屏幕，"
        "随时随地都能查看厨房的多维度安全数据（温度、湿度、CO、空气质量、声音）。这对实际应用非常有价值！",
        body_style
    ))
    
    # 第七部分：实验总结
    story.append(PageBreak())
    story.append(Paragraph("第七部分：实验总结（2分钟）", section_style))
    
    story.append(Paragraph("知识技能总结", subsection_style))
    
    knowledge = [
        "硬件方面：学会了Arduino开发板的使用，理解了4种传感器的工作原理（温湿度、CO、空气质量、声音），掌握了多传感器系统的接线方法，掌握了WiFi通信的基本概念",
        "软件方面：掌握了Arduino多传感器数据读取，学会了Python Flask Web开发，理解了客户端-服务器架构，学会了数据融合和分析",
        "系统集成：完成了硬件和软件的完美结合，实现了4个传感器实时数据监控，实现了数据可视化和历史记录，构建了完整的厨房安全监测系统"
    ]
    
    for item in knowledge:
        story.append(Paragraph(f"• {item}", bullet_style))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("实际应用价值", subsection_style))
    story.append(Paragraph(
        "这个系统在现实生活中非常有用：",
        body_style
    ))
    
    applications = [
        "家庭安全：实时监测厨房一氧化碳，防止中毒",
        "健康保护：监测空气质量，保护家人健康",
        "教学演示：展示物联网、传感器技术的综合应用",
        "实验研究：收集多维度数据，进行环境分析",
        "产品开发：可以扩展为智能家居监测产品"
    ]
    
    for app in applications:
        story.append(Paragraph(f"• {app}", bullet_style))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("扩展方向", subsection_style))
    
    extensions = [
        "更多气体传感器：PM2.5、甲烷等",
        "智能告警功能：超出阈值自动通知、远程推送",
        "机器学习数据处理和分析",
        "云端存储和数据同步",
        "联动控制：自动开启排气扇等"
    ]
    
    for ext in extensions:
        story.append(Paragraph(f"• {ext}", bullet_style))
    
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph(
        "通过这个项目，我们不仅学到了多种传感器的工作原理，更重要的是构建了一个完整的厨房安全监测系统。"
        "这个系统能够实时监测温度、湿度、一氧化碳、空气质量、声音等5个维度的数据，全方位保障厨房安全。"
        "这是一个典型的物联网项目，展示了多传感器融合、微控制器、网络通信和Web技术的综合应用。",
        body_style
    ))
    
    story.append(Spacer(1, 0.5*cm))
    
    story.append(Paragraph("扩展方向", subsection_style))
    
    extensions = [
        "更多传感器：PM2.5、CO2等",
        "告警功能：超出阈值自动通知",
        "数据处理：数据分析和预测",
        "云端存储：云端数据同步"
    ]
    
    for ext in extensions:
        story.append(Paragraph(f"• {ext}", bullet_style))
    
    story.append(Spacer(1, 1*cm))
    
    # 结束语
    story.append(Paragraph(
        "通过这个项目，我们不仅学到了硬件和软件的知识，更重要的是学会了如何用技术解决实际问题。"
        "这是一个典型的物联网项目，展示了传感器、微控制器、网络通信和Web技术的综合应用。",
        body_style
    ))
    
    # 页脚
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph(
        "<i>剧本版本：v1.0 | 创建日期：2025-01-22 | 预计拍摄时长：15-20分钟</i>",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.grey,
            fontName='ChineseFont' if chinese_font else 'Helvetica'
        )
    ))
    
    # 生成PDF
    doc.build(story)
    print(f"\nPDF已生成: {pdf_file}")
    print(f"文件大小: {os.path.getsize(pdf_file) / 1024:.2f} KB")

if __name__ == '__main__':
    print("=" * 50)
    print("生成厨房空气监测实验视频剧本PDF")
    print("=" * 50)
    
    try:
        create_pdf()
        print("\n生成完成！")
    except Exception as e:
        print(f"\n生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

