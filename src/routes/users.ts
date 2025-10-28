import { Router } from 'express';
import { UserController } from '@/controllers/userController';
import { authenticate, requireAdmin, requireModerator } from '@/middleware/auth';
import { validate, validateQuery } from '@/middleware/validation';
import { commonSchemas } from '@/middleware/validation';

const router = Router();

// 所有路由都需要认证
router.use(authenticate);

// 获取用户列表（管理员和审核员）
router.get('/', 
  requireModerator,
  validateQuery(commonSchemas.pagination), 
  UserController.getUsers
);

// 获取用户统计信息（管理员）
router.get('/stats', 
  requireAdmin,
  UserController.getUserStats
);

// 获取用户角色分布（管理员）
router.get('/role-distribution', 
  requireAdmin,
  UserController.getUserRoleDistribution
);

// 获取单个用户
router.get('/:id', UserController.getUserById);

// 更新用户信息（管理员）
router.put('/:id', 
  requireAdmin,
  validate(commonSchemas.updateUser), 
  UserController.updateUser
);

// 删除用户（超级管理员）
router.delete('/:id', 
  requireAdmin,
  UserController.deleteUser
);

// 禁用/启用用户（管理员）
router.patch('/:id/toggle-status', 
  requireAdmin,
  UserController.toggleUserStatus
);

export default router;