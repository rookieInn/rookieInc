package com.example;

import com.example.config.MyBatisConfig;
import com.example.entity.User;
import com.example.mapper.UserMapper;
import com.example.service.UserService;
import org.apache.ibatis.session.SqlSession;
import org.apache.ibatis.session.SqlSessionFactory;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Arrays;
import java.util.List;

/**
 * MyBatis JSON字段查询示例
 * 演示如何判断某个ID是否在数据库JSON字段中
 */
public class MyBatisJsonExample {
    
    private static final Logger logger = LoggerFactory.getLogger(MyBatisJsonExample.class);
    
    public static void main(String[] args) {
        SqlSessionFactory sqlSessionFactory = MyBatisConfig.getSqlSessionFactory();
        
        try (SqlSession sqlSession = sqlSessionFactory.openSession()) {
            UserMapper userMapper = sqlSession.getMapper(UserMapper.class);
            UserService userService = new UserService(userMapper);
            
            logger.info("=== MyBatis JSON字段查询示例 ===");
            
            // 1. 创建测试数据
            createTestData(userService);
            
            // 2. 演示各种JSON字段查询方法
            demonstrateJsonQueries(userService);
            
            // 3. 演示角色管理操作
            demonstrateRoleManagement(userService);
            
        } catch (Exception e) {
            logger.error("执行示例时发生错误", e);
        }
    }
    
    /**
     * 创建测试数据
     */
    private static void createTestData(UserService userService) {
        logger.info("\n=== 创建测试数据 ===");
        
        // 创建用户1：拥有角色1,2,3
        User user1 = new User();
        user1.setName("张三");
        user1.setEmail("zhangsan@example.com");
        user1.setRoleIds(Arrays.asList(1L, 2L, 3L));
        userService.createUser(user1);
        
        // 创建用户2：拥有角色2,4,5
        User user2 = new User();
        user2.setName("李四");
        user2.setEmail("lisi@example.com");
        user2.setRoleIds(Arrays.asList(2L, 4L, 5L));
        userService.createUser(user2);
        
        // 创建用户3：拥有角色1,5
        User user3 = new User();
        user3.setName("王五");
        user3.setEmail("wangwu@example.com");
        user3.setRoleIds(Arrays.asList(1L, 5L));
        userService.createUser(user3);
        
        logger.info("测试数据创建完成");
    }
    
    /**
     * 演示各种JSON字段查询方法
     */
    private static void demonstrateJsonQueries(UserService userService) {
        logger.info("\n=== 演示JSON字段查询方法 ===");
        
        // 1. 检查用户是否拥有指定角色
        logger.info("\n1. 检查用户是否拥有指定角色:");
        boolean hasRole1 = userService.hasRole(1L, 2L); // 张三是否拥有角色2
        boolean hasRole2 = userService.hasRole(1L, 4L); // 张三是否拥有角色4
        logger.info("张三拥有角色2: {}", hasRole1);
        logger.info("张三拥有角色4: {}", hasRole2);
        
        // 2. 查询拥有指定角色的所有用户
        logger.info("\n2. 查询拥有指定角色的所有用户:");
        List<User> usersWithRole2 = userService.getUsersByRole(2L);
        logger.info("拥有角色2的用户: {}", usersWithRole2);
        
        List<User> usersWithRole5 = userService.getUsersByRole(5L);
        logger.info("拥有角色5的用户: {}", usersWithRole5);
        
        // 3. 查询拥有任意指定角色的用户
        logger.info("\n3. 查询拥有任意指定角色的用户:");
        List<User> usersWithAnyRole = userService.getUsersByAnyRole(Arrays.asList(1L, 4L));
        logger.info("拥有角色1或4的用户: {}", usersWithAnyRole);
        
        // 4. 查询拥有所有指定角色的用户
        logger.info("\n4. 查询拥有所有指定角色的用户:");
        List<User> usersWithAllRoles = userService.getUsersByAllRoles(Arrays.asList(1L, 5L));
        logger.info("同时拥有角色1和5的用户: {}", usersWithAllRoles);
        
        // 5. 统计拥有指定角色的用户数量
        logger.info("\n5. 统计拥有指定角色的用户数量:");
        int count1 = userService.countUsersByRole(1L);
        int count2 = userService.countUsersByRole(2L);
        int count6 = userService.countUsersByRole(6L);
        logger.info("拥有角色1的用户数量: {}", count1);
        logger.info("拥有角色2的用户数量: {}", count2);
        logger.info("拥有角色6的用户数量: {}", count6);
    }
    
    /**
     * 演示角色管理操作
     */
    private static void demonstrateRoleManagement(UserService userService) {
        logger.info("\n=== 演示角色管理操作 ===");
        
        // 1. 为用户添加角色
        logger.info("\n1. 为用户添加角色:");
        boolean addResult1 = userService.addRoleToUser(1L, 6L); // 为张三添加角色6
        boolean addResult2 = userService.addRoleToUser(1L, 2L); // 为张三添加已存在的角色2
        logger.info("为张三添加角色6: {}", addResult1);
        logger.info("为张三添加已存在的角色2: {}", addResult2);
        
        // 2. 从用户移除角色
        logger.info("\n2. 从用户移除角色:");
        boolean removeResult1 = userService.removeRoleFromUser(1L, 3L); // 从张三移除角色3
        boolean removeResult2 = userService.removeRoleFromUser(1L, 7L); // 从张三移除不存在的角色7
        logger.info("从张三移除角色3: {}", removeResult1);
        logger.info("从张三移除不存在的角色7: {}", removeResult2);
        
        // 3. 更新用户的所有角色
        logger.info("\n3. 更新用户的所有角色:");
        boolean updateResult = userService.updateUserRoles(2L, Arrays.asList(1L, 3L, 6L));
        logger.info("更新李四的角色为[1,3,6]: {}", updateResult);
        
        // 4. 验证更新结果
        logger.info("\n4. 验证更新结果:");
        boolean hasNewRole = userService.hasRole(2L, 6L);
        boolean hasOldRole = userService.hasRole(2L, 4L);
        logger.info("李四现在拥有角色6: {}", hasNewRole);
        logger.info("李四现在拥有角色4: {}", hasOldRole);
    }
}