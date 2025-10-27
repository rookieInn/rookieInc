/**
 * 支付宝转账给个人用户示例 - Node.js版本
 * 
 * 使用前请确保：
 * 1. 已安装支付宝SDK：npm install alipay-sdk
 * 2. 已配置应用ID、私钥、公钥等参数
 * 3. 已开通转账功能
 */

const AlipaySdk = require('alipay-sdk').default;
const AlipayFormData = require('alipay-sdk/lib/form').default;
const crypto = require('crypto');

class AlipayTransferExample {
    constructor(config) {
        this.alipaySdk = new AlipaySdk({
            appId: config.appId,
            privateKey: config.privateKey,
            alipayPublicKey: config.alipayPublicKey,
            gateway: config.gateway || 'https://openapi.alipay.com/gateway.do',
            signType: 'RSA2',
            charset: 'utf-8',
            version: '1.0',
            format: 'json'
        });
    }

    /**
     * 转账给个人用户
     * 
     * @param {Object} params 转账参数
     * @param {string} params.outBizNo 商户转账唯一订单号
     * @param {string} params.payeeAccount 收款方账户
     * @param {string} params.payeeType 收款方账户类型
     * @param {string} params.amount 转账金额
     * @param {string} params.payerShowName 付款方显示名称（可选）
     * @param {string} params.payeeRealName 收款方真实姓名（可选）
     * @param {string} params.remark 转账备注（可选）
     * @returns {Promise<Object>} 转账结果
     */
    async transferToAccount(params) {
        try {
            const formData = new AlipayFormData();
            
            // 设置业务参数
            formData.setMethod('alipay.fund.trans.toaccount.transfer');
            formData.setBizContent({
                out_biz_no: params.outBizNo,
                payee_type: params.payeeType,
                payee_account: params.payeeAccount,
                amount: params.amount,
                payer_show_name: params.payerShowName,
                payee_real_name: params.payeeRealName,
                remark: params.remark
            });

            // 调用转账接口
            const result = await this.alipaySdk.exec(
                'alipay.fund.trans.toaccount.transfer',
                {},
                { formData: formData }
            );

            return result;

        } catch (error) {
            console.error('支付宝转账接口调用失败：', error.message);
            return null;
        }
    }

    /**
     * 转账给个人用户（简化版本）
     * 
     * @param {string} payeeAccount 收款方支付宝账号
     * @param {string} amount 转账金额（元）
     * @param {string} remark 转账备注
     * @returns {Promise<Object>} 转账结果
     */
    async simpleTransfer(payeeAccount, amount, remark = null) {
        // 生成唯一订单号
        const outBizNo = `TRANSFER_${Date.now()}`;

        return await this.transferToAccount({
            outBizNo: outBizNo,
            payeeAccount: payeeAccount,
            payeeType: 'ALIPAY_LOGONID', // 使用支付宝账号
            amount: amount,
            payerShowName: '测试付款方', // 付款方显示名称
            payeeRealName: null, // 不校验收款方真实姓名
            remark: remark
        });
    }

    /**
     * 处理转账结果
     * 
     * @param {Object} response 转账响应
     */
    handleTransferResponse(response) {
        if (!response) {
            console.log('转账请求失败');
            return;
        }

        if (response.code === '10000') {
            console.log('转账成功！');
            console.log(`订单号：${response.out_biz_no}`);
            console.log(`支付宝转账单据号：${response.order_id}`);
            console.log(`支付时间：${response.pay_date}`);
        } else {
            console.log('转账失败！');
            console.log(`错误码：${response.code}`);
            console.log(`错误信息：${response.msg}`);
            console.log(`子错误码：${response.sub_code}`);
            console.log(`子错误信息：${response.sub_msg}`);
        }
    }

    /**
     * 验证转账金额
     * 
     * @param {string} amount 转账金额
     * @returns {boolean} 是否有效
     */
    validateAmount(amount) {
        try {
            const amountFloat = parseFloat(amount);
            if (amountFloat < 0.1) {
                console.log('转账金额不能少于0.1元');
                return false;
            }
            if (amountFloat > 50000) {
                console.log('转账给个人账户单笔不能超过5万元');
                return false;
            }
            return true;
        } catch (error) {
            console.log('转账金额格式错误');
            return false;
        }
    }

    /**
     * 生成唯一订单号
     * 
     * @returns {string} 订单号
     */
    generateOutBizNo() {
        const timestamp = Date.now();
        const random = Math.random().toString(36).substr(2, 9);
        return `TRANSFER_${timestamp}_${random}`;
    }
}

/**
 * 主函数 - 测试转账功能
 */
async function main() {
    // 配置参数（请替换为实际值）
    const config = {
        appId: 'your_app_id',
        privateKey: `-----BEGIN RSA PRIVATE KEY-----
your_private_key_content
-----END RSA PRIVATE KEY-----`,
        alipayPublicKey: `-----BEGIN PUBLIC KEY-----
your_alipay_public_key_content
-----END PUBLIC KEY-----`,
        gateway: 'https://openapi.alipaydev.com/gateway.do' // 沙箱环境
    };

    // 创建转账实例
    const transferExample = new AlipayTransferExample(config);

    // 测试转账
    const payeeAccount = 'test@example.com'; // 收款方支付宝账号
    const amount = '0.01'; // 转账金额（测试金额）
    const remark = '测试转账'; // 转账备注

    // 验证金额
    if (!transferExample.validateAmount(amount)) {
        return;
    }

    // 执行转账
    const response = await transferExample.simpleTransfer(
        payeeAccount,
        amount,
        remark
    );

    // 处理结果
    transferExample.handleTransferResponse(response);
}

// 导出类供其他模块使用
module.exports = AlipayTransferExample;

// 如果直接运行此文件，则执行测试
if (require.main === module) {
    main().catch(console.error);
}

/**
 * 安装依赖：
 * npm install alipay-sdk
 * 
 * package.json 示例：
 * {
 *   "name": "alipay-transfer-example",
 *   "version": "1.0.0",
 *   "description": "支付宝转账示例",
 *   "main": "alipay_transfer_nodejs_example.js",
 *   "dependencies": {
 *     "alipay-sdk": "^3.4.0"
 *   }
 * }
 * 
 * 使用示例：
 * const AlipayTransferExample = require('./alipay_transfer_nodejs_example');
 * 
 * const config = {
 *     appId: 'your_app_id',
 *     privateKey: 'your_private_key',
 *     alipayPublicKey: 'your_alipay_public_key'
 * };
 * 
 * const transfer = new AlipayTransferExample(config);
 * 
 * // 执行转账
 * transfer.simpleTransfer('user@example.com', '1.00', '测试转账')
 *     .then(response => {
 *         transfer.handleTransferResponse(response);
 *     })
 *     .catch(error => {
 *         console.error('转账失败：', error);
 *     });
 */