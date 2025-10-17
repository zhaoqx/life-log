"""
空气质量数据模拟器
用于演示和测试，模拟厨房空气质量传感器数据
"""

import random
import time
import json
from datetime import datetime
from enum import Enum


class CookingActivity(Enum):
    """烹饪活动类型"""
    IDLE = "idle"  # 空闲
    BOILING = "boiling"  # 煮水/蒸煮
    FRYING = "frying"  # 炒菜
    BAKING = "baking"  # 烘焙
    CLEANING = "cleaning"  # 清洁


class AirQualitySimulator:
    """空气质量数据模拟器"""
    
    def __init__(self):
        """初始化模拟器"""
        # 基准值（正常状态）
        self.baseline = {
            'pm25': 15.0,  # μg/m³
            'pm10': 25.0,  # μg/m³
            'co': 3.0,  # ppm
            'co2': 450.0,  # ppm
            'temperature': 22.0,  # ℃
            'humidity': 55.0  # %
        }
        
        # 当前值
        self.current = self.baseline.copy()
        
        # 当前活动
        self.activity = CookingActivity.IDLE
        
        # 活动影响系数
        self.activity_effects = {
            CookingActivity.IDLE: {
                'pm25': 1.0,
                'pm10': 1.0,
                'co': 1.0,
                'co2': 1.0,
                'temperature': 1.0,
                'humidity': 1.0
            },
            CookingActivity.BOILING: {
                'pm25': 1.5,
                'pm10': 1.3,
                'co': 1.2,
                'co2': 1.8,
                'temperature': 1.15,
                'humidity': 1.2
            },
            CookingActivity.FRYING: {
                'pm25': 8.0,  # 炒菜产生大量油烟
                'pm10': 6.0,
                'co': 3.5,
                'co2': 2.5,
                'temperature': 1.3,
                'humidity': 0.9
            },
            CookingActivity.BAKING: {
                'pm25': 2.0,
                'pm10': 1.8,
                'co': 1.5,
                'co2': 2.0,
                'temperature': 1.25,
                'humidity': 0.85
            },
            CookingActivity.CLEANING: {
                'pm25': 1.2,
                'pm10': 1.5,
                'co': 0.8,
                'co2': 1.1,
                'temperature': 1.0,
                'humidity': 1.1
            }
        }
        
        # 恢复速率（每秒）
        self.recovery_rate = {
            'pm25': 0.95,  # 颗粒物沉降较慢
            'pm10': 0.96,
            'co': 0.92,  # 气体扩散较快
            'co2': 0.93,
            'temperature': 0.98,
            'humidity': 0.99
        }
    
    def set_activity(self, activity: CookingActivity):
        """设置当前烹饪活动"""
        self.activity = activity
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 活动切换: {activity.value}")
    
    def _add_noise(self, value, noise_percent=0.05):
        """添加随机噪声"""
        noise = value * noise_percent * (random.random() - 0.5) * 2
        return value + noise
    
    def _apply_activity_effect(self, sensor, base_value):
        """应用活动影响"""
        effect = self.activity_effects[self.activity][sensor]
        target_value = base_value * effect
        
        # 平滑过渡
        current_value = self.current[sensor]
        if current_value < target_value:
            # 上升（污染增加）
            new_value = current_value + (target_value - current_value) * 0.1
        else:
            # 下降（污染减少）
            recovery = self.recovery_rate[sensor]
            new_value = base_value + (current_value - base_value) * recovery
        
        return new_value
    
    def read_sensors(self):
        """读取传感器数据（模拟）"""
        # 应用活动影响
        for sensor in self.current.keys():
            base_value = self.baseline[sensor]
            self.current[sensor] = self._apply_activity_effect(sensor, base_value)
        
        # 添加噪声并构造返回数据
        data = {
            'timestamp': datetime.now().isoformat(),
            'pm25': max(0, self._add_noise(self.current['pm25'], 0.03)),
            'pm10': max(0, self._add_noise(self.current['pm10'], 0.03)),
            'co': max(0, self._add_noise(self.current['co'], 0.05)),
            'co2': max(400, self._add_noise(self.current['co2'], 0.02)),  # CO2最低400ppm
            'temperature': self._add_noise(self.current['temperature'], 0.01),
            'humidity': max(0, min(100, self._add_noise(self.current['humidity'], 0.02))),
            'activity': self.activity.value
        }
        
        return data
    
    def get_air_quality_level(self, data):
        """判断空气质量等级"""
        # 检查各项指标
        if (data['pm25'] > 150 or data['co'] > 100 or data['co2'] > 5000 or 
            data['temperature'] > 45 or data['humidity'] < 20 or data['humidity'] > 90):
            return 'danger'  # 危险
        elif (data['pm25'] > 75 or data['co'] > 35 or data['co2'] > 2000 or 
              data['temperature'] > 35 or data['humidity'] < 30 or data['humidity'] > 80):
            return 'warning'  # 警告
        else:
            return 'normal'  # 正常
    
    def should_alert(self, data):
        """判断是否需要告警"""
        level = self.get_air_quality_level(data)
        return level in ['warning', 'danger']
    
    def simulate_cooking_scenario(self, duration=60):
        """模拟完整的烹饪场景"""
        print(f"开始模拟烹饪场景，持续 {duration} 秒")
        print("-" * 80)
        
        scenarios = [
            (CookingActivity.IDLE, 10),  # 空闲10秒
            (CookingActivity.BOILING, 15),  # 煮水15秒
            (CookingActivity.FRYING, 20),  # 炒菜20秒（高污染）
            (CookingActivity.IDLE, 15)  # 恢复15秒
        ]
        
        elapsed = 0
        scenario_index = 0
        scenario_elapsed = 0
        
        while elapsed < duration:
            # 切换场景
            if scenario_index < len(scenarios):
                current_scenario, scenario_duration = scenarios[scenario_index]
                if scenario_elapsed == 0:
                    self.set_activity(current_scenario)
                
                if scenario_elapsed >= scenario_duration:
                    scenario_index += 1
                    scenario_elapsed = 0
                    continue
            
            # 读取数据
            data = self.read_sensors()
            level = self.get_air_quality_level(data)
            alert = "⚠️ 告警" if self.should_alert(data) else "✓ 正常"
            
            # 显示数据
            print(f"[{data['timestamp'][11:19]}] PM2.5:{data['pm25']:6.1f} CO:{data['co']:5.1f} "
                  f"CO2:{data['co2']:6.0f} T:{data['temperature']:4.1f}°C "
                  f"H:{data['humidity']:4.1f}% | {level:7s} {alert}")
            
            time.sleep(1)
            elapsed += 1
            scenario_elapsed += 1
        
        print("-" * 80)
        print("模拟完成")


def main():
    """主函数"""
    print("=" * 80)
    print("厨房空气质量数据模拟器")
    print("=" * 80)
    print()
    
    simulator = AirQualitySimulator()
    
    # 模拟烹饪场景
    simulator.simulate_cooking_scenario(duration=60)
    
    # 也可以手动测试
    print("\n" + "=" * 80)
    print("手动测试模式")
    print("=" * 80)
    
    test_activities = [
        CookingActivity.IDLE,
        CookingActivity.FRYING,
        CookingActivity.IDLE
    ]
    
    for activity in test_activities:
        simulator.set_activity(activity)
        for i in range(5):
            data = simulator.read_sensors()
            print(f"  PM2.5: {data['pm25']:.1f} μg/m³, CO: {data['co']:.1f} ppm, "
                  f"CO2: {data['co2']:.0f} ppm")
            time.sleep(0.5)
        print()


if __name__ == '__main__':
    main()
