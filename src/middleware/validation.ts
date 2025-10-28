import { Request, Response, NextFunction } from 'express';
import Joi from 'joi';
import { ApiResponse } from '@/types';

// 验证中间件工厂函数
export const validate = (schema: Joi.ObjectSchema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const { error, value } = schema.validate(req.body, {
      abortEarly: false,
      stripUnknown: true
    });

    if (error) {
      const errorMessages = error.details.map(detail => detail.message);
      return res.status(400).json({
        success: false,
        message: '验证失败',
        error: errorMessages
      } as ApiResponse);
    }

    req.body = value;
    next();
  };
};

// 查询参数验证中间件
export const validateQuery = (schema: Joi.ObjectSchema) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const { error, value } = schema.validate(req.query, {
      abortEarly: false,
      stripUnknown: true
    });

    if (error) {
      const errorMessages = error.details.map(detail => detail.message);
      return res.status(400).json({
        success: false,
        message: '查询参数验证失败',
        error: errorMessages
      } as ApiResponse);
    }

    req.query = value;
    next();
  };
};

// 常用验证规则
export const commonSchemas = {
  // 分页查询
  pagination: Joi.object({
    page: Joi.number().integer().min(1).default(1),
    limit: Joi.number().integer().min(1).max(100).default(10),
    sort: Joi.string().default('createdAt'),
    order: Joi.string().valid('asc', 'desc').default('desc'),
    search: Joi.string().max(100).optional()
  }),

  // 用户注册
  register: Joi.object({
    username: Joi.string().alphanum().min(3).max(30).required(),
    email: Joi.string().email().required(),
    password: Joi.string().min(6).max(128).required(),
    role: Joi.string().valid('viewer', 'streamer').optional()
  }),

  // 用户登录
  login: Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().required()
  }),

  // 创建直播房间
  createRoom: Joi.object({
    title: Joi.string().min(1).max(100).required(),
    description: Joi.string().min(1).max(1000).required(),
    category: Joi.string().min(1).max(50).required(),
    tags: Joi.array().items(Joi.string().max(20)).max(10).default([]),
    isPublic: Joi.boolean().default(true),
    scheduledTime: Joi.date().greater('now').optional()
  }),

  // 更新直播房间
  updateRoom: Joi.object({
    title: Joi.string().min(1).max(100).optional(),
    description: Joi.string().min(1).max(1000).optional(),
    category: Joi.string().min(1).max(50).optional(),
    tags: Joi.array().items(Joi.string().max(20)).max(10).optional(),
    isPublic: Joi.boolean().optional(),
    isFeatured: Joi.boolean().optional()
  }),

  // 创建举报
  createReport: Joi.object({
    targetType: Joi.string().valid('room', 'user', 'comment').required(),
    targetId: Joi.string().required(),
    reason: Joi.string().valid(
      'spam', 'harassment', 'inappropriate_content', 
      'copyright_violation', 'violence', 'other'
    ).required(),
    description: Joi.string().min(1).max(500).required()
  }),

  // 更新用户
  updateUser: Joi.object({
    username: Joi.string().alphanum().min(3).max(30).optional(),
    email: Joi.string().email().optional(),
    role: Joi.string().valid('super_admin', 'admin', 'moderator', 'streamer', 'viewer').optional(),
    isActive: Joi.boolean().optional()
  }),

  // 更新密码
  updatePassword: Joi.object({
    currentPassword: Joi.string().required(),
    newPassword: Joi.string().min(6).max(128).required()
  }),

  // 文件上传
  fileUpload: Joi.object({
    type: Joi.string().valid('avatar', 'thumbnail', 'document').required(),
    maxSize: Joi.number().max(10485760).optional() // 10MB
  })
};