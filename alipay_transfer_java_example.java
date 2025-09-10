package com.alipay.transfer;

import com.alipay.api.AlipayApiException;
import com.alipay.api.AlipayClient;
import com.alipay.api.DefaultAlipayClient;
import com.alipay.api.domain.AlipayFundTransToaccountTransferModel;
import com.alipay.api.request.AlipayFundTransToaccountTransferRequest;
import com.alipay.api.response.AlipayFundTransToaccountTransferResponse;

/**
 * 支付宝转账给个人用户示例 - Java版本
 * 
 * 使用前请确保：
 * 1. 已添加支付宝SDK依赖
 * 2. 已配置应用ID、私钥、公钥等参数
 * 3. 已开通转账功能
 */
public class AlipayTransferExample {
    
    // 支付宝网关地址
    private static final String GATEWAY_URL = "https://openapi.alipay.com/gateway.do";
    // 沙箱环境地址（测试时使用）
    // private static final String GATEWAY_URL = "https://openapi.alipaydev.com/gateway.do";
    
    // 应用ID
    private static final String APP_ID = "your_app_id";
    
    // 应用私钥
    private static final String PRIVATE_KEY = "your_private_key";
    
    // 支付宝公钥
    private static final String ALIPAY_PUBLIC_KEY = "your_alipay_public_key";
    
    // 签名算法
    private static final String SIGN_TYPE = "RSA2";
    
    // 字符编码格式
    private static final String CHARSET = "utf-8";
    
    // 数据格式
    private static final String FORMAT = "json";
    
    /**
     * 转账给个人用户
     * 
     * @param outBizNo 商户转账唯一订单号
     * @param payeeAccount 收款方账户（支付宝账号或用户ID）
     * @param payeeType 收款方账户类型（ALIPAY_LOGONID或ALIPAY_USERID）
     * @param amount 转账金额（元）
     * @param payerShowName 付款方显示名称（可选）
     * @param payeeRealName 收款方真实姓名（可选）
     * @param remark 转账备注（可选）
     * @return 转账结果
     */
    public static AlipayFundTransToaccountTransferResponse transferToAccount(
            String outBizNo,
            String payeeAccount,
            String payeeType,
            String amount,
            String payerShowName,
            String payeeRealName,
            String remark) {
        
        try {
            // 创建AlipayClient
            AlipayClient alipayClient = new DefaultAlipayClient(
                    GATEWAY_URL, APP_ID, PRIVATE_KEY, FORMAT, CHARSET, ALIPAY_PUBLIC_KEY, SIGN_TYPE);
            
            // 创建API请求
            AlipayFundTransToaccountTransferRequest request = new AlipayFundTransToaccountTransferRequest();
            
            // 设置业务参数
            AlipayFundTransToaccountTransferModel model = new AlipayFundTransToaccountTransferModel();
            model.setOutBizNo(outBizNo);
            model.setPayeeType(payeeType);
            model.setPayeeAccount(payeeAccount);
            model.setAmount(amount);
            
            // 可选参数
            if (payerShowName != null && !payerShowName.isEmpty()) {
                model.setPayerShowName(payerShowName);
            }
            if (payeeRealName != null && !payeeRealName.isEmpty()) {
                model.setPayeeRealName(payeeRealName);
            }
            if (remark != null && !remark.isEmpty()) {
                model.setRemark(remark);
            }
            
            request.setBizModel(model);
            
            // 执行请求
            AlipayFundTransToaccountTransferResponse response = alipayClient.execute(request);
            
            return response;
            
        } catch (AlipayApiException e) {
            System.err.println("支付宝转账接口调用失败：" + e.getErrMsg());
            e.printStackTrace();
            return null;
        }
    }
    
    /**
     * 转账给个人用户（简化版本）
     * 
     * @param payeeAccount 收款方支付宝账号
     * @param amount 转账金额（元）
     * @param remark 转账备注
     * @return 转账结果
     */
    public static AlipayFundTransToaccountTransferResponse simpleTransfer(
            String payeeAccount,
            String amount,
            String remark) {
        
        // 生成唯一订单号（实际项目中建议使用更复杂的生成策略）
        String outBizNo = "TRANSFER_" + System.currentTimeMillis();
        
        return transferToAccount(
                outBizNo,
                payeeAccount,
                "ALIPAY_LOGONID", // 使用支付宝账号
                amount,
                "测试付款方", // 付款方显示名称
                null, // 不校验收款方真实姓名
                remark
        );
    }
    
    /**
     * 处理转账结果
     * 
     * @param response 转账响应
     */
    public static void handleTransferResponse(AlipayFundTransToaccountTransferResponse response) {
        if (response == null) {
            System.out.println("转账请求失败");
            return;
        }
        
        if (response.isSuccess()) {
            System.out.println("转账成功！");
            System.out.println("订单号：" + response.getOutBizNo());
            System.out.println("支付宝转账单据号：" + response.getOrderId());
            System.out.println("支付时间：" + response.getPayDate());
        } else {
            System.out.println("转账失败！");
            System.out.println("错误码：" + response.getCode());
            System.out.println("错误信息：" + response.getMsg());
            System.out.println("子错误码：" + response.getSubCode());
            System.out.println("子错误信息：" + response.getSubMsg());
        }
    }
    
    /**
     * 主方法 - 测试转账功能
     */
    public static void main(String[] args) {
        // 测试转账
        AlipayFundTransToaccountTransferResponse response = simpleTransfer(
                "test@example.com", // 收款方支付宝账号
                "0.01", // 转账金额（测试金额）
                "测试转账" // 转账备注
        );
        
        // 处理结果
        handleTransferResponse(response);
    }
}

/**
 * Maven依赖配置（pom.xml）：
 * 
 * <dependency>
 *     <groupId>com.alipay.sdk</groupId>
 *     <artifactId>alipay-sdk-java</artifactId>
 *     <version>4.38.10.ALL</version>
 * </dependency>
 */