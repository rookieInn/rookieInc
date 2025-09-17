import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiResponse } from '@/types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.api.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        return response;
      },
      (error) => {
        if (error.response?.status === 401) {
          // 清除本地存储的token
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          // 重定向到登录页
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // 通用请求方法
  async get<T>(url: string, params?: any): Promise<ApiResponse<T>> {
    const response = await this.api.get(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.post(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.put(url, data);
    return response.data;
  }

  async patch<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.patch(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    const response = await this.api.delete(url);
    return response.data;
  }

  // 认证相关
  async login(email: string, password: string) {
    return this.post('/auth/login', { email, password });
  }

  async register(data: any) {
    return this.post('/auth/register', data);
  }

  async getProfile() {
    return this.get('/auth/profile');
  }

  async updateProfile(data: any) {
    return this.put('/auth/profile', data);
  }

  async changePassword(data: any) {
    return this.post('/auth/change-password', data);
  }

  // 用户管理
  async getUsers(params?: any) {
    return this.get('/users', params);
  }

  async getUserById(id: string) {
    return this.get(`/users/${id}`);
  }

  async updateUser(id: string, data: any) {
    return this.put(`/users/${id}`, data);
  }

  async deleteUser(id: string) {
    return this.delete(`/users/${id}`);
  }

  async toggleUserStatus(id: string) {
    return this.patch(`/users/${id}/toggle-status`);
  }

  async getUserStats() {
    return this.get('/users/stats');
  }

  async getUserRoleDistribution() {
    return this.get('/users/role-distribution');
  }

  // 直播房间管理
  async getRooms(params?: any) {
    return this.get('/rooms', params);
  }

  async getRoomById(id: string) {
    return this.get(`/rooms/${id}`);
  }

  async createRoom(data: any) {
    return this.post('/rooms', data);
  }

  async updateRoom(id: string, data: any) {
    return this.put(`/rooms/${id}`, data);
  }

  async deleteRoom(id: string) {
    return this.delete(`/rooms/${id}`);
  }

  async startLive(id: string) {
    return this.post(`/rooms/${id}/start`);
  }

  async endLive(id: string) {
    return this.post(`/rooms/${id}/end`);
  }

  async updateViewerCount(id: string, count: number) {
    return this.put(`/rooms/${id}/viewer-count`, { count });
  }

  async getRoomStats(id: string, params?: any) {
    return this.get(`/rooms/${id}/stats`, params);
  }

  async getFeaturedRooms(limit?: number) {
    return this.get('/rooms/featured', { limit });
  }

  // 举报管理
  async getReports(params?: any) {
    return this.get('/reports', params);
  }

  async getReportById(id: string) {
    return this.get(`/reports/${id}`);
  }

  async createReport(data: any) {
    return this.post('/reports', data);
  }

  async assignModerator(id: string, moderatorId: string) {
    return this.post(`/reports/${id}/assign`, { moderatorId });
  }

  async resolveReport(id: string, action?: string) {
    return this.post(`/reports/${id}/resolve`, { action });
  }

  async rejectReport(id: string, reason?: string) {
    return this.post(`/reports/${id}/reject`, { reason });
  }

  async getReportStats() {
    return this.get('/reports/stats');
  }

  async getReportReasonDistribution() {
    return this.get('/reports/reason-distribution');
  }

  // 通知管理
  async getNotifications(params?: any) {
    return this.get('/notifications', params);
  }

  async getNotificationById(id: string) {
    return this.get(`/notifications/${id}`);
  }

  async markAsRead(id: string) {
    return this.patch(`/notifications/${id}/read`);
  }

  async markAllAsRead() {
    return this.patch('/notifications/mark-all-read');
  }

  async deleteNotification(id: string) {
    return this.delete(`/notifications/${id}`);
  }

  async getUnreadCount() {
    return this.get('/notifications/unread-count');
  }

  async sendSystemNotification(data: any) {
    return this.post('/notifications/system', data);
  }

  async getNotificationStats() {
    return this.get('/notifications/stats');
  }
}

export const apiService = new ApiService();