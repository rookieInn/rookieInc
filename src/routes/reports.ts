import { Router } from 'express';
import { ReportController } from '@/controllers/reportController';
import { authenticate, requireModerator } from '@/middleware/auth';
import { validate, validateQuery } from '@/middleware/validation';
import { commonSchemas } from '@/middleware/validation';

const router = Router();

// 创建举报（需要认证）
router.post('/', 
  authenticate,
  validate(commonSchemas.createReport), 
  ReportController.createReport
);

// 获取举报列表（审核员）
router.get('/', 
  authenticate,
  requireModerator,
  validateQuery(commonSchemas.pagination), 
  ReportController.getReports
);

// 获取举报统计信息（审核员）
router.get('/stats', 
  authenticate,
  requireModerator,
  ReportController.getReportStats
);

// 获取举报原因分布（审核员）
router.get('/reason-distribution', 
  authenticate,
  requireModerator,
  ReportController.getReportReasonDistribution
);

// 获取单个举报（审核员）
router.get('/:id', 
  authenticate,
  requireModerator,
  ReportController.getReportById
);

// 分配审核员（审核员）
router.post('/:id/assign', 
  authenticate,
  requireModerator,
  ReportController.assignModerator
);

// 解决举报（审核员）
router.post('/:id/resolve', 
  authenticate,
  requireModerator,
  ReportController.resolveReport
);

// 拒绝举报（审核员）
router.post('/:id/reject', 
  authenticate,
  requireModerator,
  ReportController.rejectReport
);

export default router;