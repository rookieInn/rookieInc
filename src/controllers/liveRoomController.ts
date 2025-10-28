import { Request, Response } from 'express';
import { LiveRoomService } from '@/services/liveRoomService';
import { asyncHandler } from '@/middleware/errorHandler';
import { CreateRoomRequest, UpdateRoomRequest, PaginationQuery } from '@/types';

export class LiveRoomController {
  // 创建直播房间
  static createRoom = asyncHandler(async (req: Request, res: Response) => {
    const streamerId = (req as any).user._id;
    const data: CreateRoomRequest = req.body;
    
    const result = await LiveRoomService.createRoom(streamerId, data);
    
    res.status(result.success ? 201 : 400).json(result);
  });

  // 获取直播房间列表
  static getRooms = asyncHandler(async (req: Request, res: Response) => {
    const query: PaginationQuery & any = req.query;
    
    const result = await LiveRoomService.getRooms(query);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取单个直播房间
  static getRoomById = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const result = await LiveRoomService.getRoomById(id);
    
    res.status(result.success ? 200 : 404).json(result);
  });

  // 更新直播房间
  static updateRoom = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const data: UpdateRoomRequest = req.body;
    
    const result = await LiveRoomService.updateRoom(id, data);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 删除直播房间
  static deleteRoom = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const result = await LiveRoomService.deleteRoom(id);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 开始直播
  static startLive = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const result = await LiveRoomService.startLive(id);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 结束直播
  static endLive = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    
    const result = await LiveRoomService.endLive(id);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 更新观众数量
  static updateViewerCount = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const { count } = req.body;
    
    const result = await LiveRoomService.updateViewerCount(id, count);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 记录直播统计数据
  static recordStats = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const stats = req.body;
    
    const result = await LiveRoomService.recordStats(id, stats);
    
    res.status(result.success ? 201 : 400).json(result);
  });

  // 获取直播统计数据
  static getRoomStats = asyncHandler(async (req: Request, res: Response) => {
    const { id } = req.params;
    const { startTime, endTime } = req.query;
    
    const start = startTime ? new Date(startTime as string) : undefined;
    const end = endTime ? new Date(endTime as string) : undefined;
    
    const result = await LiveRoomService.getRoomStats(id, start, end);
    
    res.status(result.success ? 200 : 400).json(result);
  });

  // 获取热门直播
  static getFeaturedRooms = asyncHandler(async (req: Request, res: Response) => {
    const { limit } = req.query;
    const limitNum = limit ? parseInt(limit as string) : 10;
    
    const result = await LiveRoomService.getFeaturedRooms(limitNum);
    
    res.status(result.success ? 200 : 400).json(result);
  });
}