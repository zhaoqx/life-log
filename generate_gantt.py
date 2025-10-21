import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


CSV_PATH = os.path.join('experiment', 'air-monitor', 'docs', 'project-plan-厨房空气监测实验计划.csv')
OUTPUT_PATH = 'project_gantt.html'


def load_plan(path: str) -> pd.DataFrame:
    """Load plan CSV and perform initial cleanup."""
    df = pd.read_csv(path)
    for column in ['开始日期', '结束日期']:
        df[column] = pd.to_datetime(df[column], errors='coerce')
    df['阶段编号'] = df['任务编号'].astype(str).str.split('.').str[0]
    parents = df[df['阶段编号'] == df['任务编号'].astype(str)]
    stage_names = parents.set_index('阶段编号')['任务名称'].to_dict()
    df['所属阶段'] = df['阶段编号'].map(stage_names)
    df['进度值'] = (
        df['进度']
        .fillna('0%')
        .astype(str)
        .str.rstrip('%')
        .replace({'': '0'})
        .astype(float)
        .clip(lower=0, upper=100)
    )
    df = df[df['开始日期'].notna()].sort_values(['开始日期', '结束日期', '任务编号'])
    return df


def build_gantt(df: pd.DataFrame) -> go.Figure:
    """Create an enhanced Gantt chart figure."""
    color_sequence = px.colors.qualitative.Safe * 3
    hover_data = {
        '任务编号': True,
        '负责人': True,
        '状态': True,
        '前置任务': True,
        '备注': True,
        '所属阶段': True,
        '开始日期': '|%Y-%m-%d',
        '结束日期': '|%Y-%m-%d',
    }
    figure = px.timeline(
        df,
        x_start='开始日期',
        x_end='结束日期',
        y='任务名称',
        color='所属阶段',
        text=df['进度值'].map(lambda v: f"{v:.0f}%"),
        hover_data=hover_data,
        color_discrete_sequence=color_sequence,
        title='厨房空气监测实验计划｜专业甘特图视图',
    )

    figure.update_yaxes(autorange='reversed')
    figure.update_traces(
        marker=dict(line=dict(color='rgba(45,45,45,0.35)', width=1)),
        textposition='inside',
        insidetextanchor='middle',
    )

    today = datetime.today().date()
    figure.update_layout(
        template='plotly_white',
        height=1200,
        xaxis_title='日期',
        yaxis_title='任务',
        legend_title='项目阶段',
        font=dict(family='Microsoft YaHei, Arial, Helvetica, sans-serif', size=13),
        margin=dict(l=90, r=50, t=90, b=60),
        hoverlabel=dict(bgcolor='rgba(0,0,0,0.75)', font_color='white'),
        xaxis=dict(showgrid=True, gridcolor='rgba(160,160,160,0.25)', tickformat='%Y-%m-%d'),
        bargap=0.25,
    )

    figure.add_shape(
        type='line',
        x0=today,
        x1=today,
        y0=-0.5,
        y1=len(df['任务名称']) - 0.5,
        line=dict(color='rgba(220,20,60,0.55)', width=2, dash='dash'),
    )
    figure.add_annotation(
        x=today,
        y=-1,
        text='今天',
        showarrow=False,
        xanchor='left',
        bgcolor='rgba(255,255,255,0.7)',
        font=dict(color='rgba(220,20,60,0.85)', size=12),
    )

    durations = (df['结束日期'] - df['开始日期']).dt.days.clip(lower=1)
    progress_trace = go.Bar(
        x=durations * df['进度值'] / 100,
        y=df['任务名称'],
        base=df['开始日期'],
        orientation='h',
        marker=dict(
            color='rgba(0,0,0,0)',
            line=dict(color='rgba(0,0,0,0)'),
            pattern=dict(shape='\\', size=8, solidity=0.3, fgcolor='rgba(0,0,0,0.35)'),
        ),
        hoverinfo='skip',
        showlegend=False,
    )
    figure.add_trace(progress_trace)

    status_colors = {
        '已完成': 'rgba(34,139,34,0.9)',
        '进行中': 'rgba(30,144,255,0.9)',
        '未开始': 'rgba(169,169,169,0.9)',
        '风险': 'rgba(255,140,0,0.9)',
    }
    status_annotations = df[['任务名称', '状态']].dropna()
    for task, status in status_annotations.values:
        label_color = status_colors.get(status)
        if not label_color:
            continue
        figure.add_annotation(
            xref='paper',
            x=1.005,
            y=task,
            yanchor='middle',
            text=status,
            showarrow=False,
            font=dict(color='white', size=11),
            bordercolor=label_color,
            borderwidth=1,
            bgcolor=label_color,
        )

    return figure


def main() -> None:
    df_plan = load_plan(CSV_PATH)
    figure = build_gantt(df_plan)
    figure.write_html(OUTPUT_PATH, include_plotlyjs='cdn', full_html=True)
    print(f"已生成 {OUTPUT_PATH}，可用浏览器打开查看。")


if __name__ == '__main__':
    main()
