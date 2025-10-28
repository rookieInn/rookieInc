/**
 * 数据脱敏工具库
 * 支持手机号和身份证号的脱敏处理
 * 
 * @author AI Assistant
 * @version 1.0.0
 */

class DesensitizationUtils {
    constructor() {
        // 手机号正则表达式
        this.phoneRegex = /^(\+?86-?)?1[3-9]\d{9}$/;
        // 身份证号正则表达式
        this.idCardRegex = /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/;
        // 手机号格式化正则（用于处理带分隔符的格式）
        this.phoneFormatRegex = /^(\+?86-?)?(\d{3})-?(\d{4})-?(\d{4})$/;
    }

    /**
     * 检测数据类型
     * @param {string} data - 待检测的数据
     * @returns {string|null} - 数据类型：'phone'、'id' 或 null
     */
    detectDataType(data) {
        if (!data || typeof data !== 'string') {
            return null;
        }

        const cleanData = data.replace(/[\s-]/g, '');
        
        // 检测手机号
        if (this.phoneRegex.test(cleanData)) {
            return 'phone';
        }
        
        // 检测身份证号
        if (this.idCardRegex.test(cleanData)) {
            return 'id';
        }
        
        return null;
    }

    /**
     * 手机号脱敏
     * @param {string} phone - 手机号
     * @returns {string} - 脱敏后的手机号
     */
    desensitizePhone(phone) {
        if (!phone) return '';
        
        // 处理带格式的手机号
        const formatMatch = phone.match(this.phoneFormatRegex);
        if (formatMatch) {
            const [, prefix, part1, part2, part3] = formatMatch;
            return `${prefix || ''}${part1}-****-${part3}`;
        }
        
        // 处理标准11位手机号
        const cleanPhone = phone.replace(/[\s-]/g, '');
        if (cleanPhone.length === 11) {
            return cleanPhone.substring(0, 3) + '****' + cleanPhone.substring(7);
        }
        
        // 处理带国际区号的手机号
        if (cleanPhone.startsWith('86') && cleanPhone.length === 13) {
            return cleanPhone.substring(0, 5) + '****' + cleanPhone.substring(9);
        }
        
        return phone;
    }

    /**
     * 身份证号脱敏
     * @param {string} idCard - 身份证号
     * @returns {string} - 脱敏后的身份证号
     */
    desensitizeIdCard(idCard) {
        if (!idCard) return '';
        
        const cleanIdCard = idCard.replace(/[\s-]/g, '');
        
        if (cleanIdCard.length === 18) {
            // 保留前14位，后4位用*替换
            return cleanIdCard.substring(0, 14) + '****';
        }
        
        if (cleanIdCard.length === 15) {
            // 15位身份证号，保留前11位，后4位用*替换
            return cleanIdCard.substring(0, 11) + '****';
        }
        
        return idCard;
    }

    /**
     * 通用脱敏方法
     * @param {string} data - 待脱敏的数据
     * @returns {object|null} - 脱敏结果对象或null
     */
    desensitizeData(data) {
        if (!data || typeof data !== 'string') {
            return null;
        }

        const dataType = this.detectDataType(data);
        
        if (!dataType) {
            return null;
        }

        let desensitizedData;
        
        switch (dataType) {
            case 'phone':
                desensitizedData = this.desensitizePhone(data);
                break;
            case 'id':
                desensitizedData = this.desensitizeIdCard(data);
                break;
            default:
                return null;
        }

        return {
            original: data,
            desensitized: desensitizedData,
            type: dataType
        };
    }

    /**
     * 批量脱敏
     * @param {Array<string>} dataList - 待脱敏的数据列表
     * @returns {Array<object>} - 脱敏结果列表
     */
    batchDesensitize(dataList) {
        if (!Array.isArray(dataList)) {
            return [];
        }

        return dataList
            .map(data => this.desensitizeData(data))
            .filter(result => result !== null);
    }

    /**
     * 验证手机号格式
     * @param {string} phone - 手机号
     * @returns {boolean} - 是否为有效手机号
     */
    isValidPhone(phone) {
        if (!phone || typeof phone !== 'string') {
            return false;
        }
        
        const cleanPhone = phone.replace(/[\s-]/g, '');
        return this.phoneRegex.test(cleanPhone);
    }

    /**
     * 验证身份证号格式
     * @param {string} idCard - 身份证号
     * @returns {boolean} - 是否为有效身份证号
     */
    isValidIdCard(idCard) {
        if (!idCard || typeof idCard !== 'string') {
            return false;
        }
        
        const cleanIdCard = idCard.replace(/[\s-]/g, '');
        return this.idCardRegex.test(cleanIdCard);
    }

    /**
     * 获取脱敏统计信息
     * @param {Array<object>} results - 脱敏结果列表
     * @returns {object} - 统计信息
     */
    getStatistics(results) {
        if (!Array.isArray(results)) {
            return {
                total: 0,
                phoneCount: 0,
                idCount: 0,
                errorCount: 0
            };
        }

        const stats = {
            total: results.length,
            phoneCount: 0,
            idCount: 0,
            errorCount: 0
        };

        results.forEach(result => {
            if (result && result.type) {
                if (result.type === 'phone') {
                    stats.phoneCount++;
                } else if (result.type === 'id') {
                    stats.idCount++;
                }
            } else {
                stats.errorCount++;
            }
        });

        return stats;
    }

    /**
     * 自定义脱敏规则
     * @param {string} data - 待脱敏的数据
     * @param {object} options - 脱敏选项
     * @returns {string} - 脱敏后的数据
     */
    customDesensitize(data, options = {}) {
        const {
            keepStart = 3,    // 保留开头字符数
            keepEnd = 4,      // 保留结尾字符数
            maskChar = '*',   // 脱敏字符
            maskLength = 4    // 脱敏字符数量
        } = options;

        if (!data || typeof data !== 'string') {
            return '';
        }

        const dataLength = data.length;
        
        if (dataLength <= keepStart + keepEnd) {
            return data; // 数据太短，不进行脱敏
        }

        const start = data.substring(0, keepStart);
        const end = data.substring(dataLength - keepEnd);
        const mask = maskChar.repeat(maskLength);
        
        return start + mask + end;
    }

    /**
     * 高级脱敏（支持多种格式）
     * @param {string} data - 待脱敏的数据
     * @returns {object|null} - 脱敏结果
     */
    advancedDesensitize(data) {
        if (!data || typeof data !== 'string') {
            return null;
        }

        // 尝试检测并处理各种格式
        const cleanData = data.replace(/[\s-]/g, '');
        
        // 手机号检测
        if (this.isValidPhone(cleanData)) {
            return {
                original: data,
                desensitized: this.desensitizePhone(data),
                type: 'phone',
                format: this.detectPhoneFormat(data)
            };
        }
        
        // 身份证号检测
        if (this.isValidIdCard(cleanData)) {
            return {
                original: data,
                desensitized: this.desensitizeIdCard(data),
                type: 'id',
                format: this.detectIdCardFormat(data)
            };
        }
        
        return null;
    }

    /**
     * 检测手机号格式
     * @param {string} phone - 手机号
     * @returns {string} - 格式类型
     */
    detectPhoneFormat(phone) {
        if (phone.includes('+86')) return 'international';
        if (phone.includes('-')) return 'formatted';
        return 'standard';
    }

    /**
     * 检测身份证号格式
     * @param {string} idCard - 身份证号
     * @returns {string} - 格式类型
     */
    detectIdCardFormat(idCard) {
        if (idCard.includes('-')) return 'formatted';
        return 'standard';
    }
}

// 创建全局实例
const desensitizationUtils = new DesensitizationUtils();

// 全局函数，用于HTML页面调用
function desensitizeData(data) {
    return desensitizationUtils.desensitizeData(data);
}

function desensitizePhone(phone) {
    return desensitizationUtils.desensitizePhone(phone);
}

function desensitizeIdCard(idCard) {
    return desensitizationUtils.desensitizeIdCard(idCard);
}

function batchDesensitize(dataList) {
    return desensitizationUtils.batchDesensitize(dataList);
}

function isValidPhone(phone) {
    return desensitizationUtils.isValidPhone(phone);
}

function isValidIdCard(idCard) {
    return desensitizationUtils.isValidIdCard(idCard);
}

function customDesensitize(data, options) {
    return desensitizationUtils.customDesensitize(data, options);
}

function advancedDesensitize(data) {
    return desensitizationUtils.advancedDesensitize(data);
}

// 导出到全局作用域
if (typeof window !== 'undefined') {
    window.DesensitizationUtils = DesensitizationUtils;
    window.desensitizeData = desensitizeData;
    window.desensitizePhone = desensitizePhone;
    window.desensitizeIdCard = desensitizeIdCard;
    window.batchDesensitize = batchDesensitize;
    window.isValidPhone = isValidPhone;
    window.isValidIdCard = isValidIdCard;
    window.customDesensitize = customDesensitize;
    window.advancedDesensitize = advancedDesensitize;
}

// 如果是模块环境，导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        DesensitizationUtils,
        desensitizeData,
        desensitizePhone,
        desensitizeIdCard,
        batchDesensitize,
        isValidPhone,
        isValidIdCard,
        customDesensitize,
        advancedDesensitize
    };
}