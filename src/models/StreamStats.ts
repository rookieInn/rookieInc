import mongoose, { Document, Schema } from 'mongoose';
import { StreamStats as IStreamStats } from '@/types';

export interface StreamStatsDocument extends IStreamStats, Document {}

const streamStatsSchema = new Schema<StreamStatsDocument>({
  roomId: {
    type: Schema.Types.ObjectId,
    ref: 'LiveRoom',
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now,
    required: true
  },
  viewerCount: {
    type: Number,
    required: true,
    min: 0
  },
  likeCount: {
    type: Number,
    default: 0,
    min: 0
  },
  commentCount: {
    type: Number,
    default: 0,
    min: 0
  },
  shareCount: {
    type: Number,
    default: 0,
    min: 0
  },
  duration: {
    type: Number,
    required: true,
    min: 0
  },
  bitrate: {
    type: Number,
    required: true,
    min: 0
  },
  resolution: {
    type: String,
    required: true,
    enum: ['720p', '1080p', '1440p', '4K']
  },
  fps: {
    type: Number,
    required: true,
    min: 1,
    max: 120
  }
}, {
  timestamps: false
});

// 索引
streamStatsSchema.index({ roomId: 1, timestamp: 1 });
streamStatsSchema.index({ timestamp: -1 });

// TTL索引，自动删除30天前的统计数据
streamStatsSchema.index({ timestamp: 1 }, { expireAfterSeconds: 2592000 });

export const StreamStats = mongoose.model<StreamStatsDocument>('StreamStats', streamStatsSchema);