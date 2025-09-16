package com.example.mapper;

import com.example.entity.User;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 用户Mapper接口
 * 包含判断ID是否在JSON字段中的方法
 */
public interface UserMapper {
    
    /**
     * 根据ID查询用户
     */
    User selectById(@Param("id") Long id);
    
    /**
     * 查询所有用户
     */
    List<User> selectAll();
    
    /**
     * 插入用户
     */
    int insert(User user);
    
    /**
     * 更新用户
     */
    int update(User user);
    
    /**
     * 删除用户
     */
    int deleteById(@Param("id") Long id);
    
    /**
     * 判断指定ID是否在用户的roleIds JSON字段中
     * 使用MySQL的JSON_CONTAINS函数
     */
    boolean isRoleIdInJson(@Param("userId") Long userId, @Param("roleId") Long roleId);
    
    /**
     * 查询包含指定角色ID的所有用户
     * 使用MySQL的JSON_CONTAINS函数
     */
    List<User> selectUsersByRoleId(@Param("roleId") Long roleId);
    
    /**
     * 查询roleIds JSON字段中包含任意指定ID的用户
     * 使用MySQL的JSON_OVERLAPS函数
     */
    List<User> selectUsersByAnyRoleId(@Param("roleIds") List<Long> roleIds);
    
    /**
     * 查询roleIds JSON字段中包含所有指定ID的用户
     * 使用MySQL的JSON_CONTAINS函数
     */
    List<User> selectUsersByAllRoleIds(@Param("roleIds") List<Long> roleIds);
    
    /**
     * 统计包含指定角色ID的用户数量
     */
    int countUsersByRoleId(@Param("roleId") Long roleId);
}