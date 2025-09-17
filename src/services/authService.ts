import jwt from 'jsonwebtoken';
import { User, UserDocument } from '@/models/User';
import { UserRole, LoginRequest, RegisterRequest, JWTPayload } from '@/types';
import { ApiResponse } from '@/types';

export class AuthService {
  // 生成JWT令牌
  private static generateToken(payload: JWTPayload): string {
    return jwt.sign(payload, process.env.JWT_SECRET!, {
      expiresIn: process.env.JWT_EXPIRES_IN || '7d'
    });
  }

  // 用户注册
  static async register(data: RegisterRequest): Promise<ApiResponse<{ user: UserDocument; token: string }>> {
    try {
      // 检查邮箱是否已存在
      const existingUser = await User.findOne({ email: data.email });
      if (existingUser) {
        return {
          success: false,
          message: '邮箱已被注册'
        };
      }

      // 检查用户名是否已存在
      const existingUsername = await User.findOne({ username: data.username });
      if (existingUsername) {
        return {
          success: false,
          message: '用户名已被使用'
        };
      }

      // 创建新用户
      const user = new User({
        username: data.username,
        email: data.email,
        password: data.password,
        role: data.role || UserRole.VIEWER
      });

      await user.save();

      // 生成令牌
      const token = this.generateToken({
        userId: user._id.toString(),
        email: user.email,
        role: user.role
      });

      return {
        success: true,
        message: '注册成功',
        data: { user, token }
      };
    } catch (error) {
      throw error;
    }
  }

  // 用户登录
  static async login(data: LoginRequest): Promise<ApiResponse<{ user: UserDocument; token: string }>> {
    try {
      // 查找用户
      const user = await User.findOne({ email: data.email });
      if (!user) {
        return {
          success: false,
          message: '邮箱或密码错误'
        };
      }

      // 检查账户状态
      if (!user.isActive) {
        return {
          success: false,
          message: '账户已被禁用'
        };
      }

      // 验证密码
      const isPasswordValid = await user.comparePassword(data.password);
      if (!isPasswordValid) {
        return {
          success: false,
          message: '邮箱或密码错误'
        };
      }

      // 更新最后登录时间
      await user.updateLastLogin();

      // 生成令牌
      const token = this.generateToken({
        userId: user._id.toString(),
        email: user.email,
        role: user.role
      });

      return {
        success: true,
        message: '登录成功',
        data: { user, token }
      };
    } catch (error) {
      throw error;
    }
  }

  // 刷新令牌
  static async refreshToken(userId: string): Promise<ApiResponse<{ token: string }>> {
    try {
      const user = await User.findById(userId);
      if (!user || !user.isActive) {
        return {
          success: false,
          message: '用户不存在或已被禁用'
        };
      }

      const token = this.generateToken({
        userId: user._id.toString(),
        email: user.email,
        role: user.role
      });

      return {
        success: true,
        message: '令牌刷新成功',
        data: { token }
      };
    } catch (error) {
      throw error;
    }
  }

  // 修改密码
  static async changePassword(
    userId: string, 
    currentPassword: string, 
    newPassword: string
  ): Promise<ApiResponse> {
    try {
      const user = await User.findById(userId);
      if (!user) {
        return {
          success: false,
          message: '用户不存在'
        };
      }

      // 验证当前密码
      const isCurrentPasswordValid = await user.comparePassword(currentPassword);
      if (!isCurrentPasswordValid) {
        return {
          success: false,
          message: '当前密码错误'
        };
      }

      // 更新密码
      user.password = newPassword;
      await user.save();

      return {
        success: true,
        message: '密码修改成功'
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取用户信息
  static async getUserProfile(userId: string): Promise<ApiResponse<UserDocument>> {
    try {
      const user = await User.findById(userId);
      if (!user) {
        return {
          success: false,
          message: '用户不存在'
        };
      }

      return {
        success: true,
        message: '获取用户信息成功',
        data: user
      };
    } catch (error) {
      throw error;
    }
  }

  // 更新用户信息
  static async updateUserProfile(
    userId: string, 
    updateData: Partial<Pick<UserDocument, 'username' | 'email' | 'avatar'>>
  ): Promise<ApiResponse<UserDocument>> {
    try {
      const user = await User.findByIdAndUpdate(
        userId,
        updateData,
        { new: true, runValidators: true }
      );

      if (!user) {
        return {
          success: false,
          message: '用户不存在'
        };
      }

      return {
        success: true,
        message: '用户信息更新成功',
        data: user
      };
    } catch (error) {
      throw error;
    }
  }
}