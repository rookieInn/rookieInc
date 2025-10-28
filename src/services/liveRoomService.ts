import { LiveRoom, LiveRoomDocument } from '@/models/LiveRoom';
import { StreamStats, StreamStatsDocument } from '@/models/StreamStats';
import { User } from '@/models/User';
import { 
  LiveStatus, 
  CreateRoomRequest, 
  UpdateRoomRequest, 
  PaginationQuery,
  ApiResponse 
} from '@/types';

export class LiveRoomService {
  // 创建直播房间
  static async createRoom(
    streamerId: string, 
    data: CreateRoomRequest
  ): Promise<ApiResponse<LiveRoomDocument>> {
    try {
      // 检查主播是否存在
      const streamer = await User.findById(streamerId);
      if (!streamer) {
        return {
          success: false,
          message: '主播不存在'
        };
      }

      // 检查主播是否已有进行中的直播
      const existingLiveRoom = await LiveRoom.findOne({
        streamerId,
        status: { $in: [LiveStatus.LIVE, LiveStatus.SCHEDULED] }
      });

      if (existingLiveRoom) {
        return {
          success: false,
          message: '您已有进行中的直播或预约直播'
        };
      }

      // 生成流密钥和URL
      const streamKey = `stream_${Date.now()}_${Math.random().toString(36).substring(2)}`;
      const rtmpUrl = `${process.env.RTMP_SERVER_URL}/${streamKey}`;
      const hlsUrl = `${process.env.HLS_SERVER_URL}/${streamKey}.m3u8`;

      // 创建直播房间
      const room = new LiveRoom({
        ...data,
        streamerId,
        streamKey,
        rtmpUrl,
        hlsUrl,
        status: data.scheduledTime ? LiveStatus.SCHEDULED : LiveStatus.LIVE
      });

      await room.save();
      await room.populate('streamer', 'username email avatar');

      return {
        success: true,
        message: '直播房间创建成功',
        data: room
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取直播房间列表
  static async getRooms(
    query: PaginationQuery & { 
      status?: LiveStatus; 
      category?: string; 
      streamerId?: string;
      isPublic?: boolean;
      isFeatured?: boolean;
    }
  ): Promise<ApiResponse<LiveRoomDocument[]>> {
    try {
      const {
        page = 1,
        limit = 10,
        sort = 'createdAt',
        order = 'desc',
        search,
        status,
        category,
        streamerId,
        isPublic,
        isFeatured
      } = query;

      // 构建查询条件
      const filter: any = {};
      
      if (status) filter.status = status;
      if (category) filter.category = category;
      if (streamerId) filter.streamerId = streamerId;
      if (isPublic !== undefined) filter.isPublic = isPublic;
      if (isFeatured !== undefined) filter.isFeatured = isFeatured;
      
      if (search) {
        filter.$or = [
          { title: { $regex: search, $options: 'i' } },
          { description: { $regex: search, $options: 'i' } },
          { tags: { $in: [new RegExp(search, 'i')] } }
        ];
      }

      // 计算分页
      const skip = (page - 1) * limit;
      const sortOrder = order === 'asc' ? 1 : -1;

      // 查询数据
      const [rooms, total] = await Promise.all([
        LiveRoom.find(filter)
          .populate('streamer', 'username email avatar')
          .sort({ [sort]: sortOrder })
          .skip(skip)
          .limit(limit),
        LiveRoom.countDocuments(filter)
      ]);

      return {
        success: true,
        message: '获取直播房间列表成功',
        data: rooms,
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

  // 获取单个直播房间
  static async getRoomById(roomId: string): Promise<ApiResponse<LiveRoomDocument>> {
    try {
      const room = await LiveRoom.findById(roomId)
        .populate('streamer', 'username email avatar');

      if (!room) {
        return {
          success: false,
          message: '直播房间不存在'
        };
      }

      return {
        success: true,
        message: '获取直播房间成功',
        data: room
      };
    } catch (error) {
      throw error;
    }
  }

  // 更新直播房间
  static async updateRoom(
    roomId: string, 
    data: UpdateRoomRequest
  ): Promise<ApiResponse<LiveRoomDocument>> {
    try {
      const room = await LiveRoom.findByIdAndUpdate(
        roomId,
        data,
        { new: true, runValidators: true }
      ).populate('streamer', 'username email avatar');

      if (!room) {
        return {
          success: false,
          message: '直播房间不存在'
        };
      }

      return {
        success: true,
        message: '直播房间更新成功',
        data: room
      };
    } catch (error) {
      throw error;
    }
  }

  // 删除直播房间
  static async deleteRoom(roomId: string): Promise<ApiResponse> {
    try {
      const room = await LiveRoom.findById(roomId);
      if (!room) {
        return {
          success: false,
          message: '直播房间不存在'
        };
      }

      if (room.status === LiveStatus.LIVE) {
        return {
          success: false,
          message: '无法删除正在直播的房间'
        };
      }

      await LiveRoom.findByIdAndDelete(roomId);

      return {
        success: true,
        message: '直播房间删除成功'
      };
    } catch (error) {
      throw error;
    }
  }

  // 开始直播
  static async startLive(roomId: string): Promise<ApiResponse<LiveRoomDocument>> {
    try {
      const room = await LiveRoom.findById(roomId);
      if (!room) {
        return {
          success: false,
          message: '直播房间不存在'
        };
      }

      if (room.status !== LiveStatus.SCHEDULED) {
        return {
          success: false,
          message: '只有预约的直播才能开始'
        };
      }

      await room.startLive();
      await room.populate('streamer', 'username email avatar');

      return {
        success: true,
        message: '直播开始成功',
        data: room
      };
    } catch (error) {
      throw error;
    }
  }

  // 结束直播
  static async endLive(roomId: string): Promise<ApiResponse<LiveRoomDocument>> {
    try {
      const room = await LiveRoom.findById(roomId);
      if (!room) {
        return {
          success: false,
          message: '直播房间不存在'
        };
      }

      if (room.status !== LiveStatus.LIVE) {
        return {
          success: false,
          message: '只有正在直播的房间才能结束'
        };
      }

      await room.endLive();
      await room.populate('streamer', 'username email avatar');

      return {
        success: true,
        message: '直播结束成功',
        data: room
      };
    } catch (error) {
      throw error;
    }
  }

  // 更新观众数量
  static async updateViewerCount(roomId: string, count: number): Promise<ApiResponse> {
    try {
      const room = await LiveRoom.findById(roomId);
      if (!room) {
        return {
          success: false,
          message: '直播房间不存在'
        };
      }

      await room.updateViewerCount(count);

      return {
        success: true,
        message: '观众数量更新成功'
      };
    } catch (error) {
      throw error;
    }
  }

  // 记录直播统计数据
  static async recordStats(
    roomId: string, 
    stats: Partial<StreamStatsDocument>
  ): Promise<ApiResponse<StreamStatsDocument>> {
    try {
      const streamStats = new StreamStats({
        roomId,
        ...stats
      });

      await streamStats.save();

      return {
        success: true,
        message: '统计数据记录成功',
        data: streamStats
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取直播统计数据
  static async getRoomStats(
    roomId: string,
    startTime?: Date,
    endTime?: Date
  ): Promise<ApiResponse<StreamStatsDocument[]>> {
    try {
      const filter: any = { roomId };
      
      if (startTime && endTime) {
        filter.timestamp = {
          $gte: startTime,
          $lte: endTime
        };
      }

      const stats = await StreamStats.find(filter)
        .sort({ timestamp: 1 });

      return {
        success: true,
        message: '获取统计数据成功',
        data: stats
      };
    } catch (error) {
      throw error;
    }
  }

  // 获取热门直播
  static async getFeaturedRooms(limit: number = 10): Promise<ApiResponse<LiveRoomDocument[]>> {
    try {
      const rooms = await LiveRoom.find({
        status: LiveStatus.LIVE,
        isPublic: true
      })
        .populate('streamer', 'username email avatar')
        .sort({ viewerCount: -1, createdAt: -1 })
        .limit(limit);

      return {
        success: true,
        message: '获取热门直播成功',
        data: rooms
      };
    } catch (error) {
      throw error;
    }
  }
}