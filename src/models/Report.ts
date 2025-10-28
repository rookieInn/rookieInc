import mongoose, { Document, Schema } from 'mongoose';
import { Report as IReport, ReportTargetType, ReportReason, ReportStatus } from '@/types';

export interface ReportDocument extends IReport, Document {}

const reportSchema = new Schema<ReportDocument>({
  reporterId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  targetType: {
    type: String,
    enum: Object.values(ReportTargetType),
    required: true
  },
  targetId: {
    type: String,
    required: true
  },
  reason: {
    type: String,
    enum: Object.values(ReportReason),
    required: true
  },
  description: {
    type: String,
    required: true,
    trim: true,
    maxlength: 500
  },
  status: {
    type: String,
    enum: Object.values(ReportStatus),
    default: ReportStatus.PENDING
  },
  moderatorId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    default: null
  }
}, {
  timestamps: true
});

// 虚拟字段：reporter
reportSchema.virtual('reporter', {
  ref: 'User',
  localField: 'reporterId',
  foreignField: '_id',
  justOne: true
});

// 虚拟字段：moderator
reportSchema.virtual('moderator', {
  ref: 'User',
  localField: 'moderatorId',
  foreignField: '_id',
  justOne: true
});

// 确保虚拟字段包含在JSON输出中
reportSchema.set('toJSON', { virtuals: true });

// 分配审核员
reportSchema.methods.assignModerator = function(moderatorId: string) {
  this.moderatorId = moderatorId;
  this.status = ReportStatus.REVIEWING;
  return this.save();
};

// 解决举报
reportSchema.methods.resolve = function() {
  this.status = ReportStatus.RESOLVED;
  return this.save();
};

// 拒绝举报
reportSchema.methods.reject = function() {
  this.status = ReportStatus.REJECTED;
  return this.save();
};

// 索引
reportSchema.index({ reporterId: 1 });
reportSchema.index({ targetType: 1, targetId: 1 });
reportSchema.index({ status: 1 });
reportSchema.index({ moderatorId: 1 });
reportSchema.index({ createdAt: -1 });

export const Report = mongoose.model<ReportDocument>('Report', reportSchema);