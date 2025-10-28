import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { User, UserDocument } from '@/models/User';
import { UserRole } from '@/types';
import { ApiResponse } from '@/types';

interface AuthRequest extends Request {
  user?: UserDocument;
}

export interface JWTPayload {
  userId: string;
  email: string;
  role: UserRole;
}

// JWT认证中间件
export const authenticate = async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const token = req.header('Authorization')?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        success: false,
        message: '访问被拒绝，未提供认证令牌'
      } as ApiResponse);
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload;
    const user = await User.findById(decoded.userId).select('-password');
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: '无效的认证令牌'
      } as ApiResponse);
    }

    if (!user.isActive) {
      return res.status(401).json({
        success: false,
        message: '账户已被禁用'
      } as ApiResponse);
    }

    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({
      success: false,
      message: '无效的认证令牌'
    } as ApiResponse);
  }
};

// 角色权限中间件
export const authorize = (...roles: UserRole[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证的用户'
      } as ApiResponse);
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({
        success: false,
        message: '权限不足'
      } as ApiResponse);
    }

    next();
  };
};

// 超级管理员权限
export const requireSuperAdmin = authorize(UserRole.SUPER_ADMIN);

// 管理员权限（包括超级管理员）
export const requireAdmin = authorize(UserRole.SUPER_ADMIN, UserRole.ADMIN);

// 审核员权限（包括管理员）
export const requireModerator = authorize(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR);

// 主播权限
export const requireStreamer = authorize(UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR, UserRole.STREAMER);

// 资源所有者或管理员权限
export const requireOwnerOrAdmin = (resourceUserIdField: string = 'userId') => {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        message: '未认证的用户'
      } as ApiResponse);
    }

    const isAdmin = [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.MODERATOR].includes(req.user.role);
    const isOwner = req.user._id.toString() === req.params[resourceUserIdField];

    if (!isAdmin && !isOwner) {
      return res.status(403).json({
        success: false,
        message: '权限不足'
      } as ApiResponse);
    }

    next();
  };
};