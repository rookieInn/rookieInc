import { Request, Response } from 'express';
import { UserService } from '@/services/userService';
import { asyncHandler } from '@/middleware/errorHandler';
import { PaginationQuery } from '@/types';

export class UserController {
  // 获取用户列表
  static getUsers = asyncHandler(async (req: Request, res: Response) => {
    const query: PaginationQuery & any = req.query;
    
    const result = await UserService.getUsers(query);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取单个用户
  static getUserById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const result = await UserService.getUserById(id);
    
    res.status(result.success ? 200 : 404).json(result);
  });

  // 更新用户信息
  static updateUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const updateData = req.body;
    
    const result = await UserService.updateUser(id, updateData);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 删除用户
  static deleteUser = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const result = await UserService.deleteUser(id);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 禁用/启用用户
  static toggleUserStatus = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const result = await UserService.toggleUserStatus(id);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取用户统计信息
  static getUserStats = asyncHandler(async (req: Request, res: Response) => {
    const result = await UserService.getUserStats();
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取用户角色分布
  static getUserRoleDistribution = asyncHandler(async (req: Request, res: Response) => {
    const result = await UserService.getUserRoleDistribution();
    
    res.status(result.success ? 200 : 400).json(result);
  });
}