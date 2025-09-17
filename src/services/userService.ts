import { User, UserDocument } from '@/models/User';
import { UserRole, PaginationQuery, ApiResponse } from '@/types';

export class UserService {
  // 获取用户列表
  static async getUsers(
    query: PaginationQuery & { 
      role?: UserRole; 
      isActive?: boolean;
      search?: string;
    }
  ): Promise<ApiResponse<UserDocument[]>> {
    try {
      const {
        page = 1,
        limit = 10,
        sort = 'createdAt',
        order = 'desc',
        search,
        role,
        isActive
      } = query;

      // 构建查询条件
      const filter: any = {};
      
      if (role) filter.role = role;
      if (isActive !== undefined) filter.isActive = isActive;
      
      if (search) {
        filter.$or = [
          { username: { $regex: search, $options: 'i' } },
          { email: { $regex: search, $options: 'i' } }
        ];
      }

      // 计算分页
      const skip = (page - 1) * limit;
      const sortOrder = order === 'asc' ? 1 : -1;

      // 查询数据
      const [users, total] = await Promise.all([
        User.find(filter)
          .select('-password')
          .sort({ [sort]: sortOrder })
          .skip(skip)
          .limit(limit),
        User.countDocuments(filter)
      ]);

      return {
        success: true,
        message: '获取用户列表成功',
        data: users,
        pagination: {
          page,
          limit,
          total,
          pages: Math.ceil(total / limit)
        }
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取单个用户
  static async getUserById(userId: string): Promise<ApiResponse<UserDocument>> {
    try {
      const user = await User.findById(userId).select('-password');
      
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
  static async updateUser(
    userId: string, 
    updateData: Partial<Pick<UserDocument, 'username' | 'email' | 'role' | 'isActive' | 'avatar'>>
  ): Promise<ApiResponse<UserDocument>> {
    try {
      const user = await User.findByIdAndUpdate(
        userId,
        updateData,
        { new: true, runValidators: true }
      ).select('-password');

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

  // 删除用户
  static async deleteUser(userId: string): Promise<ApiResponse> {
    try {
      const user = await User.findById(userId);
      if (!user) {
        return {
          success: false,
          message: '用户不存在'
        };
      }

      // 检查是否有进行中的直播
      const { LiveRoom } = await import('@/models/LiveRoom');
      const activeRoom = await LiveRoom.findOne({
        streamerId: userId,
        status: { $in: ['live', 'scheduled'] }
      });

      if (activeRoom) {
        return {
          success: false,
          message: '用户有进行中的直播，无法删除'
        };
      }

      await User.findByIdAndDelete(userId);

      return {
        success: true,
        message: '用户删除成功'
      };
    } catch (error) {
      throw error;
    }
  }

  // 禁用/启用用户
  static async toggleUserStatus(userId: string): Promise<ApiResponse<UserDocument>> {
    try {
      const user = await User.findById(userId);
      if (!user) {
        return {
          success: false,
          message: '用户不存在'
        };
      }

      user.isActive = !user.isActive;
      await user.save();

      return {
        success: true,
        message: `用户已${user.isActive ? '启用' : '禁用'}`,
        data: user
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取用户统计信息
  static async getUserStats(): Promise<ApiResponse<any>> {
    try {
      const [
        totalUsers,
        activeUsers,
        streamers,
        admins,
        newUsersToday,
        newUsersThisWeek,
        newUsersThisMonth
      ] = await Promise.all([
        User.countDocuments(),
        User.countDocuments({ isActive: true }),
        User.countDocuments({ role: UserRole.STREAMER }),
        User.countDocuments({ role: { $in: [UserRole.ADMIN, UserRole.SUPER_ADMIN] } }),
        User.countDocuments({
          createdAt: { $gte: new Date(new Date().setHours(0, 0, 0, 0)) }
        }),
        User.countDocuments({
          createdAt: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
        }),
        User.countDocuments({
          createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
        })
      ]);

      const stats = {
        totalUsers,
        activeUsers,
        inactiveUsers: totalUsers - activeUsers,
        streamers,
        admins,
        newUsersToday,
        newUsersThisWeek,
        newUsersThisMonth
      };

      return {
        success: true,
        message: '获取用户统计成功',
        data: stats
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取用户角色分布
  static async getUserRoleDistribution(): Promise<ApiResponse<any>> {
    try {
      const roleStats = await User.aggregate([
        {
          $group: {
            _id: '$role',
            count: { $sum: 1 }
          }
        },
        {
          $project: {
            role: '$_id',
            count: 1,
            _id: 0
          }
        }
      ]);

      return {
        success: true,
        message: '获取用户角色分布成功',
        data: roleStats
      };
    } catch (error) {
      throw error;
    }
  }
}