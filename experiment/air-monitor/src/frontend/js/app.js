/**
 * 厨房空气质量监测系统 - 前端JavaScript
 */

// API基础URL
const API_BASE = 'http://localhost:5000/api';

// Chart.js实例
let trendChart = null;

// 历史数据
let historyData = {
    labels: [],
    pm25: [],
    co: [],
    co2: [],
    temperature: [],
    humidity: []
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initChart();
    startDataPolling();
    updateTime();
    setInterval(updateTime, 1000);
});

/**
 * 初始化图表
 */
function initChart() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'PM2.5 (μg/m³)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    yAxisID: 'y',
                },
                {
                    label: 'CO (ppm)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    yAxisID: 'y',
                },
                {
                    label: 'CO2 (ppm)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'PM2.5 / CO'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'CO2'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

/**
 * 更新时间显示
 */
function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('zh-CN', { 
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    document.getElementById('currentTime').textContent = timeStr;
}

/**
 * 开始数据轮询
 */
function startDataPolling() {
    // 立即获取一次数据
    fetchCurrentData();
    
    // 每2秒更新一次当前数据
    setInterval(fetchCurrentData, 2000);
    
    // 每10秒更新一次历史数据
    setInterval(fetchHistoryData, 10000);
    
    // 每30秒更新一次统计信息
    setInterval(fetchStatistics, 30000);
}

/**
 * 获取当前数据
 */
async function fetchCurrentData() {
    try {
        const response = await fetch(`${API_BASE}/current`);
        const result = await response.json();
        
        if (result.success) {
            updateCurrentDisplay(result.data, result.level, result.alert);
        }
    } catch (error) {
        console.error('获取当前数据失败:', error);
        document.getElementById('systemStatus').textContent = '连接失败';
    }
}

/**
 * 获取历史数据
 */
async function fetchHistoryData() {
    try {
        const response = await fetch(`${API_BASE}/history?hours=1&limit=50`);
        const result = await response.json();
        
        if (result.success && result.data.length > 0) {
            updateChart(result.data);
        }
    } catch (error) {
        console.error('获取历史数据失败:', error);
    }
}

/**
 * 获取统计信息
 */
async function fetchStatistics() {
    try {
        const response = await fetch(`${API_BASE}/stats`);
        const result = await response.json();
        
        if (result.success && result.stats) {
            updateStatistics(result.stats);
        }
    } catch (error) {
        console.error('获取统计信息失败:', error);
    }
}

/**
 * 更新当前数据显示
 */
function updateCurrentDisplay(data, level, alert) {
    // 更新数值
    document.getElementById('pm25Value').textContent = data.pm25.toFixed(1);
    document.getElementById('coValue').textContent = data.co.toFixed(1);
    document.getElementById('co2Value').textContent = data.co2.toFixed(0);
    document.getElementById('tempValue').textContent = data.temperature.toFixed(1);
    document.getElementById('humidityValue').textContent = data.humidity.toFixed(1);
    
    // 更新卡片颜色
    updateCardColor('pm25Card', data.pm25, 75, 150);
    updateCardColor('coCard', data.co, 35, 100);
    updateCardColor('co2Card', data.co2, 2000, 5000);
    updateCardColor('tempCard', data.temperature, 35, 45);
    updateCardColorHumidity('humidityCard', data.humidity);
    
    // 更新状态指示器
    const indicator = document.getElementById('statusIndicator');
    indicator.className = 'status-indicator';
    if (level === 'danger') {
        indicator.classList.add('status-danger');
        document.getElementById('currentStatus').textContent = '危险';
    } else if (level === 'warning') {
        indicator.classList.add('status-warning');
        document.getElementById('currentStatus').textContent = '警告';
    } else {
        indicator.classList.add('status-normal');
        document.getElementById('currentStatus').textContent = '正常';
    }
    
    // 显示/隐藏告警徽章
    const alertBadge = document.getElementById('alertBadge');
    if (alert) {
        alertBadge.style.display = 'block';
    } else {
        alertBadge.style.display = 'none';
    }
    
    // 更新系统状态
    document.getElementById('systemStatus').textContent = '系统运行中';
}

/**
 * 更新卡片颜色（普通传感器）
 */
function updateCardColor(cardId, value, warningThreshold, dangerThreshold) {
    const card = document.getElementById(cardId);
    card.style.borderLeft = '5px solid';
    
    if (value >= dangerThreshold) {
        card.style.borderColor = '#dc3545';
        card.style.backgroundColor = '#f8d7da';
    } else if (value >= warningThreshold) {
        card.style.borderColor = '#ffc107';
        card.style.backgroundColor = '#fff3cd';
    } else {
        card.style.borderColor = '#28a745';
        card.style.backgroundColor = '#d4edda';
    }
}

/**
 * 更新湿度卡片颜色
 */
function updateCardColorHumidity(cardId, value) {
    const card = document.getElementById(cardId);
    card.style.borderLeft = '5px solid';
    
    if (value < 20 || value > 90) {
        card.style.borderColor = '#dc3545';
        card.style.backgroundColor = '#f8d7da';
    } else if (value < 30 || value > 80) {
        card.style.borderColor = '#ffc107';
        card.style.backgroundColor = '#fff3cd';
    } else {
        card.style.borderColor = '#28a745';
        card.style.backgroundColor = '#d4edda';
    }
}

/**
 * 更新图表
 */
function updateChart(data) {
    const labels = data.map(d => {
        const time = new Date(d.timestamp);
        return time.toLocaleTimeString('zh-CN', { hour12: false });
    });
    
    const pm25Data = data.map(d => d.pm25);
    const coData = data.map(d => d.co);
    const co2Data = data.map(d => d.co2);
    
    trendChart.data.labels = labels;
    trendChart.data.datasets[0].data = pm25Data;
    trendChart.data.datasets[1].data = coData;
    trendChart.data.datasets[2].data = co2Data;
    
    trendChart.update();
}

/**
 * 更新统计信息
 */
function updateStatistics(stats) {
    document.getElementById('totalRecords').textContent = stats.total_records || 0;
    document.getElementById('totalAlerts').textContent = stats.total_alerts || 0;
}

/**
 * 设置烹饪活动（演示用）
 */
async function setActivity(activity) {
    try {
        const response = await fetch(`${API_BASE}/activity`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ activity: activity })
        });
        
        const result = await response.json();
        
        if (result.success) {
            console.log('活动已切换:', activity);
            // 立即刷新数据
            fetchCurrentData();
        } else {
            console.error('切换活动失败:', result.message);
        }
    } catch (error) {
        console.error('切换活动失败:', error);
    }
}
