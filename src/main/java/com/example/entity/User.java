package com.example.entity;

import java.util.List;

/**
 * 用户实体类
 * 包含JSON字段存储ID列表
 */
public class User {
    private Long id;
    private String name;
    private String email;
    private List<Long> roleIds; // JSON字段存储的角色ID列表
    
    public User() {}
    
    public User(Long id, String name, String email, List<Long> roleIds) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.roleIds = roleIds;
    }
    
    // Getters and Setters
    public Long getId() {
        return id;
    }
    
    public void setId(Long id) {
        this.id = id;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public List<Long> getRoleIds() {
        return roleIds;
    }
    
    public void setRoleIds(List<Long> roleIds) {
        this.roleIds = roleIds;
    }
    
    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", email='" + email + '\'' +
                ", roleIds=" + roleIds +
                '}';
    }
}