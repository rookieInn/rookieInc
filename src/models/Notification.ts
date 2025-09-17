import mongoose, { Document, Schema } from 'mongoose';
import { Notification as INotification, NotificationType } from '@/types';

export interface NotificationDocument extends INotification, Document {}

const notificationSchema = new Schema<NotificationDocument>({
  userId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: {
    type: String,
    required: true,
    trim: true,
    maxlength: 100
  },
  message: {
    type: String,
    required: true,
    trim: true,
    maxlength: 500
  },
  type: {
    type: String,
    enum: Object.values(NotificationType),
    required: true
  },
  isRead: {
    type: Boolean,
    default: false
  },
  data: {
    type: Schema.Types.Mixed,
    default: null
  }
}, {
  timestamps: true
});

// 标记为已读
notificationSchema.methods.markAsRead = function() {
  this.isRead = true;
  return this.save();
};

// 批量标记为已读
notificationSchema.statics.markAllAsRead = function(userId: string) {
  return this.updateMany(
    { userId, isRead: false },
    { isRead: true }
  );
};

// 获取用户未读通知数量
notificationSchema.statics.getUnreadCount = function(userId: string) {
  return this.countDocuments({ userId, isRead: false });
};

// 索引
notificationSchema.index({ userId: 1, isRead: 1 });
notificationSchema.index({ type: 1 });
notificationSchema.index({ createdAt: -1 });

// TTL索引，自动删除30天前的通知
notificationSchema.index({ createdAt: 1 }, { expireAfterSeconds: 2592000 });

export const Notification = mongoose.model<NotificationDocument>('Notification', notificationSchema);