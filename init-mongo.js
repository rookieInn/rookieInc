// MongoDB初始化脚本
db = db.getSiblingDB('live_streaming_admin');

// 创建应用用户
db.createUser({
  user: 'app_user',
  pwd: 'app_password',
  roles: [
    {
      role: 'readWrite',
      db: 'live_streaming_admin'
    }
  ]
});

// 创建索引
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ username: 1 }, { unique: true });
db.users.createIndex({ role: 1 });
db.users.createIndex({ isActive: 1 });

db.liverooms.createIndex({ streamerId: 1 });
db.liverooms.createIndex({ status: 1 });
db.liverooms.createIndex({ category: 1 });
db.liverooms.createIndex({ isPublic: 1 });
db.liverooms.createIndex({ isFeatured: 1 });
db.liverooms.createIndex({ createdAt: -1 });
db.liverooms.createIndex({ viewerCount: -1 });

db.streamstats.createIndex({ roomId: 1, timestamp: 1 });
db.streamstats.createIndex({ timestamp: -1 });
db.streamstats.createIndex({ timestamp: 1 }, { expireAfterSeconds: 2592000 }); // 30天TTL

db.reports.createIndex({ reporterId: 1 });
db.reports.createIndex({ targetType: 1, targetId: 1 });
db.reports.createIndex({ status: 1 });
db.reports.createIndex({ moderatorId: 1 });
db.reports.createIndex({ createdAt: -1 });

db.notifications.createIndex({ userId: 1, isRead: 1 });
db.notifications.createIndex({ type: 1 });
db.notifications.createIndex({ createdAt: -1 });
db.notifications.createIndex({ createdAt: 1 }, { expireAfterSeconds: 2592000 }); // 30天TTL

print('数据库初始化完成');