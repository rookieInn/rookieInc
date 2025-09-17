import React from 'react';
import { List, Avatar, Typography, Button, Empty, Spin } from 'antd';
import { BellOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNotifications } from '@/hooks/useNotifications';
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import 'dayjs/locale/zh-cn';

dayjs.extend(relativeTime);
dayjs.locale('zh-cn');

const { Text, Title } = Typography;

const NotificationList: React.FC = () => {
  const { 
    notifications, 
    isLoading, 
    markAsRead, 
    deleteNotification 
  } = useNotifications();

  const handleMarkAsRead = (id: string) => {
    markAsRead(id);
  };

  const handleDelete = (id: string) => {
    deleteNotification(id);
  };

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (notifications.length === 0) {
    return (
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description="暂无通知"
      />
    );
  }

  return (
    <List
      itemLayout="horizontal"
      dataSource={notifications}
      renderItem={(notification) => (
        <List.Item
          style={{
            backgroundColor: notification.isRead ? '#fff' : '#f0f9ff',
            padding: '12px 16px',
            marginBottom: 8,
            borderRadius: 6,
            border: notification.isRead ? 'none' : '1px solid #e6f7ff',
          }}
          actions={[
            !notification.isRead && (
              <Button
                type="link"
                size="small"
                onClick={() => handleMarkAsRead(notification._id)}
              >
                标记已读
              </Button>
            ),
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(notification._id)}
            />
          ]}
        >
          <List.Item.Meta
            avatar={
              <Avatar 
                icon={<BellOutlined />} 
                style={{ 
                  backgroundColor: notification.isRead ? '#d9d9d9' : '#1890ff' 
                }}
              />
            }
            title={
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Title level={5} style={{ margin: 0 }}>
                  {notification.title}
                </Title>
                {!notification.isRead && (
                  <div
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: '#ff4d4f',
                    }}
                  />
                )}
              </div>
            }
            description={
              <div>
                <Text type="secondary">{notification.message}</Text>
                <br />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {dayjs(notification.createdAt).fromNow()}
                </Text>
              </div>
            }
          />
        </List.Item>
      )}
    />
  );
};

export default NotificationList;