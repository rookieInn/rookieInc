import { Report, ReportDocument } from '@/models/Report';
import { User } from '@/models/User';
import { Notification } from '@/models/Notification';
import { 
  ReportTargetType, 
  ReportReason, 
  ReportStatus, 
  CreateReportRequest, 
  PaginationQuery, 
  ApiResponse,
  NotificationType 
} from '@/types';

export class ReportService {
  // 创建举报
  static async createReport(
    reporterId: string, 
    data: CreateReportRequest
  ): Promise<ApiResponse<ReportDocument>> {
    try {
      // 检查是否已经举报过相同目标
      const existingReport = await Report.findOne({
        reporterId,
        targetType: data.targetType,
        targetId: data.targetId,
        status: { $in: [ReportStatus.PENDING, ReportStatus.REVIEWING] }
      });

      if (existingReport) {
        return {
          success: false,
          message: '您已经举报过此内容'
        };
      }

      // 创建举报
      const report = new Report({
        reporterId,
        ...data
      });

      await report.save();
      await report.populate('reporter', 'username email');

      // 发送通知给管理员
      const admins = await User.find({
        role: { $in: ['super_admin', 'admin', 'moderator'] }
      });

      for (const admin of admins) {
        await Notification.create({
          userId: admin._id,
          title: '新举报通知',
          message: `收到新的举报：${data.reason}`,
          type: NotificationType.REPORT_RECEIVED,
          data: { reportId: report._id }
        });
      }

      return {
        success: true,
        message: '举报提交成功',
        data: report
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取举报列表
  static async getReports(
    query: PaginationQuery & {
      status?: ReportStatus;
      targetType?: ReportTargetType;
      reason?: ReportReason;
      moderatorId?: string;
    }
  ): Promise<ApiResponse<ReportDocument[]>> {
    try {
      const {
        page = 1,
        limit = 10,
        sort = 'createdAt',
        order = 'desc',
        status,
        targetType,
        reason,
        moderatorId
      } = query;

      // 构建查询条件
      const filter: any = {};
      
      if (status) filter.status = status;
      if (targetType) filter.targetType = targetType;
      if (reason) filter.reason = reason;
      if (moderatorId) filter.moderatorId = moderatorId;

      // 计算分页
      const skip = (page - 1) * limit;
      const sortOrder = order === 'asc' ? 1 : -1;

      // 查询数据
      const [reports, total] = await Promise.all([
        Report.find(filter)
          .populate('reporter', 'username email')
          .populate('moderator', 'username email')
          .sort({ [sort]: sortOrder })
          .skip(skip)
          .limit(limit),
        Report.countDocuments(filter)
      ]);

      return {
        success: true,
        message: '获取举报列表成功',
        data: reports,
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

  // 获取单个举报
  static async getReportById(reportId: string): Promise<ApiResponse<ReportDocument>> {
    try {
      const report = await Report.findById(reportId)
        .populate('reporter', 'username email')
        .populate('moderator', 'username email');

      if (!report) {
        return {
          success: false,
          message: '举报不存在'
        };
      }

      return {
        success: true,
        message: '获取举报信息成功',
        data: report
      };
    } catch (error) {
      throw error;
    }
  }

  // 分配审核员
  static async assignModerator(
    reportId: string, 
    moderatorId: string
  ): Promise<ApiResponse<ReportDocument>> {
    try {
      const report = await Report.findById(reportId);
      if (!report) {
        return {
          success: false,
          message: '举报不存在'
        };
      }

      if (report.status !== ReportStatus.PENDING) {
        return {
          success: false,
          message: '举报已被处理'
        };
      }

      await report.assignModerator(moderatorId);
      await report.populate('reporter', 'username email');
      await report.populate('moderator', 'username email');

      return {
        success: true,
        message: '审核员分配成功',
        data: report
      };
    } catch (error) {
      throw error;
    }
  }

  // 解决举报
  static async resolveReport(
    reportId: string, 
    moderatorId: string,
    action?: string
  ): Promise<ApiResponse<ReportDocument>> {
    try {
      const report = await Report.findById(reportId);
      if (!report) {
        return {
          success: false,
          message: '举报不存在'
        };
      }

      if (report.status === ReportStatus.RESOLVED) {
        return {
          success: false,
          message: '举报已解决'
        };
      }

      // 分配审核员（如果还没有）
      if (!report.moderatorId) {
        report.moderatorId = moderatorId;
      }

      await report.resolve();
      await report.populate('reporter', 'username email');
      await report.populate('moderator', 'username email');

      // 发送通知给举报者
      await Notification.create({
        userId: report.reporterId,
        title: '举报处理完成',
        message: '您的举报已处理完成',
        type: NotificationType.REPORT_RESOLVED,
        data: { reportId: report._id, action }
      });

      return {
        success: true,
        message: '举报解决成功',
        data: report
      };
    } catch (error) {
      throw error;
    }
  }

  // 拒绝举报
  static async rejectReport(
    reportId: string, 
    moderatorId: string,
    reason?: string
  ): Promise<ApiResponse<ReportDocument>> {
    try {
      const report = await Report.findById(reportId);
      if (!report) {
        return {
          success: false,
          message: '举报不存在'
        };
      }

      if (report.status === ReportStatus.REJECTED) {
        return {
          success: false,
          message: '举报已拒绝'
        };
      }

      // 分配审核员（如果还没有）
      if (!report.moderatorId) {
        report.moderatorId = moderatorId;
      }

      await report.reject();
      await report.populate('reporter', 'username email');
      await report.populate('moderator', 'username email');

      // 发送通知给举报者
      await Notification.create({
        userId: report.reporterId,
        title: '举报处理结果',
        message: reason || '您的举报经审核后未发现违规行为',
        type: NotificationType.REPORT_RESOLVED,
        data: { reportId: report._id, rejected: true, reason }
      });

      return {
        success: true,
        message: '举报拒绝成功',
        data: report
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取举报统计信息
  static async getReportStats(): Promise<ApiResponse<any>> {
    try {
      const [
        totalReports,
        pendingReports,
        reviewingReports,
        resolvedReports,
        rejectedReports,
        reportsToday,
        reportsThisWeek,
        reportsThisMonth
      ] = await Promise.all([
        Report.countDocuments(),
        Report.countDocuments({ status: ReportStatus.PENDING }),
        Report.countDocuments({ status: ReportStatus.REVIEWING }),
        Report.countDocuments({ status: ReportStatus.RESOLVED }),
        Report.countDocuments({ status: ReportStatus.REJECTED }),
        Report.countDocuments({
          createdAt: { $gte: new Date(new Date().setHours(0, 0, 0, 0)) }
        }),
        Report.countDocuments({
          createdAt: { $gte: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000) }
        }),
        Report.countDocuments({
          createdAt: { $gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000) }
        })
      ]);

      const stats = {
        totalReports,
        pendingReports,
        reviewingReports,
        resolvedReports,
        rejectedReports,
        reportsToday,
        reportsThisWeek,
        reportsThisMonth
      };

      return {
        success: true,
        message: '获取举报统计成功',
        data: stats
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取举报原因分布
  static async getReportReasonDistribution(): Promise<ApiResponse<any>> {
    try {
      const reasonStats = await Report.aggregate([
        {
          $group: {
            _id: '$reason',
            count: { $sum: 1 }
          }
        },
        {
          $project: {
            reason: '$_id',
            count: 1,
            _id: 0
          }
        }
      ]);

      return {
        success: true,
        message: '获取举报原因分布成功',
        data: reasonStats
      };
    } catch (error) {
      throw error;
    }
  }
}