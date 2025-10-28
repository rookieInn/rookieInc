import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useNotificationStore } from '@/store/notificationStore';
import { apiService } from '@/services/api';
import { message } from 'antd';

export const useNotifications = () => {
  const {
    notifications,
    unreadCount,
    isLoading,
    setNotifications,
    addNotification,
    markAsRead: markAsReadStore,
    markAllAsRead: markAllAsReadStore,
    removeNotification,
    setUnreadCount,
    setLoading,
  } = useNotificationStore();

  const queryClient = useQueryClient();

  // 获取通知列表
  const { data: notificationsData, refetch: refetchNotifications } = useQuery(
    'notifications',
    () => apiService.getNotifications({ limit: 50 }),
    {
      onSuccess: (response) => {
        if (response.success && response.data) {
          setNotifications(response.data);
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '获取通知失败');
      },
    }
  );

  // 获取未读数量
  const { data: unreadCountData } = useQuery(
    'unread-count',
    () => apiService.getUnreadCount(),
    {
      onSuccess: (response) => {
        if (response.success && response.data) {
          setUnreadCount(response.data.count);
        }
      },
      refetchInterval: 30000, // 30秒刷新一次
    }
  );

  // 标记为已读
  const markAsReadMutation = useMutation(
    (id: string) => apiService.markAsRead(id),
    {
      onSuccess: (response, id) => {
        if (response.success) {
          markAsReadStore(id);
        } else {
          message.error(response.message || '标记失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '标记失败');
      },
    }
  );

  // 标记所有为已读
  const markAllAsReadMutation = useMutation(
    () => apiService.markAllAsRead(),
    {
      onSuccess: (response) => {
        if (response.success) {
          markAllAsReadStore();
          message.success('所有通知已标记为已读');
        } else {
          message.error(response.message || '标记失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '标记失败');
      },
    }
  );

  // 删除通知
  const deleteNotificationMutation = useMutation(
    (id: string) => apiService.deleteNotification(id),
    {
      onSuccess: (response, id) => {
        if (response.success) {
          removeNotification(id);
          message.success('通知已删除');
        } else {
          message.error(response.message || '删除失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '删除失败');
      },
    }
  );

  // 发送系统通知
  const sendSystemNotificationMutation = useMutation(
    (data: any) => apiService.sendSystemNotification(data),
    {
      onSuccess: (response) => {
        if (response.success) {
          message.success('系统通知发送成功');
          refetchNotifications();
        } else {
          message.error(response.message || '发送失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '发送失败');
      },
    }
  );

  // 标记为已读
  const handleMarkAsRead = (id: string) => {
    markAsReadMutation.mutate(id);
  };

  // 标记所有为已读
  const handleMarkAllAsRead = () => {
    markAllAsReadMutation.mutate();
  };

  // 删除通知
  const handleDeleteNotification = (id: string) => {
    deleteNotificationMutation.mutate(id);
  };

  // 发送系统通知
  const handleSendSystemNotification = (data: any) => {
    sendSystemNotificationMutation.mutate(data);
  };

  // 刷新通知
  const refreshNotifications = () => {
    refetchNotifications();
  };

  return {
    notifications,
    unreadCount,
    isLoading,
    markAsRead: handleMarkAsRead,
    markAllAsRead: handleMarkAllAsRead,
    deleteNotification: handleDeleteNotification,
    sendSystemNotification: handleSendSystemNotification,
    refreshNotifications,
    isMarkAsReadLoading: markAsReadMutation.isLoading,
    isMarkAllAsReadLoading: markAllAsReadMutation.isLoading,
    isDeleteLoading: deleteNotificationMutation.isLoading,
    isSendSystemNotificationLoading: sendSystemNotificationMutation.isLoading,
  };
};