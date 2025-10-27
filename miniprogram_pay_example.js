// 小程序支付示例代码
// 在小程序中使用微信支付API

// 配置API基础URL
const API_BASE_URL = 'https://yourdomain.com'; // 替换为你的API域名

/**
 * 创建小程序支付订单
 * @param {Object} paymentData 支付数据
 * @returns {Promise} 支付结果
 */
function createMiniprogramPayment(paymentData) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}/api/wechat/pay/miniprogram`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        openid: paymentData.openid,
        total_fee: paymentData.total_fee,
        body: paymentData.body,
        attach: paymentData.attach || '',
        out_trade_no: paymentData.out_trade_no || ''
      },
      success: function(res) {
        if (res.data.success) {
          resolve(res.data.data);
        } else {
          reject(new Error(res.data.error));
        }
      },
      fail: function(error) {
        reject(error);
      }
    });
  });
}

/**
 * 调用微信支付
 * @param {Object} paymentParams 支付参数
 * @returns {Promise} 支付结果
 */
function requestPayment(paymentParams) {
  return new Promise((resolve, reject) => {
    wx.requestPayment({
      timeStamp: paymentParams.timeStamp,
      nonceStr: paymentParams.nonceStr,
      package: paymentParams.package,
      signType: paymentParams.signType,
      paySign: paymentParams.paySign,
      success: function(res) {
        console.log('支付成功', res);
        resolve(res);
      },
      fail: function(error) {
        console.log('支付失败', error);
        reject(error);
      }
    });
  });
}

/**
 * 查询支付状态
 * @param {String} outTradeNo 商户订单号
 * @returns {Promise} 查询结果
 */
function queryPaymentStatus(outTradeNo) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}/api/wechat/pay/query`,
      method: 'POST',
      header: {
        'Content-Type': 'application/json'
      },
      data: {
        out_trade_no: outTradeNo
      },
      success: function(res) {
        if (res.data.success) {
          resolve(res.data.data);
        } else {
          reject(new Error(res.data.error));
        }
      },
      fail: function(error) {
        reject(error);
      }
    });
  });
}

/**
 * 获取支付状态（本地查询）
 * @param {String} outTradeNo 商户订单号
 * @returns {Promise} 查询结果
 */
function getPaymentStatus(outTradeNo) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}/api/wechat/pay/status/${outTradeNo}`,
      method: 'GET',
      success: function(res) {
        if (res.data.success) {
          resolve(res.data.data);
        } else {
          reject(new Error(res.data.error));
        }
      },
      fail: function(error) {
        reject(error);
      }
    });
  });
}

/**
 * 完整的支付流程示例
 * @param {Object} orderInfo 订单信息
 */
async function processPayment(orderInfo) {
  try {
    console.log('开始支付流程', orderInfo);
    
    // 1. 创建支付订单
    console.log('1. 创建支付订单...');
    const paymentData = await createMiniprogramPayment({
      openid: orderInfo.openid,
      total_fee: orderInfo.total_fee,
      body: orderInfo.body,
      attach: orderInfo.attach || '',
      out_trade_no: orderInfo.out_trade_no || ''
    });
    
    console.log('支付订单创建成功', paymentData);
    
    // 2. 调用微信支付
    console.log('2. 调用微信支付...');
    const payResult = await requestPayment(paymentData.miniprogram_params);
    
    console.log('微信支付调用成功', payResult);
    
    // 3. 查询支付状态
    console.log('3. 查询支付状态...');
    const statusResult = await queryPaymentStatus(paymentData.out_trade_no);
    
    console.log('支付状态查询结果', statusResult);
    
    // 4. 根据支付状态处理业务逻辑
    if (statusResult.trade_state === 'SUCCESS') {
      console.log('支付成功，处理业务逻辑...');
      // 这里可以调用你的业务API，如更新订单状态、发货等
      await handlePaymentSuccess(paymentData.out_trade_no, statusResult);
    } else {
      console.log('支付未成功，状态:', statusResult.trade_state);
    }
    
    return {
      success: true,
      out_trade_no: paymentData.out_trade_no,
      trade_state: statusResult.trade_state
    };
    
  } catch (error) {
    console.error('支付流程失败', error);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * 处理支付成功后的业务逻辑
 * @param {String} outTradeNo 商户订单号
 * @param {Object} paymentResult 支付结果
 */
async function handlePaymentSuccess(outTradeNo, paymentResult) {
  try {
    // 这里添加你的业务逻辑
    console.log('处理支付成功业务逻辑', outTradeNo, paymentResult);
    
    // 示例：更新订单状态
    // await updateOrderStatus(outTradeNo, 'PAID');
    
    // 示例：发送支付成功通知
    // await sendPaymentNotification(outTradeNo);
    
    // 示例：跳转到支付成功页面
    // wx.navigateTo({
    //   url: `/pages/payment/success?out_trade_no=${outTradeNo}`
    // });
    
  } catch (error) {
    console.error('处理支付成功业务逻辑失败', error);
  }
}

/**
 * 页面使用示例
 */
Page({
  data: {
    orderInfo: {
      openid: '', // 用户openid
      total_fee: 100, // 支付金额（分）
      body: '测试商品', // 商品描述
      attach: 'test_attach', // 附加数据
      out_trade_no: '' // 商户订单号
    }
  },
  
  onLoad: function(options) {
    // 获取用户openid
    this.getUserOpenId();
    
    // 生成商户订单号
    this.setData({
      'orderInfo.out_trade_no': this.generateOutTradeNo()
    });
  },
  
  // 获取用户openid
  getUserOpenId: function() {
    wx.login({
      success: (res) => {
        if (res.code) {
          // 发送code到后端获取openid
          wx.request({
            url: `${API_BASE_URL}/api/wechat/get_openid`,
            method: 'POST',
            data: {
              code: res.code
            },
            success: (res) => {
              if (res.data.success) {
                this.setData({
                  'orderInfo.openid': res.data.openid
                });
              }
            }
          });
        }
      }
    });
  },
  
  // 生成商户订单号
  generateOutTradeNo: function() {
    const timestamp = new Date().getTime();
    const random = Math.floor(Math.random() * 1000);
    return `WX${timestamp}${random}`;
  },
  
  // 支付按钮点击事件
  onPayButtonClick: function() {
    const orderInfo = this.data.orderInfo;
    
    if (!orderInfo.openid) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }
    
    if (!orderInfo.total_fee || orderInfo.total_fee <= 0) {
      wx.showToast({
        title: '支付金额无效',
        icon: 'none'
      });
      return;
    }
    
    // 显示加载中
    wx.showLoading({
      title: '正在支付...'
    });
    
    // 执行支付流程
    processPayment(orderInfo).then(result => {
      wx.hideLoading();
      
      if (result.success) {
        if (result.trade_state === 'SUCCESS') {
          wx.showToast({
            title: '支付成功',
            icon: 'success'
          });
        } else {
          wx.showToast({
            title: '支付未完成',
            icon: 'none'
          });
        }
      } else {
        wx.showToast({
          title: result.error || '支付失败',
          icon: 'none'
        });
      }
    }).catch(error => {
      wx.hideLoading();
      wx.showToast({
        title: '支付失败',
        icon: 'none'
      });
      console.error('支付失败', error);
    });
  },
  
  // 查询支付状态
  onQueryPaymentStatus: function() {
    const outTradeNo = this.data.orderInfo.out_trade_no;
    
    if (!outTradeNo) {
      wx.showToast({
        title: '订单号不存在',
        icon: 'none'
      });
      return;
    }
    
    wx.showLoading({
      title: '查询中...'
    });
    
    getPaymentStatus(outTradeNo).then(result => {
      wx.hideLoading();
      wx.showModal({
        title: '支付状态',
        content: `订单号: ${result.out_trade_no}\n状态: ${result.trade_state}\n时间: ${result.update_time}`,
        showCancel: false
      });
    }).catch(error => {
      wx.hideLoading();
      wx.showToast({
        title: '查询失败',
        icon: 'none'
      });
      console.error('查询失败', error);
    });
  }
});

// 导出函数供其他页面使用
module.exports = {
  createMiniprogramPayment,
  requestPayment,
  queryPaymentStatus,
  getPaymentStatus,
  processPayment,
  handlePaymentSuccess
};