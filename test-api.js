#!/usr/bin/env node

/**
 * API测试脚本
 * 用于测试直播管理后台系统的基本功能
 */

const axios = require('axios');

const BASE_URL = 'http://localhost:3000/api';
let authToken = '';

// 创建axios实例
const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
});

// 请求拦截器
api.interceptors.request.use((config) => {
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});

// 测试用例
const tests = [
  {
    name: '健康检查',
    test: async () => {
      const response = await axios.get('http://localhost:3000/health');
      console.log('✅ 健康检查:', response.data);
    }
  },
  {
    name: '用户注册',
    test: async () => {
      const userData = {
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
        role: 'admin'
      };
      const response = await api.post('/auth/register', userData);
      if (response.data.success) {
        authToken = response.data.data.token;
        console.log('✅ 用户注册成功:', response.data.data.user.username);
      } else {
        console.log('❌ 用户注册失败:', response.data.message);
      }
    }
  },
  {
    name: '用户登录',
    test: async () => {
      const loginData = {
        email: 'test@example.com',
        password: 'password123'
      };
      const response = await api.post('/auth/login', loginData);
      if (response.data.success) {
        authToken = response.data.data.token;
        console.log('✅ 用户登录成功:', response.data.data.user.username);
      } else {
        console.log('❌ 用户登录失败:', response.data.message);
      }
    }
  },
  {
    name: '获取用户信息',
    test: async () => {
      const response = await api.get('/auth/profile');
      if (response.data.success) {
        console.log('✅ 获取用户信息成功:', response.data.data.username);
      } else {
        console.log('❌ 获取用户信息失败:', response.data.message);
      }
    }
  },
  {
    name: '创建直播房间',
    test: async () => {
      const roomData = {
        title: '测试直播房间',
        description: '这是一个测试直播房间',
        category: '游戏',
        tags: ['测试', '游戏'],
        isPublic: true
      };
      const response = await api.post('/rooms', roomData);
      if (response.data.success) {
        console.log('✅ 创建直播房间成功:', response.data.data.title);
      } else {
        console.log('❌ 创建直播房间失败:', response.data.message);
      }
    }
  },
  {
    name: '获取直播房间列表',
    test: async () => {
      const response = await api.get('/rooms');
      if (response.data.success) {
        console.log('✅ 获取直播房间列表成功，共', response.data.data.length, '个房间');
      } else {
        console.log('❌ 获取直播房间列表失败:', response.data.message);
      }
    }
  },
  {
    name: '获取用户统计',
    test: async () => {
      const response = await api.get('/users/stats');
      if (response.data.success) {
        console.log('✅ 获取用户统计成功:', response.data.data);
      } else {
        console.log('❌ 获取用户统计失败:', response.data.message);
      }
    }
  },
  {
    name: '创建举报',
    test: async () => {
      const reportData = {
        targetType: 'room',
        targetId: 'test-room-id',
        reason: 'spam',
        description: '这是一个测试举报'
      };
      const response = await api.post('/reports', reportData);
      if (response.data.success) {
        console.log('✅ 创建举报成功:', response.data.data._id);
      } else {
        console.log('❌ 创建举报失败:', response.data.message);
      }
    }
  },
  {
    name: '获取通知列表',
    test: async () => {
      const response = await api.get('/notifications');
      if (response.data.success) {
        console.log('✅ 获取通知列表成功，共', response.data.data.length, '条通知');
      } else {
        console.log('❌ 获取通知列表失败:', response.data.message);
      }
    }
  }
];

// 运行测试
async function runTests() {
  console.log('🚀 开始API测试...\n');
  
  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    try {
      console.log(`📋 测试: ${test.name}`);
      await test.test();
      passed++;
    } catch (error) {
      console.log(`❌ 测试失败: ${test.name}`);
      console.log('   错误:', error.message);
      failed++;
    }
    console.log('');
  }

  console.log('📊 测试结果:');
  console.log(`   ✅ 通过: ${passed}`);
  console.log(`   ❌ 失败: ${failed}`);
  console.log(`   📈 成功率: ${((passed / (passed + failed)) * 100).toFixed(1)}%`);
}

// 检查服务器是否运行
async function checkServer() {
  try {
    await axios.get('http://localhost:3000/health');
    return true;
  } catch (error) {
    console.log('❌ 服务器未运行，请先启动服务器');
    console.log('   启动命令: npm run dev');
    return false;
  }
}

// 主函数
async function main() {
  const isServerRunning = await checkServer();
  if (!isServerRunning) {
    process.exit(1);
  }
  
  await runTests();
}

// 运行测试
main().catch(console.error);