"""
门禁硬件接口模拟器
模拟真实的门禁硬件设备，包括门锁、传感器等
"""

import time
import random
import threading
from datetime import datetime
import json

class DoorHardwareSimulator:
    def __init__(self):
        self.door_states = {}  # 存储每个房间的门锁状态
        self.sensors = {}      # 存储传感器状态
        self.callbacks = []    # 回调函数列表
        
    def register_callback(self, callback):
        """注册状态变化回调函数"""
        self.callbacks.append(callback)
    
    def notify_callbacks(self, room_id, event_type, data):
        """通知所有回调函数"""
        for callback in self.callbacks:
            try:
                callback(room_id, event_type, data)
            except Exception as e:
                print(f"回调函数执行失败: {e}")
    
    def unlock_door(self, room_id):
        """解锁门禁"""
        print(f"[{datetime.now()}] 房间 {room_id} 门禁解锁")
        self.door_states[room_id] = {
            'locked': False,
            'unlock_time': datetime.now(),
            'last_action': 'unlock'
        }
        self.notify_callbacks(room_id, 'door_unlocked', {
            'room_id': room_id,
            'timestamp': datetime.now().isoformat()
        })
        return True
    
    def lock_door(self, room_id):
        """锁定门禁"""
        print(f"[{datetime.now()}] 房间 {room_id} 门禁锁定")
        self.door_states[room_id] = {
            'locked': True,
            'lock_time': datetime.now(),
            'last_action': 'lock'
        }
        self.notify_callbacks(room_id, 'door_locked', {
            'room_id': room_id,
            'timestamp': datetime.now().isoformat()
        })
        return True
    
    def is_door_locked(self, room_id):
        """检查门禁是否锁定"""
        return self.door_states.get(room_id, {}).get('locked', True)
    
    def get_door_status(self, room_id):
        """获取门禁状态"""
        return self.door_states.get(room_id, {
            'locked': True,
            'last_action': 'unknown'
        })
    
    def simulate_motion_sensor(self, room_id, motion_detected=True):
        """模拟运动传感器"""
        self.sensors[room_id] = {
            'motion_detected': motion_detected,
            'last_motion': datetime.now() if motion_detected else None
        }
        
        if motion_detected:
            print(f"[{datetime.now()}] 房间 {room_id} 检测到运动")
            self.notify_callbacks(room_id, 'motion_detected', {
                'room_id': room_id,
                'timestamp': datetime.now().isoformat()
            })
    
    def simulate_door_sensor(self, room_id, door_open=True):
        """模拟门开关传感器"""
        door_state = self.sensors.get(room_id, {})
        door_state['door_open'] = door_open
        door_state['last_door_change'] = datetime.now()
        self.sensors[room_id] = door_state
        
        status = "打开" if door_open else "关闭"
        print(f"[{datetime.now()}] 房间 {room_id} 门{status}")
        
        self.notify_callbacks(room_id, 'door_state_changed', {
            'room_id': room_id,
            'door_open': door_open,
            'timestamp': datetime.now().isoformat()
        })
    
    def simulate_emergency_button(self, room_id):
        """模拟紧急按钮"""
        print(f"[{datetime.now()}] 房间 {room_id} 紧急按钮被按下")
        self.notify_callbacks(room_id, 'emergency_button', {
            'room_id': room_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # 紧急情况下强制解锁
        self.unlock_door(room_id)
        return True
    
    def simulate_power_failure(self, room_id):
        """模拟断电情况"""
        print(f"[{datetime.now()}] 房间 {room_id} 发生断电")
        self.notify_callbacks(room_id, 'power_failure', {
            'room_id': room_id,
            'timestamp': datetime.now().isoformat()
        })
        
        # 断电时门禁应该保持锁定状态
        self.door_states[room_id] = {
            'locked': True,
            'power_failure': True,
            'failure_time': datetime.now()
        }
    
    def restore_power(self, room_id):
        """恢复供电"""
        print(f"[{datetime.now()}] 房间 {room_id} 供电恢复")
        door_state = self.door_states.get(room_id, {})
        door_state.pop('power_failure', None)
        door_state.pop('failure_time', None)
        
        self.notify_callbacks(room_id, 'power_restored', {
            'room_id': room_id,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_room_status(self, room_id):
        """获取房间完整状态"""
        return {
            'door_state': self.get_door_status(room_id),
            'sensors': self.sensors.get(room_id, {}),
            'timestamp': datetime.now().isoformat()
        }
    
    def start_simulation(self):
        """启动硬件模拟"""
        def simulation_loop():
            while True:
                try:
                    # 随机模拟一些硬件事件
                    for room_id in self.door_states.keys():
                        # 随机模拟运动检测
                        if random.random() < 0.1:  # 10% 概率
                            self.simulate_motion_sensor(room_id, random.choice([True, False]))
                        
                        # 随机模拟门开关
                        if random.random() < 0.05:  # 5% 概率
                            self.simulate_door_sensor(room_id, random.choice([True, False]))
                        
                        # 随机模拟紧急情况
                        if random.random() < 0.001:  # 0.1% 概率
                            self.simulate_emergency_button(room_id)
                    
                    time.sleep(10)  # 每10秒检查一次
                except Exception as e:
                    print(f"硬件模拟循环错误: {e}")
                    time.sleep(5)
        
        simulation_thread = threading.Thread(target=simulation_loop, daemon=True)
        simulation_thread.start()
        print("硬件模拟器已启动")

# 全局硬件模拟器实例
hardware_simulator = DoorHardwareSimulator()

def get_hardware_simulator():
    """获取硬件模拟器实例"""
    return hardware_simulator

if __name__ == "__main__":
    # 测试硬件模拟器
    simulator = DoorHardwareSimulator()
    
    def test_callback(room_id, event_type, data):
        print(f"回调: 房间{room_id} 事件:{event_type} 数据:{data}")
    
    simulator.register_callback(test_callback)
    
    # 测试基本功能
    simulator.unlock_door(1)
    simulator.simulate_motion_sensor(1, True)
    simulator.simulate_door_sensor(1, True)
    time.sleep(2)
    simulator.lock_door(1)
    simulator.simulate_door_sensor(1, False)
    
    # 启动模拟循环
    simulator.start_simulation()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("硬件模拟器已停止")