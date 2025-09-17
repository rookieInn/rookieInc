import mongoose from 'mongoose';
import { createClient } from 'redis';
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
    new winston.transports.File({ filename: 'logs/combined.log' }),
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// MongoDB连接
export const connectMongoDB = async (): Promise<void> => {
  try {
    const mongoUri = process.env.MONGODB_URI || 'mongodb://localhost:27017/live_streaming_admin';
    
    await mongoose.connect(mongoUri, {
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    });

    logger.info('MongoDB连接成功');
    
    // 监听连接事件
    mongoose.connection.on('error', (error) => {
      logger.error('MongoDB连接错误:', error);
    });

    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB连接断开');
    });

    mongoose.connection.on('reconnected', () => {
      logger.info('MongoDB重新连接成功');
    });

  } catch (error) {
    logger.error('MongoDB连接失败:', error);
    process.exit(1);
  }
};

// Redis连接
export const connectRedis = async () => {
  try {
    const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';
    const client = createClient({ url: redisUrl });

    client.on('error', (error) => {
      logger.error('Redis连接错误:', error);
    });

    client.on('connect', () => {
      logger.info('Redis连接成功');
    });

    await client.connect();
    return client;
  } catch (error) {
    logger.error('Redis连接失败:', error);
    throw error;
  }
};

// 关闭数据库连接
export const closeConnections = async (): Promise<void> => {
  try {
    await mongoose.connection.close();
    logger.info('MongoDB连接已关闭');
  } catch (error) {
    logger.error('关闭MongoDB连接时出错:', error);
  }
};