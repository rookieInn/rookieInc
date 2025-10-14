-- 五级行政区划查询系统数据库初始化脚本
-- 省、市、县、镇、村五级联动查询

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS administrative_query 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE administrative_query;

-- 创建省级表
CREATE TABLE IF NOT EXISTS provinces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL COMMENT '省级行政区划代码',
    name VARCHAR(50) NOT NULL COMMENT '省级名称',
    short_name VARCHAR(20) COMMENT '简称',
    pinyin VARCHAR(100) COMMENT '拼音',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_code (code),
    INDEX idx_name (name),
    INDEX idx_sort_order (sort_order)
) COMMENT '省级行政区划表';

-- 创建市级表
CREATE TABLE IF NOT EXISTS cities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL COMMENT '市级行政区划代码',
    name VARCHAR(50) NOT NULL COMMENT '市级名称',
    short_name VARCHAR(20) COMMENT '简称',
    pinyin VARCHAR(100) COMMENT '拼音',
    province_id INT NOT NULL COMMENT '所属省份ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE CASCADE,
    INDEX idx_code (code),
    INDEX idx_name (name),
    INDEX idx_province_id (province_id),
    INDEX idx_sort_order (sort_order)
) COMMENT '市级行政区划表';

-- 创建县级表
CREATE TABLE IF NOT EXISTS counties (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL COMMENT '县级行政区划代码',
    name VARCHAR(50) NOT NULL COMMENT '县级名称',
    short_name VARCHAR(20) COMMENT '简称',
    pinyin VARCHAR(100) COMMENT '拼音',
    city_id INT NOT NULL COMMENT '所属城市ID',
    province_id INT NOT NULL COMMENT '所属省份ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE CASCADE,
    INDEX idx_code (code),
    INDEX idx_name (name),
    INDEX idx_city_id (city_id),
    INDEX idx_province_id (province_id),
    INDEX idx_sort_order (sort_order)
) COMMENT '县级行政区划表';

-- 创建镇级表
CREATE TABLE IF NOT EXISTS towns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL COMMENT '镇级行政区划代码',
    name VARCHAR(50) NOT NULL COMMENT '镇级名称',
    short_name VARCHAR(20) COMMENT '简称',
    pinyin VARCHAR(100) COMMENT '拼音',
    county_id INT NOT NULL COMMENT '所属县ID',
    city_id INT NOT NULL COMMENT '所属城市ID',
    province_id INT NOT NULL COMMENT '所属省份ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (county_id) REFERENCES counties(id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE CASCADE,
    INDEX idx_code (code),
    INDEX idx_name (name),
    INDEX idx_county_id (county_id),
    INDEX idx_city_id (city_id),
    INDEX idx_province_id (province_id),
    INDEX idx_sort_order (sort_order)
) COMMENT '镇级行政区划表';

-- 创建村级表
CREATE TABLE IF NOT EXISTS villages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(6) UNIQUE NOT NULL COMMENT '村级行政区划代码',
    name VARCHAR(50) NOT NULL COMMENT '村级名称',
    short_name VARCHAR(20) COMMENT '简称',
    pinyin VARCHAR(100) COMMENT '拼音',
    town_id INT NOT NULL COMMENT '所属镇ID',
    county_id INT NOT NULL COMMENT '所属县ID',
    city_id INT NOT NULL COMMENT '所属城市ID',
    province_id INT NOT NULL COMMENT '所属省份ID',
    sort_order INT DEFAULT 0 COMMENT '排序',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (town_id) REFERENCES towns(id) ON DELETE CASCADE,
    FOREIGN KEY (county_id) REFERENCES counties(id) ON DELETE CASCADE,
    FOREIGN KEY (city_id) REFERENCES cities(id) ON DELETE CASCADE,
    FOREIGN KEY (province_id) REFERENCES provinces(id) ON DELETE CASCADE,
    INDEX idx_code (code),
    INDEX idx_name (name),
    INDEX idx_town_id (town_id),
    INDEX idx_county_id (county_id),
    INDEX idx_city_id (city_id),
    INDEX idx_province_id (province_id),
    INDEX idx_sort_order (sort_order)
) COMMENT '村级行政区划表';

-- 创建视图：完整行政区划层级关系
CREATE VIEW administrative_hierarchy AS
SELECT 
    v.id as village_id,
    v.code as village_code,
    v.name as village_name,
    v.pinyin as village_pinyin,
    t.id as town_id,
    t.code as town_code,
    t.name as town_name,
    t.pinyin as town_pinyin,
    c.id as county_id,
    c.code as county_code,
    c.name as county_name,
    c.pinyin as county_pinyin,
    ci.id as city_id,
    ci.code as city_code,
    ci.name as city_name,
    ci.pinyin as city_pinyin,
    p.id as province_id,
    p.code as province_code,
    p.name as province_name,
    p.pinyin as province_pinyin,
    CONCAT(p.name, ci.name, c.name, t.name, v.name) as full_path,
    CONCAT(p.code, ci.code, c.code, t.code, v.code) as full_code
FROM villages v
JOIN towns t ON v.town_id = t.id
JOIN counties c ON v.county_id = c.id
JOIN cities ci ON v.city_id = ci.id
JOIN provinces p ON v.province_id = p.id
WHERE v.is_active = TRUE 
  AND t.is_active = TRUE 
  AND c.is_active = TRUE 
  AND ci.is_active = TRUE 
  AND p.is_active = TRUE;

-- 创建存储过程：根据上级ID获取下级行政区划
DELIMITER //
CREATE PROCEDURE GetSubAdministrativeDivisions(
    IN p_level VARCHAR(10),
    IN p_parent_id INT
)
BEGIN
    CASE p_level
        WHEN 'province' THEN
            SELECT id, code, name, short_name, pinyin, sort_order 
            FROM cities 
            WHERE province_id = p_parent_id AND is_active = TRUE 
            ORDER BY sort_order, name;
        WHEN 'city' THEN
            SELECT id, code, name, short_name, pinyin, sort_order 
            FROM counties 
            WHERE city_id = p_parent_id AND is_active = TRUE 
            ORDER BY sort_order, name;
        WHEN 'county' THEN
            SELECT id, code, name, short_name, pinyin, sort_order 
            FROM towns 
            WHERE county_id = p_parent_id AND is_active = TRUE 
            ORDER BY sort_order, name;
        WHEN 'town' THEN
            SELECT id, code, name, short_name, pinyin, sort_order 
            FROM villages 
            WHERE town_id = p_parent_id AND is_active = TRUE 
            ORDER BY sort_order, name;
        ELSE
            SELECT 'Invalid level parameter' as error;
    END CASE;
END //
DELIMITER ;

-- 创建存储过程：搜索行政区划
DELIMITER //
CREATE PROCEDURE SearchAdministrativeDivisions(
    IN p_keyword VARCHAR(100)
)
BEGIN
    SELECT 
        'province' as level,
        id, code, name, short_name, pinyin, NULL as parent_id, NULL as parent_name
    FROM provinces 
    WHERE (name LIKE CONCAT('%', p_keyword, '%') OR pinyin LIKE CONCAT('%', p_keyword, '%'))
      AND is_active = TRUE
    
    UNION ALL
    
    SELECT 
        'city' as level,
        c.id, c.code, c.name, c.short_name, c.pinyin, c.province_id, p.name as parent_name
    FROM cities c
    JOIN provinces p ON c.province_id = p.id
    WHERE (c.name LIKE CONCAT('%', p_keyword, '%') OR c.pinyin LIKE CONCAT('%', p_keyword, '%'))
      AND c.is_active = TRUE
    
    UNION ALL
    
    SELECT 
        'county' as level,
        co.id, co.code, co.name, co.short_name, co.pinyin, co.city_id, ci.name as parent_name
    FROM counties co
    JOIN cities ci ON co.city_id = ci.id
    WHERE (co.name LIKE CONCAT('%', p_keyword, '%') OR co.pinyin LIKE CONCAT('%', p_keyword, '%'))
      AND co.is_active = TRUE
    
    UNION ALL
    
    SELECT 
        'town' as level,
        t.id, t.code, t.name, t.short_name, t.pinyin, t.county_id, c.name as parent_name
    FROM towns t
    JOIN counties c ON t.county_id = c.id
    WHERE (t.name LIKE CONCAT('%', p_keyword, '%') OR t.pinyin LIKE CONCAT('%', p_keyword, '%'))
      AND t.is_active = TRUE
    
    UNION ALL
    
    SELECT 
        'village' as level,
        v.id, v.code, v.name, v.short_name, v.pinyin, v.town_id, t.name as parent_name
    FROM villages v
    JOIN towns t ON v.town_id = t.id
    WHERE (v.name LIKE CONCAT('%', p_keyword, '%') OR v.pinyin LIKE CONCAT('%', p_keyword, '%'))
      AND v.is_active = TRUE
    
    ORDER BY level, name;
END //
DELIMITER ;

-- 插入示例数据

-- 插入省级数据
INSERT INTO provinces (code, name, short_name, pinyin, sort_order) VALUES
('110000', '北京市', '京', 'beijing', 1),
('120000', '天津市', '津', 'tianjin', 2),
('130000', '河北省', '冀', 'hebei', 3),
('140000', '山西省', '晋', 'shanxi', 4),
('150000', '内蒙古自治区', '蒙', 'neimenggu', 5),
('210000', '辽宁省', '辽', 'liaoning', 6),
('220000', '吉林省', '吉', 'jilin', 7),
('230000', '黑龙江省', '黑', 'heilongjiang', 8),
('310000', '上海市', '沪', 'shanghai', 9),
('320000', '江苏省', '苏', 'jiangsu', 10),
('330000', '浙江省', '浙', 'zhejiang', 11),
('340000', '安徽省', '皖', 'anhui', 12),
('350000', '福建省', '闽', 'fujian', 13),
('360000', '江西省', '赣', 'jiangxi', 14),
('370000', '山东省', '鲁', 'shandong', 15),
('410000', '河南省', '豫', 'henan', 16),
('420000', '湖北省', '鄂', 'hubei', 17),
('430000', '湖南省', '湘', 'hunan', 18),
('440000', '广东省', '粤', 'guangdong', 19),
('450000', '广西壮族自治区', '桂', 'guangxi', 20),
('460000', '海南省', '琼', 'hainan', 21),
('500000', '重庆市', '渝', 'chongqing', 22),
('510000', '四川省', '川', 'sichuan', 23),
('520000', '贵州省', '贵', 'guizhou', 24),
('530000', '云南省', '滇', 'yunnan', 25),
('540000', '西藏自治区', '藏', 'xizang', 26),
('610000', '陕西省', '陕', 'shaanxi', 27),
('620000', '甘肃省', '甘', 'gansu', 28),
('630000', '青海省', '青', 'qinghai', 29),
('640000', '宁夏回族自治区', '宁', 'ningxia', 30),
('650000', '新疆维吾尔自治区', '新', 'xinjiang', 31);

-- 插入北京市市级数据
INSERT INTO cities (code, name, short_name, pinyin, province_id, sort_order) VALUES
('110100', '北京市', '京', 'beijing', 1, 1);

-- 插入北京市区县数据
INSERT INTO counties (code, name, short_name, pinyin, city_id, province_id, sort_order) VALUES
('110101', '东城区', '东城', 'dongcheng', 1, 1, 1),
('110102', '西城区', '西城', 'xicheng', 1, 1, 2),
('110105', '朝阳区', '朝阳', 'chaoyang', 1, 1, 3),
('110106', '丰台区', '丰台', 'fengtai', 1, 1, 4),
('110107', '石景山区', '石景山', 'shijingshan', 1, 1, 5),
('110108', '海淀区', '海淀', 'haidian', 1, 1, 6),
('110109', '门头沟区', '门头沟', 'mentougou', 1, 1, 7),
('110111', '房山区', '房山', 'fangshan', 1, 1, 8),
('110112', '通州区', '通州', 'tongzhou', 1, 1, 9),
('110113', '顺义区', '顺义', 'shunyi', 1, 1, 10),
('110114', '昌平区', '昌平', 'changping', 1, 1, 11),
('110115', '大兴区', '大兴', 'daxing', 1, 1, 12),
('110116', '怀柔区', '怀柔', 'huairou', 1, 1, 13),
('110117', '平谷区', '平谷', 'pinggu', 1, 1, 14),
('110118', '密云区', '密云', 'miyun', 1, 1, 15),
('110119', '延庆区', '延庆', 'yanqing', 1, 1, 16);

-- 插入朝阳区镇级数据
INSERT INTO towns (code, name, short_name, pinyin, county_id, city_id, province_id, sort_order) VALUES
('110105001', '建外街道', '建外', 'jianwai', 3, 1, 1, 1),
('110105002', '朝外街道', '朝外', 'chaowai', 3, 1, 1, 2),
('110105003', '呼家楼街道', '呼家楼', 'hujialou', 3, 1, 1, 3),
('110105004', '三里屯街道', '三里屯', 'sanlitun', 3, 1, 1, 4),
('110105005', '左家庄街道', '左家庄', 'zuojiazhuang', 3, 1, 1, 5),
('110105006', '香河园街道', '香河园', 'xiangheyuan', 3, 1, 1, 6),
('110105007', '和平街街道', '和平街', 'hepingjie', 3, 1, 1, 7),
('110105008', '安贞街道', '安贞', 'anzhen', 3, 1, 1, 8),
('110105009', '亚运村街道', '亚运村', 'yayuncun', 3, 1, 1, 9),
('110105010', '小关街道', '小关', 'xiaoguan', 3, 1, 1, 10),
('110105011', '酒仙桥街道', '酒仙桥', 'jiuxianqiao', 3, 1, 1, 11),
('110105012', '麦子店街道', '麦子店', 'maizidian', 3, 1, 1, 12),
('110105013', '团结湖街道', '团结湖', 'tuanjiehu', 3, 1, 1, 13),
('110105014', '六里屯街道', '六里屯', 'liulitun', 3, 1, 1, 14),
('110105015', '八里庄街道', '八里庄', 'balizhuang', 3, 1, 1, 15),
('110105016', '双井街道', '双井', 'shuangjing', 3, 1, 1, 16),
('110105017', '劲松街道', '劲松', 'jinsong', 3, 1, 1, 17),
('110105018', '潘家园街道', '潘家园', 'panjiayuan', 3, 1, 1, 18),
('110105019', '垡头街道', '垡头', 'fatou', 3, 1, 1, 19),
('110105020', '南磨房街道', '南磨房', 'nanmofang', 3, 1, 1, 20),
('110105021', '高碑店街道', '高碑店', 'gaobeidian', 3, 1, 1, 21),
('110105022', '将台街道', '将台', 'jiangtai', 3, 1, 1, 22),
('110105023', '太阳宫街道', '太阳宫', 'taiyanggong', 3, 1, 1, 23),
('110105024', '大屯街道', '大屯', 'datun', 3, 1, 1, 24),
('110105025', '望京街道', '望京', 'wangjing', 3, 1, 1, 25),
('110105026', '小红门街道', '小红门', 'xiaohongmen', 3, 1, 1, 26),
('110105027', '十八里店街道', '十八里店', 'shibalidian', 3, 1, 1, 27),
('110105028', '平房街道', '平房', 'pingfang', 3, 1, 1, 28),
('110105029', '东风街道', '东风', 'dongfeng', 3, 1, 1, 29),
('110105030', '奥运村街道', '奥运村', 'aoyuncun', 3, 1, 1, 30),
('110105031', '来广营街道', '来广营', 'laiguangying', 3, 1, 1, 31),
('110105032', '常营街道', '常营', 'changying', 3, 1, 1, 32),
('110105033', '三间房街道', '三间房', 'sanjianfang', 3, 1, 1, 33),
('110105034', '管庄街道', '管庄', 'guanzhuang', 3, 1, 1, 34),
('110105035', '金盏街道', '金盏', 'jinzhan', 3, 1, 1, 35),
('110105036', '孙河街道', '孙河', 'sunhe', 3, 1, 1, 36),
('110105037', '崔各庄街道', '崔各庄', 'cuigezhuang', 3, 1, 1, 37),
('110105038', '东坝街道', '东坝', 'dongba', 3, 1, 1, 38),
('110105039', '黑庄户街道', '黑庄户', 'heizhuanghu', 3, 1, 1, 39),
('110105040', '豆各庄街道', '豆各庄', 'dougezhuang', 3, 1, 1, 40),
('110105041', '王四营街道', '王四营', 'wangsying', 3, 1, 1, 41),
('110105042', '东湖街道', '东湖', 'donghu', 3, 1, 1, 42),
('110105043', '首都机场街道', '首都机场', 'shoudujichang', 3, 1, 1, 43);

-- 插入建外街道村级数据
INSERT INTO villages (code, name, short_name, pinyin, town_id, county_id, city_id, province_id, sort_order) VALUES
('110105001001', '建国门外社区', '建国门外', 'jianguomenwai', 1, 3, 1, 1, 1),
('110105001002', '永安里社区', '永安里', 'yonganli', 1, 3, 1, 1, 2),
('110105001003', '光华里社区', '光华里', 'guanghuali', 1, 3, 1, 1, 3),
('110105001004', '秀水社区', '秀水', 'xiushui', 1, 3, 1, 1, 4),
('110105001005', '北郎社区', '北郎', 'beilang', 1, 3, 1, 1, 5),
('110105001006', '南郎社区', '南郎', 'nanlang', 1, 3, 1, 1, 6),
('110105001007', '建外SOHO社区', '建外SOHO', 'jianwaisoho', 1, 3, 1, 1, 7),
('110105001008', '国贸社区', '国贸', 'guomao', 1, 3, 1, 1, 8),
('110105001009', '建外大街社区', '建外大街', 'jianwaidajie', 1, 3, 1, 1, 9),
('110105001010', '永安里东社区', '永安里东', 'yonganlidong', 1, 3, 1, 1, 10);

-- 插入上海市数据
INSERT INTO cities (code, name, short_name, pinyin, province_id, sort_order) VALUES
('310100', '上海市', '沪', 'shanghai', 9, 1);

-- 插入上海市区县数据
INSERT INTO counties (code, name, short_name, pinyin, city_id, province_id, sort_order) VALUES
('310101', '黄浦区', '黄浦', 'huangpu', 2, 9, 1),
('310104', '徐汇区', '徐汇', 'xuhui', 2, 9, 2),
('310105', '长宁区', '长宁', 'changning', 2, 9, 3),
('310106', '静安区', '静安', 'jingan', 2, 9, 4),
('310107', '普陀区', '普陀', 'putuo', 2, 9, 5),
('310109', '虹口区', '虹口', 'hongkou', 2, 9, 6),
('310110', '杨浦区', '杨浦', 'yangpu', 2, 9, 7),
('310112', '闵行区', '闵行', 'minhang', 2, 9, 8),
('310113', '宝山区', '宝山', 'baoshan', 2, 9, 9),
('310114', '嘉定区', '嘉定', 'jiading', 2, 9, 10),
('310115', '浦东新区', '浦东', 'pudong', 2, 9, 11),
('310116', '金山区', '金山', 'jinshan', 2, 9, 12),
('310117', '松江区', '松江', 'songjiang', 2, 9, 13),
('310118', '青浦区', '青浦', 'qingpu', 2, 9, 14),
('310120', '奉贤区', '奉贤', 'fengxian', 2, 9, 15),
('310151', '崇明区', '崇明', 'chongming', 2, 9, 16);

-- 创建索引优化查询性能
CREATE INDEX idx_provinces_name_pinyin ON provinces(name, pinyin);
CREATE INDEX idx_cities_name_pinyin ON cities(name, pinyin);
CREATE INDEX idx_counties_name_pinyin ON counties(name, pinyin);
CREATE INDEX idx_towns_name_pinyin ON towns(name, pinyin);
CREATE INDEX idx_villages_name_pinyin ON villages(name, pinyin);

-- 显示创建结果
SELECT 'Administrative query system database initialization completed successfully!' as message;
SELECT COUNT(*) as province_count FROM provinces;
SELECT COUNT(*) as city_count FROM cities;
SELECT COUNT(*) as county_count FROM counties;
SELECT COUNT(*) as town_count FROM towns;
SELECT COUNT(*) as village_count FROM villages;