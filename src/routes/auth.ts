import { Router } from 'express';
import { AuthController } from '@/controllers/authController';
import { authenticate } from '@/middleware/auth';
import { validate } from '@/middleware/validation';
import { commonSchemas } from '@/middleware/validation';

const router = Router();

// 公开路由
router.post('/register', 
  validate(commonSchemas.register), 
  AuthController.register
);

router.post('/login', 
  validate(commonSchemas.login), 
  AuthController.login
);

// 需要认证的路由
router.use(authenticate);

router.post('/refresh-token', AuthController.refreshToken);
router.post('/change-password', 
  validate(commonSchemas.updatePassword), 
  AuthController.changePassword
);
router.get('/profile', AuthController.getProfile);
router.put('/profile', 
  validate(commonSchemas.updateUser), 
  AuthController.updateProfile
);
router.post('/logout', AuthController.logout);

export default router;