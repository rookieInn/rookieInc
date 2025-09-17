import { Router } from 'express';
import { LiveRoomController } from '@/controllers/liveRoomController';
import { authenticate, requireStreamer, requireOwnerOrAdmin } from '@/middleware/auth';
import { validate, validateQuery } from '@/middleware/validation';
import { commonSchemas } from '@/middleware/validation';

const router = Router();

// 公开路由
router.get('/', 
  validateQuery(commonSchemas.pagination), 
  LiveRoomController.getRooms
);

router.get('/featured', LiveRoomController.getFeaturedRooms);
router.get('/:id', LiveRoomController.getRoomById);

// 需要认证的路由
router.use(authenticate);

// 主播相关路由
router.post('/', 
  requireStreamer,
  validate(commonSchemas.createRoom), 
  LiveRoomController.createRoom
);

router.put('/:id', 
  requireOwnerOrAdmin('streamerId'),
  validate(commonSchemas.updateRoom), 
  LiveRoomController.updateRoom
);

router.delete('/:id', 
  requireOwnerOrAdmin('streamerId'),
  LiveRoomController.deleteRoom
);

router.post('/:id/start', 
  requireOwnerOrAdmin('streamerId'),
  LiveRoomController.startLive
);

router.post('/:id/end', 
  requireOwnerOrAdmin('streamerId'),
  LiveRoomController.endLive
);

router.put('/:id/viewer-count', 
  requireOwnerOrAdmin('streamerId'),
  LiveRoomController.updateViewerCount
);

router.post('/:id/stats', 
  requireOwnerOrAdmin('streamerId'),
  LiveRoomController.recordStats
);

router.get('/:id/stats', 
  requireOwnerOrAdmin('streamerId'),
  LiveRoomController.getRoomStats
);

export default router;