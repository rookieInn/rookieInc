export interface User {
  _id: string;
  username: string;
  email: string;
  role: UserRole;
  avatar?: string;
  isActive: boolean;
  lastLogin?: string;
  createdAt: string;
  updatedAt: string;
}

export enum UserRole {
  SUPER_ADMIN = 'super_admin',
  ADMIN = 'admin',
  MODERATOR = 'moderator',
  STREAMER = 'streamer',
  VIEWER = 'viewer'
}

export interface LiveRoom {
  _id: string;
  title: string;
  description: string;
  streamerId: string;
  streamer: User;
  category: string;
  tags: string[];
  thumbnail?: string;
  status: LiveStatus;
  viewerCount: number;
  maxViewers: number;
  startTime?: string;
  endTime?: string;
  duration: number;
  streamKey: string;
  rtmpUrl: string;
  hlsUrl: string;
  isPublic: boolean;
  isFeatured: boolean;
  createdAt: string;
  updatedAt: string;
}

export enum LiveStatus {
  SCHEDULED = 'scheduled',
  LIVE = 'live',
  ENDED = 'ended',
  BANNED = 'banned'
}

export interface Report {
  _id: string;
  reporterId: string;
  reporter: User;
  targetType: ReportTargetType;
  targetId: string;
  reason: ReportReason;
  description: string;
  status: ReportStatus;
  moderatorId?: string;
  moderator?: User;
  createdAt: string;
  updatedAt: string;
}

export enum ReportTargetType {
  ROOM = 'room',
  USER = 'user',
  COMMENT = 'comment'
}

export enum ReportReason {
  SPAM = 'spam',
  HARASSMENT = 'harassment',
  INAPPROPRIATE_CONTENT = 'inappropriate_content',
  COPYRIGHT_VIOLATION = 'copyright_violation',
  VIOLENCE = 'violence',
  OTHER = 'other'
}

export enum ReportStatus {
  PENDING = 'pending',
  REVIEWING = 'reviewing',
  RESOLVED = 'resolved',
  REJECTED = 'rejected'
}

export interface Notification {
  _id: string;
  userId: string;
  title: string;
  message: string;
  type: NotificationType;
  isRead: boolean;
  data?: any;
  createdAt: string;
}

export enum NotificationType {
  SYSTEM = 'system',
  ROOM_APPROVED = 'room_approved',
  ROOM_REJECTED = 'room_rejected',
  ROOM_BANNED = 'room_banned',
  REPORT_RECEIVED = 'report_received',
  REPORT_RESOLVED = 'report_resolved',
  USER_BANNED = 'user_banned',
  USER_UNBANNED = 'user_unbanned'
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  pagination?: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

export interface PaginationQuery {
  page?: number;
  limit?: number;
  sort?: string;
  order?: 'asc' | 'desc';
  search?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  role?: UserRole;
}

export interface CreateRoomRequest {
  title: string;
  description: string;
  category: string;
  tags: string[];
  isPublic: boolean;
  scheduledTime?: string;
}

export interface UpdateRoomRequest {
  title?: string;
  description?: string;
  category?: string;
  tags?: string[];
  isPublic?: boolean;
  isFeatured?: boolean;
}

export interface CreateReportRequest {
  targetType: ReportTargetType;
  targetId: string;
  reason: ReportReason;
  description: string;
}

export interface DashboardStats {
  totalUsers: number;
  activeUsers: number;
  totalRooms: number;
  liveRooms: number;
  totalReports: number;
  pendingReports: number;
  totalNotifications: number;
  unreadNotifications: number;
}

export interface MenuItem {
  key: string;
  label: string;
  icon: React.ReactNode;
  path?: string;
  children?: MenuItem[];
  roles?: UserRole[];
}