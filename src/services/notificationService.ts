import { Notification, NotificationDocument } from '@/models/Notification';
import { User } from '@/models/User';
import { NotificationType, PaginationQuery, ApiResponse } from '@/types';

export class NotificationService {
  // 创建通知
  static async createNotification(
    userId: string,
    title: string,
    message: string,
    type: NotificationType,
    data?: any
  ): Promise<ApiResponse<NotificationDocument>> {
    try {
      const notification = new Notification({
        userId,
        title,
        message,
        type,
        data
      });

      await notification.save();

      return {
        success: true,
        message: '通知创建成功',
        data: notification
      };
    } catch (error) {
      throw error;
    }
  }

  // 批量创建通知
  static async createBulkNotifications(
    userIds: string[],
    title: string,
    message: string,
    type: NotificationType,
    data?: any
  ): Promise<ApiResponse<NotificationDocument[]>> {
    try {
      const notifications = userIds.map(userId => ({
        userId,
        title,
        message,
        type,
        data
      }));

      const createdNotifications = await Notification.insertMany(notifications);

      return {
        success: true,
        message: '批量通知创建成功',
        data: createdNotifications
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取用户通知列表
  static async getUserNotifications(
    userId: string,
    query: PaginationQuery & { isRead?: boolean; type?: NotificationType }
  ): Promise<ApiResponse<NotificationDocument[]>> {
    try {
      const {
        page = 1,
        limit = 10,
        sort = 'createdAt',
        order = 'desc',
        isRead,
        type
      } = query;

      // 构建查询条件
      const filter: any = { userId };
      
      if (isRead !== undefined) filter.isRead = isRead;
      if (type) filter.type = type;

      // 计算分页
      const skip = (page - 1) * limit;
      const sortOrder = order === 'asc' ? 1 : -1;

      // 查询数据
      const [notifications, total] = await Promise.all([
        Notification.find(filter)
          .sort({ [sort]: sortOrder })
          .skip(skip)
          .limit(limit),
        Notification.countDocuments(filter)
      ]);

      return {
        success: true,
        message: '获取通知列表成功',
        data: notifications,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        }
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取单个通知
  static async getNotificationById(
    notificationId: string,
    userId: string
  ): Promise<ApiResponse<NotificationDocument>> {
    try {
      const notification = await Notification.findOne({
        _id: notificationId,
        userId
      });

      if (!notification) {
        return {
          success: false,
          message: '通知不存在'
        };
      }

      return {
        success: true,
        message: '获取通知成功',
        data: notification
      };
    } catch (error) {
      throw error;
    }
  }

  // 标记通知为已读
  static async markAsRead(
    notificationId: string,
    userId: string
  ): Promise<ApiResponse<NotificationDocument>> {
    try {
      const notification = await Notification.findOne({
        _id: notificationId,
        userId
      });

      if (!notification) {
        return {
          success: false,
          message: '通知不存在'
        };
      }

      await notification.markAsRead();

      return {
        success: true,
        message: '通知已标记为已读',
        data: notification
      };
    } catch (error) {
      throw error;
    }
  }

  // 标记所有通知为已读
  static async markAllAsRead(userId: string): Promise<ApiResponse> {
    try {
      await Notification.markAllAsRead(userId);

      return {
        success: true,
        message: '所有通知已标记为已读'
      };
    } catch (error) {
      throw error;
    }
  }

  // 删除通知
  static async deleteNotification(
    notificationId: string,
    userId: string
  ): Promise<ApiResponse> {
    try {
      const notification = await Notification.findOneAndDelete({
        _id: notificationId,
        userId
      });

      if (!notification) {
        return {
          success: false,
          message: '通知不存在'
        };
      }

      return {
        success: true,
        message: '通知删除成功'
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取未读通知数量
  static async getUnreadCount(userId: string): Promise<ApiResponse<{ count: number }>> {
    try {
      const count = await Notification.getUnreadCount(userId);

      return {
        success: true,
        message: '获取未读通知数量成功',
        data: { count }
      };
    } catch (error) {
      throw error;
    }
  }

  // 发送系统通知
  static async sendSystemNotification(
    title: string,
    message: string,
    targetRoles?: string[],
    targetUsers?: string[]
  ): Promise<ApiResponse<NotificationDocument[]>> {
    try {
      let userIds: string[] = [];

      if (targetRoles && targetRoles.length > 0) {
        const users = await User.find({ role: { $in: targetRoles } }).select('_id');
        userIds = users.map(user => user._id.toString());
      }

      if (targetUsers && targetUsers.length > 0) {
        userIds = [...userIds, ...targetUsers];
      }

      if (userIds.length === 0) {
        // 如果没有指定目标，发送给所有用户
        const allUsers = await User.find().select('_id');
        userIds = allUsers.map(user => user._id.toString());
      }

      const result = await this.createBulkNotifications(
        userIds,
        title,
        message,
        NotificationType.SYSTEM
      );

      return result;
    } catch (error) {
      throw error;
    }
  }

  // 获取通知统计信息
  static async getNotificationStats(userId: string): Promise<ApiResponse<any>> {
    try {
      const [
        totalNotifications,
        unreadNotifications,
        notificationsToday,
        notificationsThisWeek,
        notificationsThisMonth
      ] = await Promise.all([
        Notification.countDocuments({ userId }),
        Notification.countDocuments({ userId, isRead: false }),
        Notification.countDocuments({
          userId,
          createdAt: { $gte: new Date(new Date().setHours(0, 0, 0, 0)) }
        }),
        Notification.countDocuments({
          userId,
          createdAt: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
        }),
        Notification.countDocuments({
          userId,
          createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
        })
      ]);

      const stats = {
        totalNotifications,
        unreadNotifications,
        readNotifications: totalNotifications - unreadNotifications,
        notificationsToday,
        notificationsThisWeek,
        notificationsThisMonth
      };

      return {
        success: true,
        message: '获取通知统计成功',
        data: stats
      };
    } catch (error) {
      throw error;
    }
  }
}