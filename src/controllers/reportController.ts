import { Request, Response } from 'express';
import { ReportService } from '@/services/reportService';
import { asyncHandler } from '@/middleware/errorHandler';
import { PaginationQuery } from '@/types';

export class ReportController {
  // 创建举报
  static createReport = asyncHandler(async (req: Request, res: Response) => {
    const reporterId = (req as any).user._id;
    const data = req.body;
    
    const result = await ReportService.createReport(reporterId, data);
    
    res.status(result.success ? 201 : 400).json(result);
  });

  // 获取举报列表
  static getReports = asyncHandler(async (req: Request, res: Response) => {
    const query: PaginationQuery & any = req.query;
    
    const result = await ReportService.getReports(query);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取单个举报
  static getReportById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const result = await ReportService.getReportById(id);
    
    res.status(result.success ? 200 : 404).json(result);
  });

  // 分配审核员
  static assignModerator = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const { moderatorId } = req.body;
    
    const result = await ReportService.assignModerator(id, moderatorId);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 解决举报
  static resolveReport = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const moderatorId = (req as any).user._id;
    const { action } = req.body;
    
    const result = await ReportService.resolveReport(id, moderatorId, action);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 拒绝举报
  static rejectReport = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const moderatorId = (req as any).user._id;
    const { reason } = req.body;
    
    const result = await ReportService.rejectReport(id, moderatorId, reason);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取举报统计信息
  static getReportStats = asyncHandler(async (req: Request, res: Response) => {
    const result = await ReportService.getReportStats();
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取举报原因分布
  static getReportReasonDistribution = asyncHandler(async (req: Request, res: Response) => {
    const result = await ReportService.getReportReasonDistribution();
    
    res.status(result.success ? 200 : 400).json(result);
  });
}