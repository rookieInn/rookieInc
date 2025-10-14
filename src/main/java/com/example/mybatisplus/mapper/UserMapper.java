package com.example.mybatisplus.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.mybatisplus.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

/**
 * 用户Mapper接口
 * 
 * @author Generated
 * @since 2024-01-01
 */
@Mapper
public interface UserMapper extends BaseMapper<User> {

    /**
     * 根据用户名查询用户
     * 
     * @param username 用户名
     * @return 用户信息
     */
    User selectByUsername(@Param("username") String username);

    /**
     * 根据邮箱查询用户
     * 
     * @param email 邮箱
     * @return 用户信息
     */
    User selectByEmail(@Param("email") String email);

    /**
     * 根据手机号查询用户
     * 
     * @param phone 手机号
     * @return 用户信息
     */
    User selectByPhone(@Param("phone") String phone);

    /**
     * 分页查询用户列表（带条件）
     * 
     * @param page 分页对象
     * @param username 用户名（模糊查询）
     * @param realName 真实姓名（模糊查询）
     * @param status 状态
     * @return 用户分页列表
     */
    IPage<User> selectUserPage(Page<User> page, 
                              @Param("username") String username,
                              @Param("realName") String realName,
                              @Param("status") Integer status);

    /**
     * 根据状态查询用户列表
     * 
     * @param status 状态
     * @return 用户列表
     */
    List<User> selectByStatus(@Param("status") Integer status);

    /**
     * 批量更新用户状态
     * 
     * @param ids 用户ID列表
     * @param status 状态
     * @return 更新记录数
     */
    int updateStatusBatch(@Param("ids") List<Long> ids, @Param("status") Integer status);

    /**
     * 统计用户数量（按状态分组）
     * 
     * @return 统计结果
     */
    List<User> countByStatus();
}