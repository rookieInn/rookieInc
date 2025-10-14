package com.example.mybatisplus.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.mybatisplus.entity.User;
import com.example.mybatisplus.mapper.UserMapper;
import com.example.mybatisplus.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;

import java.util.List;

/**
 * 用户服务实现类
 * 
 * @author Generated
 * @since 2024-01-01
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {

    @Autowired
    private UserMapper userMapper;

    @Override
    public User getByUsername(String username) {
        if (!StringUtils.hasText(username)) {
            return null;
        }
        return userMapper.selectByUsername(username);
    }

    @Override
    public User getByEmail(String email) {
        if (!StringUtils.hasText(email)) {
            return null;
        }
        return userMapper.selectByEmail(email);
    }

    @Override
    public User getByPhone(String phone) {
        if (!StringUtils.hasText(phone)) {
            return null;
        }
        return userMapper.selectByPhone(phone);
    }

    @Override
    public IPage<User> getUserPage(Page<User> page, String username, String realName, Integer status) {
        return userMapper.selectUserPage(page, username, realName, status);
    }

    @Override
    public List<User> getByStatus(Integer status) {
        return userMapper.selectByStatus(status);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean createUser(User user) {
        if (user == null) {
            return false;
        }
        
        // 检查用户名是否已存在
        if (isUsernameExists(user.getUsername(), null)) {
            throw new RuntimeException("用户名已存在");
        }
        
        // 检查邮箱是否已存在
        if (StringUtils.hasText(user.getEmail()) && isEmailExists(user.getEmail(), null)) {
            throw new RuntimeException("邮箱已存在");
        }
        
        // 检查手机号是否已存在
        if (StringUtils.hasText(user.getPhone()) && isPhoneExists(user.getPhone(), null)) {
            throw new RuntimeException("手机号已存在");
        }
        
        // 设置默认值
        if (user.getStatus() == null) {
            user.setStatus(1); // 默认启用
        }
        if (user.getDeleted() == null) {
            user.setDeleted(0); // 默认未删除
        }
        if (user.getVersion() == null) {
            user.setVersion(1); // 默认版本号
        }
        
        return save(user);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateUser(User user) {
        if (user == null || user.getId() == null) {
            return false;
        }
        
        // 检查用户是否存在
        User existUser = getById(user.getId());
        if (existUser == null) {
            throw new RuntimeException("用户不存在");
        }
        
        // 检查用户名是否已存在（排除当前用户）
        if (StringUtils.hasText(user.getUsername()) && isUsernameExists(user.getUsername(), user.getId())) {
            throw new RuntimeException("用户名已存在");
        }
        
        // 检查邮箱是否已存在（排除当前用户）
        if (StringUtils.hasText(user.getEmail()) && isEmailExists(user.getEmail(), user.getId())) {
            throw new RuntimeException("邮箱已存在");
        }
        
        // 检查手机号是否已存在（排除当前用户）
        if (StringUtils.hasText(user.getPhone()) && isPhoneExists(user.getPhone(), user.getId())) {
            throw new RuntimeException("手机号已存在");
        }
        
        return updateById(user);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteUser(Long id) {
        if (id == null) {
            return false;
        }
        
        User user = getById(id);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        
        return removeById(id);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteUsers(List<Long> ids) {
        if (ids == null || ids.isEmpty()) {
            return false;
        }
        
        // 检查所有用户是否存在
        List<User> users = listByIds(ids);
        if (users.size() != ids.size()) {
            throw new RuntimeException("部分用户不存在");
        }
        
        return removeByIds(ids);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateStatusBatch(List<Long> ids, Integer status) {
        if (ids == null || ids.isEmpty() || status == null) {
            return false;
        }
        
        // 检查所有用户是否存在
        List<User> users = listByIds(ids);
        if (users.size() != ids.size()) {
            throw new RuntimeException("部分用户不存在");
        }
        
        int result = userMapper.updateStatusBatch(ids, status);
        return result > 0;
    }

    @Override
    public boolean isUsernameExists(String username, Long excludeId) {
        if (!StringUtils.hasText(username)) {
            return false;
        }
        
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getUsername, username);
        if (excludeId != null) {
            wrapper.ne(User::getId, excludeId);
        }
        
        return count(wrapper) > 0;
    }

    @Override
    public boolean isEmailExists(String email, Long excludeId) {
        if (!StringUtils.hasText(email)) {
            return false;
        }
        
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getEmail, email);
        if (excludeId != null) {
            wrapper.ne(User::getId, excludeId);
        }
        
        return count(wrapper) > 0;
    }

    @Override
    public boolean isPhoneExists(String phone, Long excludeId) {
        if (!StringUtils.hasText(phone)) {
            return false;
        }
        
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(User::getPhone, phone);
        if (excludeId != null) {
            wrapper.ne(User::getId, excludeId);
        }
        
        return count(wrapper) > 0;
    }

    @Override
    public List<User> countByStatus() {
        return userMapper.countByStatus();
    }
}