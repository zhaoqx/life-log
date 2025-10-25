#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DHT11温湿度监控系统 - Python Web服务器
功能：接收Arduino数据，提供Web界面和API
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import time
from datetime import datetime
import threading
import sqlite3
import os

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 全局变量存储最新数据
latest_data = {
    'temperature': 0.0,
    'humidity': 0.0,
    'timestamp': 0,
    'device_id': '',
    'last_update': None
}

# 数据存储
data_history = []
max_history = 1000  # 最多保存1000条记录

# 数据库初始化
def init_database():
    """初始化SQLite数据库"""
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            humidity REAL,
            timestamp INTEGER,
            device_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

# 保存数据到数据库
def save_to_database(data):
    """保存数据到SQLite数据库"""
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sensor_data (temperature, humidity, timestamp, device_id)
        VALUES (?, ?, ?, ?)
    ''', (data['temperature'], data['humidity'], data['timestamp'], data['device_id']))
    
    conn.commit()
    conn.close()

# 从数据库获取历史数据
def get_history_from_db(limit=100):
    """从数据库获取历史数据"""
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT temperature, humidity, timestamp, device_id, created_at
        FROM sensor_data
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    history = []
    for row in results:
        history.append({
            'temperature': row[0],
            'humidity': row[1],
            'timestamp': row[2],
            'device_id': row[3],
            'created_at': row[4]
        })
    
    return history

@app.route('/')
def index():
    """主页 - 显示Web界面"""
    return render_template('index.html')

@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    """接收Arduino发送的传感器数据"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
        
        # 验证数据格式
        required_fields = ['temperature', 'humidity', 'timestamp', 'device_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # 更新全局数据
        global latest_data
        latest_data.update(data)
        latest_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 添加到历史数据
        data_history.append(data.copy())
        if len(data_history) > max_history:
            data_history.pop(0)
        
        # 保存到数据库
        save_to_database(data)
        
        print(f"收到数据: 温度={data['temperature']}°C, 湿度={data['humidity']}%")
        
        return jsonify({
            'status': 'success',
            'message': 'Data received successfully',
            'timestamp': int(time.time())
        })
        
    except Exception as e:
        print(f"处理数据时出错: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/current-data')
def get_current_data():
    """获取当前最新数据"""
    return jsonify(latest_data)

@app.route('/api/history')
def get_history():
    """获取历史数据"""
    limit = request.args.get('limit', 100, type=int)
    history = get_history_from_db(limit)
    return jsonify(history)

@app.route('/api/stats')
def get_stats():
    """获取统计信息"""
    if not data_history:
        return jsonify({
            'total_records': 0,
            'avg_temperature': 0,
            'avg_humidity': 0,
            'uptime': 0
        })
    
    temperatures = [d['temperature'] for d in data_history]
    humidities = [d['humidity'] for d in data_history]
    
    return jsonify({
        'total_records': len(data_history),
        'avg_temperature': round(sum(temperatures) / len(temperatures), 2),
        'avg_humidity': round(sum(humidities) / len(humidities), 2),
        'min_temperature': round(min(temperatures), 2),
        'max_temperature': round(max(temperatures), 2),
        'min_humidity': round(min(humidities), 2),
        'max_humidity': round(max(humidities), 2),
        'last_update': latest_data.get('last_update', 'Never')
    })

# 创建模板目录和文件
def create_templates():
    """创建HTML模板文件"""
    os.makedirs('templates', exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DHT11温湿度监控系统</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin: 0;
        }
        
        .header p {
            font-size: 1.2em;
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        
        .content {
            padding: 30px;
        }
        
        .data-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .data-card {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: transform 0.3s ease;
            border-left: 5px solid;
        }
        
        .data-card:hover {
            transform: translateY(-5px);
        }
        
        .data-card.temperature {
            border-left-color: #ff9800;
            background: linear-gradient(135deg, #fff3e0, #ffe0b2);
        }
        
        .data-card.humidity {
            border-left-color: #4caf50;
            background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
        }
        
        .data-card h3 {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #333;
        }
        
        .data-value {
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #333;
        }
        
        .data-unit {
            font-size: 1.2em;
            color: #666;
        }
        
        .status-section {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding: 10px;
            background: white;
            border-radius: 8px;
        }
        
        .status-label {
            font-weight: bold;
            color: #333;
        }
        
        .status-value {
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
        }
        
        .status-value.connected {
            background: #e8f5e8;
            color: #2e7d32;
        }
        
        .status-value.disconnected {
            background: #ffebee;
            color: #c62828;
        }
        
        .status-value.auto-refresh {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .controls {
            text-align: center;
            margin: 30px 0;
        }
        
        .btn {
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 0 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(33, 150, 243, 0.4);
        }
        
        .btn.secondary {
            background: linear-gradient(45deg, #ff9800, #ffb74d);
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        }
        
        .btn.secondary:hover {
            box-shadow: 0 6px 20px rgba(255, 152, 0, 0.4);
        }
        
        .chart-container {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        
        .chart-title {
            text-align: center;
            font-size: 1.5em;
            margin-bottom: 20px;
            color: #333;
        }
        
        .chart-wrapper {
            position: relative;
            height: 400px;
        }
        
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #2196F3;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 15px;
            }
            .header {
                padding: 20px;
            }
            .header h1 {
                font-size: 2em;
            }
            .content {
                padding: 20px;
            }
            .data-grid {
                grid-template-columns: 1fr;
            }
            .data-value {
                font-size: 2.5em;
            }
            .btn {
                display: block;
                width: 100%;
                margin: 10px 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌡️ DHT11温湿度监控系统</h1>
            <p>Python Flask Web服务器 - 实时数据监控</p>
        </div>
        
        <div class="content">
            <div class="data-grid">
                <div class="data-card temperature">
                    <h3>🌡️ 当前温度</h3>
                    <div class="data-value" id="temperature">--</div>
                    <div class="data-unit">°C</div>
                </div>
                
                <div class="data-card humidity">
                    <h3>💧 当前湿度</h3>
                    <div class="data-value" id="humidity">--</div>
                    <div class="data-unit">%</div>
                </div>
            </div>
            
            <div class="status-section">
                <div class="status-item">
                    <span class="status-label">📡 连接状态</span>
                    <span class="status-value" id="connectionStatus">检查中...</span>
                </div>
                <div class="status-item">
                    <span class="status-label">🕒 最后更新</span>
                    <span class="status-value" id="lastUpdate">--</span>
                </div>
                <div class="status-item">
                    <span class="status-label">🔄 自动刷新</span>
                    <span class="status-value" id="autoRefreshStatus">已启动</span>
                </div>
                <div class="status-item">
                    <span class="status-label">📊 数据记录</span>
                    <span class="status-value" id="dataCount">--</span>
                </div>
            </div>
            
            <div class="controls">
                <button class="btn" onclick="refreshData()">🔄 手动刷新</button>
                <button class="btn secondary" onclick="loadHistory()">📈 加载历史</button>
                <button class="btn" onclick="toggleAutoRefresh()">⏹️ 停止自动刷新</button>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">📊 温湿度历史趋势</div>
                <div class="chart-wrapper">
                    <canvas id="temperatureChart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        let temperatureChart;
        let autoRefreshInterval;
        let isAutoRefresh = true;
        
        // 初始化图表
        function initChart() {
            const ctx = document.getElementById('temperatureChart').getContext('2d');
            temperatureChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '温度 (°C)',
                        data: [],
                        borderColor: '#ff9800',
                        backgroundColor: 'rgba(255, 152, 0, 0.1)',
                        tension: 0.4
                    }, {
                        label: '湿度 (%)',
                        data: [],
                        borderColor: '#4caf50',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.4,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            title: { display: true, text: '温度 (°C)' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            title: { display: true, text: '湿度 (%)' },
                            grid: { drawOnChartArea: false }
                        }
                    }
                }
            });
        }
        
        // 获取当前数据
        async function fetchCurrentData() {
            try {
                const response = await fetch('/api/current-data');
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('获取数据失败:', error);
                throw error;
            }
        }
        
        // 获取历史数据
        async function fetchHistory() {
            try {
                const response = await fetch('/api/history?limit=50');
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('获取历史数据失败:', error);
                throw error;
            }
        }
        
        // 更新页面显示
        function updateDisplay(data) {
            document.getElementById('temperature').textContent = data.temperature.toFixed(1);
            document.getElementById('humidity').textContent = data.humidity.toFixed(1);
            document.getElementById('lastUpdate').textContent = data.last_update || '--';
            document.getElementById('connectionStatus').textContent = '已连接';
            document.getElementById('connectionStatus').className = 'status-value connected';
        }
        
        // 显示错误状态
        function showError() {
            document.getElementById('temperature').textContent = '--';
            document.getElementById('humidity').textContent = '--';
            document.getElementById('connectionStatus').textContent = '连接失败';
            document.getElementById('connectionStatus').className = 'status-value disconnected';
        }
        
        // 刷新数据
        async function refreshData() {
            try {
                const data = await fetchCurrentData();
                updateDisplay(data);
            } catch (error) {
                showError();
            }
        }
        
        // 加载历史数据
        async function loadHistory() {
            try {
                const history = await fetchHistory();
                updateChart(history);
                document.getElementById('dataCount').textContent = history.length + ' 条记录';
            } catch (error) {
                console.error('加载历史数据失败:', error);
            }
        }
        
        // 更新图表
        function updateChart(history) {
            if (!temperatureChart || !history.length) return;
            
            const labels = history.map((_, index) => index);
            const temperatures = history.map(d => d.temperature);
            const humidities = history.map(d => d.humidity);
            
            temperatureChart.data.labels = labels;
            temperatureChart.data.datasets[0].data = temperatures;
            temperatureChart.data.datasets[1].data = humidities;
            temperatureChart.update();
        }
        
        // 切换自动刷新
        function toggleAutoRefresh() {
            if (isAutoRefresh) {
                clearInterval(autoRefreshInterval);
                isAutoRefresh = false;
                document.querySelector('button[onclick="toggleAutoRefresh()"]').textContent = '🚀 开始自动刷新';
                document.getElementById('autoRefreshStatus').textContent = '已停止';
                document.getElementById('autoRefreshStatus').className = 'status-value disconnected';
            } else {
                autoRefreshInterval = setInterval(refreshData, 3000);
                isAutoRefresh = true;
                document.querySelector('button[onclick="toggleAutoRefresh()"]').textContent = '⏹️ 停止自动刷新';
                document.getElementById('autoRefreshStatus').textContent = '每3秒刷新';
                document.getElementById('autoRefreshStatus').className = 'status-value auto-refresh pulse';
            }
        }
        
        // 页面加载时初始化
        window.addEventListener('load', function() {
            initChart();
            refreshData();
            loadHistory();
            
            // 启动自动刷新
            autoRefreshInterval = setInterval(refreshData, 3000);
        });
        
        // 页面关闭时清理
        window.addEventListener('beforeunload', function() {
            if (autoRefreshInterval) {
                clearInterval(autoRefreshInterval);
            }
        });
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("HTML模板文件已创建")

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 创建模板文件
    create_templates()
    
    print("=" * 50)
    print("DHT11温湿度监控系统 - Python Web服务器")
    print("=" * 50)
    print("服务器启动中...")
    print("Web界面访问地址: http://localhost:5000")
    print("API接口:")
    print("  - POST /api/sensor-data (Arduino发送数据)")
    print("  - GET  /api/current-data (获取当前数据)")
    print("  - GET  /api/history (获取历史数据)")
    print("  - GET  /api/stats (获取统计信息)")
    print("=" * 50)
    
    # 启动Flask服务器
    app.run(host='0.0.0.0', port=5000, debug=True)
