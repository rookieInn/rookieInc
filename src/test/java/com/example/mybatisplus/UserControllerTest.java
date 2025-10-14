package com.example.mybatisplus;

import com.example.mybatisplus.entity.User;
import com.example.mybatisplus.service.UserService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.ActiveProfiles;

import java.util.List;

/**
 * 用户服务测试类
 * 
 * @author Generated
 * @since 2024-01-01
 */
@SpringBootTest
@ActiveProfiles("test")
public class UserControllerTest {

    @Autowired
    private UserService userService;

    @Test
    public void testCreateUser() {
        User user = new User();
        user.setUsername("testuser");
        user.setPassword("test123");
        user.setEmail("test@example.com");
        user.setPhone("13800138000");
        user.setRealName("测试用户");
        user.setAge(25);
        user.setGender(1);
        user.setStatus(1);

        boolean result = userService.createUser(user);
        System.out.println("创建用户结果：" + result);
        System.out.println("用户ID：" + user.getId());
    }

    @Test
    public void testGetUserById() {
        User user = userService.getById(1L);
        System.out.println("查询用户：" + user);
    }

    @Test
    public void testGetUserByUsername() {
        User user = userService.getByUsername("admin");
        System.out.println("根据用户名查询：" + user);
    }

    @Test
    public void testGetUsersByStatus() {
        List<User> users = userService.getByStatus(1);
        System.out.println("根据状态查询用户数量：" + users.size());
        users.forEach(System.out::println);
    }

    @Test
    public void testUpdateUser() {
        User user = userService.getById(1L);
        if (user != null) {
            user.setRealName("更新后的姓名");
            boolean result = userService.updateUser(user);
            System.out.println("更新用户结果：" + result);
        }
    }

    @Test
    public void testDeleteUser() {
        boolean result = userService.deleteUser(10L);
        System.out.println("删除用户结果：" + result);
    }

    @Test
    public void testCheckUsernameExists() {
        boolean exists = userService.isUsernameExists("admin", null);
        System.out.println("用户名admin是否存在：" + exists);
    }

    @Test
    public void testGetUserStatistics() {
        List<User> statistics = userService.countByStatus();
        System.out.println("用户统计：" + statistics);
    }
}