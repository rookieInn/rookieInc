import mongoose, { Document, Schema } from 'mongoose';
import { LiveRoom as ILiveRoom, LiveStatus } from '@/types';

export interface LiveRoomDocument extends ILiveRoom, Document {}

const liveRoomSchema = new Schema<LiveRoomDocument>({
  title: {
    type: String,
    required: true,
    trim: true,
    maxlength: 100
  },
  description: {
    type: String,
    required: true,
    trim: true,
    maxlength: 1000
  },
  streamerId: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  category: {
    type: String,
    required: true,
    trim: true
  },
  tags: [{
    type: String,
    trim: true,
    maxlength: 20
  }],
  thumbnail: {
    type: String,
    default: null
  },
  status: {
    type: String,
    enum: Object.values(LiveStatus),
    default: LiveStatus.SCHEDULED
  },
  viewerCount: {
    type: Number,
    default: 0,
    min: 0
  },
  maxViewers: {
    type: Number,
    default: 0,
    min: 0
  },
  startTime: {
    type: Date,
    default: null
  },
  endTime: {
    type: Date,
    default: null
  },
  duration: {
    type: Number,
    default: 0,
    min: 0
  },
  streamKey: {
    type: String,
    required: true,
    unique: true
  },
  rtmpUrl: {
    type: String,
    required: true
  },
  hlsUrl: {
    type: String,
    required: true
  },
  isPublic: {
    type: Boolean,
    default: true
  },
  isFeatured: {
    type: Boolean,
    default: false
  }
}, {
  timestamps: true
});

// 虚拟字段：streamer
liveRoomSchema.virtual('streamer', {
  ref: 'User',
  localField: 'streamerId',
  foreignField: '_id',
  justOne: true
});

// 确保虚拟字段包含在JSON输出中
liveRoomSchema.set('toJSON', { virtuals: true });

// 生成流密钥的方法
liveRoomSchema.methods.generateStreamKey = function() {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2);
  this.streamKey = `stream_${timestamp}_${random}`;
  return this.streamKey;
};

// 开始直播
liveRoomSchema.methods.startLive = function() {
  this.status = LiveStatus.LIVE;
  this.startTime = new Date();
  return this.save();
};

// 结束直播
liveRoomSchema.methods.endLive = function() {
  this.status = LiveStatus.ENDED;
  this.endTime = new Date();
  if (this.startTime) {
    this.duration = Math.floor((this.endTime.getTime() - this.startTime.getTime()) / 1000);
  }
  return this.save();
};

// 更新观众数量
liveRoomSchema.methods.updateViewerCount = function(count: number) {
  this.viewerCount = count;
  if (count > this.maxViewers) {
    this.maxViewers = count;
  }
  return this.save();
};

// 索引
liveRoomSchema.index({ streamerId: 1 });
liveRoomSchema.index({ status: 1 });
liveRoomSchema.index({ category: 1 });
liveRoomSchema.index({ isPublic: 1 });
liveRoomSchema.index({ isFeatured: 1 });
liveRoomSchema.index({ createdAt: -1 });
liveRoomSchema.index({ viewerCount: -1 });

export const LiveRoom = mongoose.model<LiveRoomDocument>('LiveRoom', liveRoomSchema);