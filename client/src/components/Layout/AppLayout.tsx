import React, { useState } from 'react';
import { Layout, Menu, Avatar, Dropdown, Badge, Button, Drawer } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useNotifications } from '@/hooks/useNotifications';
import { UserRole } from '@/types';
import NotificationList from './NotificationList';

const { Header, Sider, Content } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [notificationDrawerVisible, setNotificationDrawerVisible] = useState(false);
  const { user, logout, isAdmin, isModerator, isStreamer } = useAuth();
  const { unreadCount, markAllAsRead } = useNotifications();
  const navigate = useNavigate();
  const location = useLocation();

  // 菜单项配置
  const menuItems = [
    {
      key: '/dashboard',
      icon: <UserOutlined />,
      label: '仪表盘',
      roles: [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR],
    },
    {
      key: '/users',
      icon: <UserOutlined />,
      label: '用户管理',
      roles: [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR],
    },
    {
      key: '/rooms',
      icon: <UserOutlined />,
      label: '直播管理',
      roles: [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR, UserRole.STREAMER],
    },
    {
      key: '/reports',
      icon: <UserOutlined />,
      label: '举报管理',
      roles: [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR],
    },
    {
      key: '/notifications',
      icon: <BellOutlined />,
      label: '通知管理',
      roles: [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR],
    },
  ];

  // 过滤菜单项
  const filteredMenuItems = menuItems.filter((item) => {
    if (!user) return false;
    return item.roles.includes(user.role);
  });

  // 用户下拉菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider' as const,
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      onClick: logout,
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  const handleNotificationClick = () => {
    setNotificationDrawerVisible(true);
  };

  const handleNotificationDrawerClose = () => {
    setNotificationDrawerVisible(false);
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider trigger={null} collapsible collapsed={collapsed}>
        <div style={{ 
          height: 32, 
          margin: 16, 
          background: 'rgba(255, 255, 255, 0.3)',
          borderRadius: 6,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 'bold'
        }}>
          {collapsed ? 'LS' : '直播管理'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={filteredMenuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          padding: '0 16px', 
          background: '#fff', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between' 
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            style={{ fontSize: '16px', width: 64, height: 64 }}
          />
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Badge count={unreadCount} size="small">
              <Button
                type="text"
                icon={<BellOutlined />}
                onClick={handleNotificationClick}
                style={{ fontSize: '16px' }}
              />
            </Badge>
            
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              arrow
            >
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: 8, 
                cursor: 'pointer',
                padding: '8px 12px',
                borderRadius: 6,
                transition: 'background-color 0.3s'
              }}>
                <Avatar 
                  src={user?.avatar} 
                  icon={<UserOutlined />} 
                  size="small"
                />
                <span>{user?.username}</span>
              </div>
            </Dropdown>
          </div>
        </Header>
        
        <Content style={{ 
          margin: '16px', 
          padding: 24, 
          background: '#fff', 
          borderRadius: 8,
          minHeight: 'calc(100vh - 112px)'
        }}>
          {children}
        </Content>
      </Layout>

      <Drawer
        title="通知中心"
        placement="right"
        onClose={handleNotificationDrawerClose}
        open={notificationDrawerVisible}
        width={400}
        extra={
          <Button 
            type="link" 
            onClick={markAllAsRead}
            disabled={unreadCount === 0}
          >
            全部已读
          </Button>
        }
      >
        <NotificationList />
      </Drawer>
    </Layout>
  );
};

export default AppLayout;