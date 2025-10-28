import { useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { useAuthStore } from '@/store/authStore';
import { apiService } from '@/services/api';
import { User, LoginRequest, RegisterRequest } from '@/types';
import { message } from 'antd';

export const useAuth = () => {
  const {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    logout,
    updateUser,
    setLoading,
    hasRole,
    hasAnyRole,
  } = useAuthStore();

  const queryClient = useQueryClient();

  // 获取用户信息
  const { data: profileData, isLoading: profileLoading } = useQuery(
    'profile',
    () => apiService.getProfile(),
    {
      enabled: isAuthenticated && !!token,
      onSuccess: (response) => {
        if (response.success && response.data) {
          updateUser(response.data);
        }
      },
      onError: () => {
        logout();
      },
    }
  );

  // 登录
  const loginMutation = useMutation(
    (data: LoginRequest) => apiService.login(data.email, data.password),
    {
      onSuccess: (response) => {
        if (response.success && response.data) {
          const { user, token } = response.data;
          login(user, token);
          message.success('登录成功');
        } else {
          message.error(response.message || '登录失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '登录失败');
      },
    }
  );

  // 注册
  const registerMutation = useMutation(
    (data: RegisterRequest) => apiService.register(data),
    {
      onSuccess: (response) => {
        if (response.success && response.data) {
          const { user, token } = response.data;
          login(user, token);
          message.success('注册成功');
        } else {
          message.error(response.message || '注册失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '注册失败');
      },
    }
  );

  // 更新用户信息
  const updateProfileMutation = useMutation(
    (data: Partial<User>) => apiService.updateProfile(data),
    {
      onSuccess: (response) => {
        if (response.success && response.data) {
          updateUser(response.data);
          message.success('用户信息更新成功');
        } else {
          message.error(response.message || '更新失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '更新失败');
      },
    }
  );

  // 修改密码
  const changePasswordMutation = useMutation(
    (data: { currentPassword: string; newPassword: string }) =>
      apiService.changePassword(data),
    {
      onSuccess: (response) => {
        if (response.success) {
          message.success('密码修改成功');
        } else {
          message.error(response.message || '密码修改失败');
        }
      },
      onError: (error: any) => {
        message.error(error.response?.data?.message || '密码修改失败');
      },
    }
  );

  // 登出
  const handleLogout = () => {
    logout();
    queryClient.clear();
    message.success('已退出登录');
  };

  // 检查权限
  const checkPermission = (requiredRoles: string[]) => {
    if (!user) return false;
    return hasAnyRole(requiredRoles as any);
  };

  // 检查是否为管理员
  const isAdmin = () => {
    return hasAnyRole(['super_admin', 'admin']);
  };

  // 检查是否为审核员
  const isModerator = () => {
    return hasAnyRole(['super_admin', 'admin', 'moderator']);
  };

  // 检查是否为主播
  const isStreamer = () => {
    return hasAnyRole(['super_admin', 'admin', 'moderator', 'streamer']);
  };

  return {
    user,
    token,
    isAuthenticated,
    isLoading: isLoading || profileLoading,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    updateProfile: updateProfileMutation.mutate,
    changePassword: changePasswordMutation.mutate,
    logout: handleLogout,
    hasRole,
    hasAnyRole,
    checkPermission,
    isAdmin,
    isModerator,
    isStreamer,
    isLoginLoading: loginMutation.isLoading,
    isRegisterLoading: registerMutation.isLoading,
    isUpdateLoading: updateProfileMutation.isLoading,
    isChangePasswordLoading: changePasswordMutation.isLoading,
  };
};