import { Router } from 'express';
import { NotificationController } from '@/controllers/notificationController';
import { authenticate, requireAdmin } from '@/middleware/auth';
import { validateQuery } from '@/middleware/validation';
import { commonSchemas } from '@/middleware/validation';

const router = Router();

// 所有路由都需要认证
router.use(authenticate);

// 获取用户通知列表
router.get('/', 
  validateQuery(commonSchemas.pagination), 
  NotificationController.getUserNotifications
);

// 获取未读通知数量
router.get('/unread-count', NotificationController.getUnreadCount);

// 获取通知统计信息
router.get('/stats', NotificationController.getNotificationStats);

// 获取单个通知
router.get('/:id', NotificationController.getNotificationById);

// 标记通知为已读
router.patch('/:id/read', NotificationController.markAsRead);

// 标记所有通知为已读
router.patch('/mark-all-read', NotificationController.markAllAsRead);

// 删除通知
router.delete('/:id', NotificationController.deleteNotification);

// 发送系统通知（管理员功能）
router.post('/system', 
  requireAdmin,
  NotificationController.sendSystemNotification
);

export default router;