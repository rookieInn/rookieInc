package com.example.mybatisplus.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.mybatisplus.entity.User;
import com.example.mybatisplus.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 用户控制器
 * 
 * @author Generated
 * @since 2024-01-01
 */
@RestController
@RequestMapping("/api/users")
@CrossOrigin(origins = "*")
public class UserController {

    @Autowired
    private UserService userService;

    /**
     * 分页查询用户列表
     * 
     * @param current 当前页
     * @param size 每页大小
     * @param username 用户名（模糊查询）
     * @param realName 真实姓名（模糊查询）
     * @param status 状态
     * @return 分页结果
     */
    @GetMapping("/page")
    public ResponseEntity<Map<String, Object>> getUserPage(
            @RequestParam(defaultValue = "1") Long current,
            @RequestParam(defaultValue = "10") Long size,
            @RequestParam(required = false) String username,
            @RequestParam(required = false) String realName,
            @RequestParam(required = false) Integer status) {
        
        try {
            Page<User> page = new Page<>(current, size);
            IPage<User> result = userService.getUserPage(page, username, realName, status);
            
            Map<String, Object> response = new HashMap<>();
            response.put("code", 200);
            response.put("message", "查询成功");
            response.put("data", result);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "查询失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 根据ID查询用户详情
     * 
     * @param id 用户ID
     * @return 用户详情
     */
    @GetMapping("/{id}")
    public ResponseEntity<Map<String, Object>> getUserById(@PathVariable Long id) {
        try {
            User user = userService.getById(id);
            Map<String, Object> response = new HashMap<>();
            
            if (user != null) {
                response.put("code", 200);
                response.put("message", "查询成功");
                response.put("data", user);
            } else {
                response.put("code", 404);
                response.put("message", "用户不存在");
                response.put("data", null);
            }
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "查询失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 根据用户名查询用户
     * 
     * @param username 用户名
     * @return 用户信息
     */
    @GetMapping("/username/{username}")
    public ResponseEntity<Map<String, Object>> getUserByUsername(@PathVariable String username) {
        try {
            User user = userService.getByUsername(username);
            Map<String, Object> response = new HashMap<>();
            
            if (user != null) {
                response.put("code", 200);
                response.put("message", "查询成功");
                response.put("data", user);
            } else {
                response.put("code", 404);
                response.put("message", "用户不存在");
                response.put("data", null);
            }
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "查询失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 根据状态查询用户列表
     * 
     * @param status 状态
     * @return 用户列表
     */
    @GetMapping("/status/{status}")
    public ResponseEntity<Map<String, Object>> getUsersByStatus(@PathVariable Integer status) {
        try {
            List<User> users = userService.getByStatus(status);
            Map<String, Object> response = new HashMap<>();
            response.put("code", 200);
            response.put("message", "查询成功");
            response.put("data", users);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "查询失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 创建用户
     * 
     * @param user 用户信息
     * @return 创建结果
     */
    @PostMapping
    public ResponseEntity<Map<String, Object>> createUser(@RequestBody User user) {
        try {
            boolean success = userService.createUser(user);
            Map<String, Object> response = new HashMap<>();
            
            if (success) {
                response.put("code", 200);
                response.put("message", "创建成功");
                response.put("data", user);
            } else {
                response.put("code", 500);
                response.put("message", "创建失败");
                response.put("data", null);
            }
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "创建失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 更新用户信息
     * 
     * @param id 用户ID
     * @param user 用户信息
     * @return 更新结果
     */
    @PutMapping("/{id}")
    public ResponseEntity<Map<String, Object>> updateUser(@PathVariable Long id, @RequestBody User user) {
        try {
            user.setId(id);
            boolean success = userService.updateUser(user);
            Map<String, Object> response = new HashMap<>();
            
            if (success) {
                response.put("code", 200);
                response.put("message", "更新成功");
                response.put("data", user);
            } else {
                response.put("code", 500);
                response.put("message", "更新失败");
                response.put("data", null);
            }
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "更新失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 根据ID删除用户（逻辑删除）
     * 
     * @param id 用户ID
     * @return 删除结果
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Map<String, Object>> deleteUser(@PathVariable Long id) {
        try {
            boolean success = userService.deleteUser(id);
            Map<String, Object> response = new HashMap<>();
            
            if (success) {
                response.put("code", 200);
                response.put("message", "删除成功");
                response.put("data", null);
            } else {
                response.put("code", 500);
                response.put("message", "删除失败");
                response.put("data", null);
            }
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "删除失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 批量删除用户（逻辑删除）
     * 
     * @param ids 用户ID列表
     * @return 删除结果
     */
    @DeleteMapping("/batch")
    public ResponseEntity<Map<String, Object>> deleteUsers(@RequestBody List<Long> ids) {
        try {
            boolean success = userService.deleteUsers(ids);
            Map<String, Object> response = new HashMap<>();
            
            if (success) {
                response.put("code", 200);
                response.put("message", "批量删除成功");
                response.put("data", null);
            } else {
                response.put("code", 500);
                response.put("message", "批量删除失败");
                response.put("data", null);
            }
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "批量删除失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 批量更新用户状态
     * 
     * @param request 包含用户ID列表和状态的请求对象
     * @return 更新结果
     */
    @PutMapping("/status/batch")
    public ResponseEntity<Map<String, Object>> updateStatusBatch(@RequestBody Map<String, Object> request) {
        try {
            @SuppressWarnings("unchecked")
            List<Long> ids = (List<Long>) request.get("ids");
            Integer status = (Integer) request.get("status");
            
            boolean success = userService.updateStatusBatch(ids, status);
            Map<String, Object> response = new HashMap<>();
            
            if (success) {
                response.put("code", 200);
                response.put("message", "批量更新状态成功");
                response.put("data", null);
            } else {
                response.put("code", 500);
                response.put("message", "批量更新状态失败");
                response.put("data", null);
            }
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "批量更新状态失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 检查用户名是否存在
     * 
     * @param username 用户名
     * @param excludeId 排除的用户ID（可选）
     * @return 检查结果
     */
    @GetMapping("/check/username")
    public ResponseEntity<Map<String, Object>> checkUsername(@RequestParam String username, 
                                                           @RequestParam(required = false) Long excludeId) {
        try {
            boolean exists = userService.isUsernameExists(username, excludeId);
            Map<String, Object> response = new HashMap<>();
            response.put("code", 200);
            response.put("message", "检查完成");
            response.put("data", Map.of("exists", exists));
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "检查失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 检查邮箱是否存在
     * 
     * @param email 邮箱
     * @param excludeId 排除的用户ID（可选）
     * @return 检查结果
     */
    @GetMapping("/check/email")
    public ResponseEntity<Map<String, Object>> checkEmail(@RequestParam String email, 
                                                        @RequestParam(required = false) Long excludeId) {
        try {
            boolean exists = userService.isEmailExists(email, excludeId);
            Map<String, Object> response = new HashMap<>();
            response.put("code", 200);
            response.put("message", "检查完成");
            response.put("data", Map.of("exists", exists));
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "检查失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 检查手机号是否存在
     * 
     * @param phone 手机号
     * @param excludeId 排除的用户ID（可选）
     * @return 检查结果
     */
    @GetMapping("/check/phone")
    public ResponseEntity<Map<String, Object>> checkPhone(@RequestParam String phone, 
                                                        @RequestParam(required = false) Long excludeId) {
        try {
            boolean exists = userService.isPhoneExists(phone, excludeId);
            Map<String, Object> response = new HashMap<>();
            response.put("code", 200);
            response.put("message", "检查完成");
            response.put("data", Map.of("exists", exists));
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "检查失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }

    /**
     * 统计用户数量（按状态分组）
     * 
     * @return 统计结果
     */
    @GetMapping("/statistics")
    public ResponseEntity<Map<String, Object>> getUserStatistics() {
        try {
            List<User> statistics = userService.countByStatus();
            Map<String, Object> response = new HashMap<>();
            response.put("code", 200);
            response.put("message", "统计成功");
            response.put("data", statistics);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("code", 500);
            response.put("message", "统计失败：" + e.getMessage());
            response.put("data", null);
            return ResponseEntity.ok(response);
        }
    }
}