import { Request, Response } from 'express';
import { AuthService } from '@/services/authService';
import { asyncHandler } from '@/middleware/errorHandler';
import { LoginRequest, RegisterRequest, ApiResponse } from '@/types';

export class AuthController {
  // 用户注册
  static register = asyncHandler(async (req: Request, res: Response) => {
    const data: RegisterRequest = req.body;
    const result = await AuthService.register(data);
    
    res.status(result.success ? 201 : 400).json(result);
  });

  // 用户登录
  static login = asyncHandler(async (req: Request, res: Response) => {
    const data: LoginRequest = req.body;
    const result = await AuthService.login(data);
    
    res.status(result.success ? 200 : 401).json(result);
  });

  // 刷新令牌
  static refreshToken = asyncHandler(async (req: Request, res: Response) => {
    const userId = (req as any).user._id;
    const result = await AuthService.refreshToken(userId);
    
    res.status(result.success ? 200 : 401).json(result);
  });

  // 修改密码
  static changePassword = asyncHandler(async (req: Request, res: Response) => {
    const userId = (req as any).user._id;
    const { currentPassword, newPassword } = req.body;
    
    const result = await AuthService.changePassword(userId, currentPassword, newPassword);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取用户信息
  static getProfile = asyncHandler(async (req: Request, res: Response) => {
    const userId = (req as any).user._id;
    const result = await AuthService.getUserProfile(userId);
    
    res.status(result.success ? 200 : 404).json(result);
  });

  // 更新用户信息
  static updateProfile = asyncHandler(async (req: Request, res: Response) => {
    const userId = (req as any).user._id;
    const updateData = req.body;
    
    const result = await AuthService.updateUserProfile(userId, updateData);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 登出（客户端处理，这里只是返回成功）
  static logout = asyncHandler(async (req: Request, res: Response) => {
    res.json({
      success: true,
      message: '登出成功'
    } as ApiResponse);
  });
}