from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import schedule
import time
import threading
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///livestream_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)

# 数据库模型
class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_locked = db.Column(db.Boolean, default=True)
    current_session = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'is_locked': self.is_locked,
            'current_session': self.current_session
        }

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, active, completed, cancelled
    actual_start_time = db.Column(db.DateTime, nullable=True)
    actual_end_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'user_name': self.user_name,
            'user_phone': self.user_phone,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'actual_start_time': self.actual_start_time.isoformat() if self.actual_start_time else None,
            'actual_end_time': self.actual_end_time.isoformat() if self.actual_end_time else None,
            'created_at': self.created_at.isoformat()
        }

class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=True)
    action = db.Column(db.String(20), nullable=False)  # unlock, lock, access_denied
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(200), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'room_id': self.room_id,
            'booking_id': self.booking_id,
            'action': self.action,
            'timestamp': self.timestamp.isoformat(),
            'reason': self.reason
        }

# 门禁控制类
class DoorController:
    def __init__(self):
        self.door_status = {}  # 存储每个房间的门禁状态
    
    def unlock_door(self, room_id):
        """解锁门禁"""
        room = Room.query.get(room_id)
        if room:
            room.is_locked = False
            db.session.commit()
            self.door_status[room_id] = 'unlocked'
            self.log_access(room_id, None, 'unlock', '门禁已解锁')
            return True
        return False
    
    def lock_door(self, room_id):
        """锁定门禁"""
        room = Room.query.get(room_id)
        if room:
            room.is_locked = True
            room.current_session = None
            db.session.commit()
            self.door_status[room_id] = 'locked'
            self.log_access(room_id, None, 'lock', '门禁已锁定')
            return True
        return False
    
    def check_access(self, room_id, user_phone):
        """检查访问权限"""
        now = datetime.now()
        
        # 查找当前有效的预约
        active_booking = Booking.query.filter(
            Booking.room_id == room_id,
            Booking.user_phone == user_phone,
            Booking.start_time <= now,
            Booking.end_time >= now,
            Booking.status == 'active'
        ).first()
        
        if active_booking:
            # 记录实际开始时间
            if not active_booking.actual_start_time:
                active_booking.actual_start_time = now
                db.session.commit()
            
            self.log_access(room_id, active_booking.id, 'access_granted', '预约时间内，允许进入')
            return True, "访问成功"
        else:
            self.log_access(room_id, None, 'access_denied', '无有效预约或时间不符')
            return False, "无有效预约或时间不符"
    
    def log_access(self, room_id, booking_id, action, reason):
        """记录访问日志"""
        log = AccessLog(
            room_id=room_id,
            booking_id=booking_id,
            action=action,
            reason=reason
        )
        db.session.add(log)
        db.session.commit()

# 全局门禁控制器
door_controller = DoorController()

# API 路由
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    rooms = Room.query.all()
    return jsonify([room.to_dict() for room in rooms])

@app.route('/api/rooms', methods=['POST'])
def create_room():
    data = request.get_json()
    room = Room(name=data['name'])
    db.session.add(room)
    db.session.commit()
    return jsonify(room.to_dict()), 201

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    bookings = Booking.query.order_by(Booking.start_time.desc()).all()
    return jsonify([booking.to_dict() for booking in bookings])

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    
    # 检查时间冲突
    conflicting_booking = Booking.query.filter(
        Booking.room_id == data['room_id'],
        Booking.status.in_(['pending', 'active']),
        Booking.start_time < data['end_time'],
        Booking.end_time > data['start_time']
    ).first()
    
    if conflicting_booking:
        return jsonify({'error': '该时间段已有预约'}), 400
    
    booking = Booking(
        room_id=data['room_id'],
        user_name=data['user_name'],
        user_phone=data['user_phone'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time'])
    )
    
    db.session.add(booking)
    db.session.commit()
    return jsonify(booking.to_dict()), 201

@app.route('/api/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    data = request.get_json()
    
    if 'status' in data:
        booking.status = data['status']
        
        if data['status'] == 'active':
            booking.actual_start_time = datetime.now()
        elif data['status'] == 'completed':
            booking.actual_end_time = datetime.now()
    
    db.session.commit()
    return jsonify(booking.to_dict())

@app.route('/api/access/<int:room_id>', methods=['POST'])
def check_access(room_id):
    data = request.get_json()
    user_phone = data.get('user_phone')
    
    if not user_phone:
        return jsonify({'error': '缺少用户手机号'}), 400
    
    success, message = door_controller.check_access(room_id, user_phone)
    
    if success:
        door_controller.unlock_door(room_id)
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'message': message})

@app.route('/api/door/<int:room_id>/lock', methods=['POST'])
def lock_door(room_id):
    success = door_controller.lock_door(room_id)
    if success:
        return jsonify({'success': True, 'message': '门禁已锁定'})
    else:
        return jsonify({'success': False, 'message': '锁定失败'})

@app.route('/api/door/<int:room_id>/unlock', methods=['POST'])
def unlock_door(room_id):
    success = door_controller.unlock_door(room_id)
    if success:
        return jsonify({'success': True, 'message': '门禁已解锁'})
    else:
        return jsonify({'success': False, 'message': '解锁失败'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs])

# 定时任务函数
def check_booking_times():
    """检查预约时间，自动开启和关闭门禁"""
    now = datetime.now()
    
    # 检查需要开始的预约
    pending_bookings = Booking.query.filter(
        Booking.status == 'pending',
        Booking.start_time <= now,
        Booking.end_time > now
    ).all()
    
    for booking in pending_bookings:
        booking.status = 'active'
        booking.actual_start_time = now
        room = Room.query.get(booking.room_id)
        if room:
            room.current_session = booking.id
            door_controller.unlock_door(booking.room_id)
        db.session.commit()
    
    # 检查需要结束的预约
    active_bookings = Booking.query.filter(
        Booking.status == 'active',
        Booking.end_time <= now
    ).all()
    
    for booking in active_bookings:
        booking.status = 'completed'
        booking.actual_end_time = now
        room = Room.query.get(booking.room_id)
        if room:
            door_controller.lock_door(booking.room_id)
        db.session.commit()

def run_scheduler():
    """运行定时任务"""
    schedule.every(30).seconds.do(check_booking_times)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# 初始化数据库
def init_db():
    with app.app_context():
        db.create_all()
        
        # 创建默认房间
        if not Room.query.first():
            default_room = Room(name="直播间1")
            db.session.add(default_room)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    
    # 启动定时任务线程
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=5000)