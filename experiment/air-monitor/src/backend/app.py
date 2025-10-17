"""
厨房空气质量监测系统 - Flask后端应用
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sys
import os
from datetime import datetime, timedelta

# 添加父目录到路径，以便导入模拟器
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.air_quality_simulator import AirQualitySimulator, CookingActivity

app = Flask(__name__, 
            static_folder='../frontend',
            template_folder='../frontend')
CORS(app)

# 全局模拟器实例
simulator = AirQualitySimulator()

# 数据历史记录（简单实现，实际应使用数据库）
data_history = []
MAX_HISTORY = 1000  # 最多保留1000条记录

# 告警历史
alert_history = []
MAX_ALERTS = 100


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/current', methods=['GET'])
def get_current_data():
    """获取当前传感器数据"""
    data = simulator.read_sensors()
    level = simulator.get_air_quality_level(data)
    should_alert = simulator.should_alert(data)
    
    # 添加到历史记录
    data_history.append(data)
    if len(data_history) > MAX_HISTORY:
        data_history.pop(0)
    
    # 如果需要告警，记录告警
    if should_alert:
        alert_record = {
            'timestamp': data['timestamp'],
            'level': level,
            'pm25': data['pm25'],
            'co': data['co'],
            'co2': data['co2'],
            'temperature': data['temperature'],
            'humidity': data['humidity']
        }
        alert_history.append(alert_record)
        if len(alert_history) > MAX_ALERTS:
            alert_history.pop(0)
    
    return jsonify({
        'success': True,
        'data': data,
        'level': level,
        'alert': should_alert
    })


@app.route('/api/history', methods=['GET'])
def get_history_data():
    """获取历史数据"""
    # 获取查询参数
    hours = request.args.get('hours', default=1, type=int)
    limit = request.args.get('limit', default=100, type=int)
    
    # 计算时间范围
    now = datetime.now()
    start_time = now - timedelta(hours=hours)
    
    # 筛选数据
    filtered_data = []
    for record in data_history:
        record_time = datetime.fromisoformat(record['timestamp'])
        if record_time >= start_time:
            filtered_data.append(record)
    
    # 限制返回数量
    if len(filtered_data) > limit:
        # 均匀采样
        step = len(filtered_data) // limit
        filtered_data = filtered_data[::step]
    
    return jsonify({
        'success': True,
        'data': filtered_data,
        'count': len(filtered_data)
    })


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """获取告警历史"""
    limit = request.args.get('limit', default=50, type=int)
    
    # 返回最近的告警
    recent_alerts = alert_history[-limit:] if len(alert_history) > limit else alert_history
    
    return jsonify({
        'success': True,
        'alerts': recent_alerts,
        'count': len(recent_alerts)
    })


@app.route('/api/activity', methods=['POST'])
def set_activity():
    """设置烹饪活动（用于演示）"""
    data = request.get_json()
    activity_name = data.get('activity', 'idle')
    
    try:
        activity = CookingActivity(activity_name)
        simulator.set_activity(activity)
        
        return jsonify({
            'success': True,
            'message': f'活动已设置为: {activity_name}'
        })
    except ValueError:
        return jsonify({
            'success': False,
            'message': f'无效的活动类型: {activity_name}'
        }), 400


@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """获取统计信息"""
    if not data_history:
        return jsonify({
            'success': True,
            'stats': {}
        })
    
    # 计算统计信息
    pm25_values = [d['pm25'] for d in data_history]
    co_values = [d['co'] for d in data_history]
    co2_values = [d['co2'] for d in data_history]
    temp_values = [d['temperature'] for d in data_history]
    humidity_values = [d['humidity'] for d in data_history]
    
    stats = {
        'pm25': {
            'avg': sum(pm25_values) / len(pm25_values),
            'min': min(pm25_values),
            'max': max(pm25_values)
        },
        'co': {
            'avg': sum(co_values) / len(co_values),
            'min': min(co_values),
            'max': max(co_values)
        },
        'co2': {
            'avg': sum(co2_values) / len(co2_values),
            'min': min(co2_values),
            'max': max(co2_values)
        },
        'temperature': {
            'avg': sum(temp_values) / len(temp_values),
            'min': min(temp_values),
            'max': max(temp_values)
        },
        'humidity': {
            'avg': sum(humidity_values) / len(humidity_values),
            'min': min(humidity_values),
            'max': max(humidity_values)
        },
        'total_records': len(data_history),
        'total_alerts': len(alert_history)
    }
    
    return jsonify({
        'success': True,
        'stats': stats
    })


@app.route('/api/thresholds', methods=['GET'])
def get_thresholds():
    """获取告警阈值"""
    thresholds = {
        'pm25': {'warning': 75, 'danger': 150},
        'pm10': {'warning': 150, 'danger': 250},
        'co': {'warning': 35, 'danger': 100},
        'co2': {'warning': 2000, 'danger': 5000},
        'temperature': {'warning': 35, 'danger': 45},
        'humidity': {
            'warning_low': 30, 'warning_high': 80,
            'danger_low': 20, 'danger_high': 90
        }
    }
    
    return jsonify({
        'success': True,
        'thresholds': thresholds
    })


if __name__ == '__main__':
    print("=" * 80)
    print("厨房空气质量监测系统 - 后端服务")
    print("=" * 80)
    print("服务地址: http://localhost:5000")
    print("API文档:")
    print("  GET  /api/current    - 获取当前数据")
    print("  GET  /api/history    - 获取历史数据")
    print("  GET  /api/alerts     - 获取告警历史")
    print("  POST /api/activity   - 设置烹饪活动（演示用）")
    print("  GET  /api/stats      - 获取统计信息")
    print("  GET  /api/thresholds - 获取告警阈值")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
