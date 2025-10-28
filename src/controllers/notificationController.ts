import { Request, Response } from 'express';
import { NotificationService } from '@/services/notificationService';
import { asyncHandler } from '@/middleware/errorHandler';
import { PaginationQuery } from '@/types';

export class NotificationController {
  // 获取用户通知列表
  static getUserNotifications = asyncHandler(async (req: Request, res: Response) => {
    const userId = (req as any).user._id;
    const query: PaginationQuery & any = req.query;
    
    const result = await NotificationService.getUserNotifications(userId, query);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取单个通知
  static getNotificationById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const userId = (req as any).user._id;
    
    const result = await NotificationService.getNotificationById(id, userId);
    
    res.status(result.success ? 200 : 404).json(result);
  });

  // 标记通知为已读
  static markAsRead = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const userId = (req as any).user._id;
    
    const result = await NotificationService.markAsRead(id, userId);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 标记所有通知为已读
  static markAllAsRead = asyncHandler(async (req: Request, res: Response) => {
    const userId = (req as any).user._id;
    
    const result = await NotificationService.markAllAsRead(userId);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 删除通知
  static deleteNotification = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const userId = (req as any).user._id;
    
    const result = await NotificationService.deleteNotification(id, userId);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取未读通知数量
  static getUnreadCount = asyncHandler(async (req: Request, res: Response) => {
    const userId = (req as any).user._id;
    
    const result = await NotificationService.getUnreadCount(userId);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 发送系统通知（管理员功能）
  static sendSystemNotification = asyncHandler(async (req: Request, res: Response) => {
    const { title, message, targetRoles, targetUsers } = req.body;
    
    const result = await NotificationService.sendSystemNotification(
      title, 
      message, 
      targetRoles, 
      targetUsers
    );
    
    res.status(result.success ? 201 : 400).json(result);
  });

  // 获取通知统计信息
  static getNotificationStats = asyncHandler(async (req: Request, res: Response) => {
    const userId = (req as any).user._id;
    
    const result = await NotificationService.getNotificationStats(userId);
    
    res.status(result.success ? 200 : 400).json(result);
  });
}