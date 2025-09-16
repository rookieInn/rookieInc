package com.example.service;

import com.example.entity.User;
import com.example.mapper.UserMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

/**
 * 用户服务类
 * 演示如何判断ID是否在JSON字段中
 */
public class UserService {
    
    private static final Logger logger = LoggerFactory.getLogger(UserService.class);
    
    private final UserMapper userMapper;
    
    public UserService(UserMapper userMapper) {
        this.userMapper = userMapper;
    }
    
    /**
     * 检查用户是否拥有指定角色
     * @param userId 用户ID
     * @param roleId 角色ID
     * @return 是否拥有该角色
     */
    public boolean hasRole(Long userId, Long roleId) {
        logger.info("检查用户 {} 是否拥有角色 {}", userId, roleId);
        boolean hasRole = userMapper.isRoleIdInJson(userId, roleId);
        logger.info("用户 {} 拥有角色 {}: {}", userId, roleId, hasRole);
        return hasRole;
    }
    
    /**
     * 获取拥有指定角色的所有用户
     * @param roleId 角色ID
     * @return 用户列表
     */
    public List<User> getUsersByRole(Long roleId) {
        logger.info("查询拥有角色 {} 的所有用户", roleId);
        List<User> users = userMapper.selectUsersByRoleId(roleId);
        logger.info("找到 {} 个拥有角色 {} 的用户", users.size(), roleId);
        return users;
    }
    
    /**
     * 获取拥有任意指定角色的用户
     * @param roleIds 角色ID列表
     * @return 用户列表
     */
    public List<User> getUsersByAnyRole(List<Long> roleIds) {
        logger.info("查询拥有任意角色 {} 的用户", roleIds);
        List<User> users = userMapper.selectUsersByAnyRoleId(roleIds);
        logger.info("找到 {} 个拥有任意指定角色的用户", users.size());
        return users;
    }
    
    /**
     * 获取拥有所有指定角色的用户
     * @param roleIds 角色ID列表
     * @return 用户列表
     */
    public List<User> getUsersByAllRoles(List<Long> roleIds) {
        logger.info("查询拥有所有角色 {} 的用户", roleIds);
        List<User> users = userMapper.selectUsersByAllRoleIds(roleIds);
        logger.info("找到 {} 个拥有所有指定角色的用户", users.size());
        return users;
    }
    
    /**
     * 统计拥有指定角色的用户数量
     * @param roleId 角色ID
     * @return 用户数量
     */
    public int countUsersByRole(Long roleId) {
        logger.info("统计拥有角色 {} 的用户数量", roleId);
        int count = userMapper.countUsersByRoleId(roleId);
        logger.info("拥有角色 {} 的用户数量: {}", roleId, count);
        return count;
    }
    
    /**
     * 创建用户
     * @param user 用户信息
     * @return 是否创建成功
     */
    public boolean createUser(User user) {
        logger.info("创建用户: {}", user);
        int result = userMapper.insert(user);
        boolean success = result > 0;
        logger.info("用户创建{}: {}", success ? "成功" : "失败", user.getName());
        return success;
    }
    
    /**
     * 更新用户角色
     * @param userId 用户ID
     * @param roleIds 新的角色ID列表
     * @return 是否更新成功
     */
    public boolean updateUserRoles(Long userId, List<Long> roleIds) {
        logger.info("更新用户 {} 的角色为: {}", userId, roleIds);
        User user = userMapper.selectById(userId);
        if (user == null) {
            logger.warn("用户 {} 不存在", userId);
            return false;
        }
        user.setRoleIds(roleIds);
        int result = userMapper.update(user);
        boolean success = result > 0;
        logger.info("用户 {} 角色更新{}", userId, success ? "成功" : "失败");
        return success;
    }
    
    /**
     * 为用户添加角色
     * @param userId 用户ID
     * @param roleId 要添加的角色ID
     * @return 是否添加成功
     */
    public boolean addRoleToUser(Long userId, Long roleId) {
        logger.info("为用户 {} 添加角色 {}", userId, roleId);
        User user = userMapper.selectById(userId);
        if (user == null) {
            logger.warn("用户 {} 不存在", userId);
            return false;
        }
        
        List<Long> roleIds = user.getRoleIds();
        if (roleIds == null) {
            roleIds = new java.util.ArrayList<>();
        }
        
        if (!roleIds.contains(roleId)) {
            roleIds.add(roleId);
            user.setRoleIds(roleIds);
            int result = userMapper.update(user);
            boolean success = result > 0;
            logger.info("为用户 {} 添加角色 {} {}", userId, roleId, success ? "成功" : "失败");
            return success;
        } else {
            logger.info("用户 {} 已经拥有角色 {}", userId, roleId);
            return true;
        }
    }
    
    /**
     * 从用户移除角色
     * @param userId 用户ID
     * @param roleId 要移除的角色ID
     * @return 是否移除成功
     */
    public boolean removeRoleFromUser(Long userId, Long roleId) {
        logger.info("从用户 {} 移除角色 {}", userId, roleId);
        User user = userMapper.selectById(userId);
        if (user == null) {
            logger.warn("用户 {} 不存在", userId);
            return false;
        }
        
        List<Long> roleIds = user.getRoleIds();
        if (roleIds != null && roleIds.contains(roleId)) {
            roleIds.remove(roleId);
            user.setRoleIds(roleIds);
            int result = userMapper.update(user);
            boolean success = result > 0;
            logger.info("从用户 {} 移除角色 {} {}", userId, roleId, success ? "成功" : "失败");
            return success;
        } else {
            logger.info("用户 {} 不拥有角色 {}", userId, roleId);
            return true;
        }
    }
}