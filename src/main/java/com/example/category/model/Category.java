package com.example.category.model;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * 分类实体类 - 支持多级分类结构
 * Category entity class - supports multi-level category structure
 */
public class Category {
    
    private Long id;
    private String name;
    private String description;
    private Long parentId;
    private Integer level;
    private String path; // 存储从根节点到当前节点的路径，如：/1/2/3/
    private Integer sortOrder;
    private Boolean isActive;
    private LocalDateTime createTime;
    private LocalDateTime updateTime;
    
    // 用于树形结构展示的子分类列表
    private List<Category> children = new ArrayList<>();
    
    public Category() {
        this.isActive = true;
        this.createTime = LocalDateTime.now();
        this.updateTime = LocalDateTime.now();
    }
    
    public Category(String name, String description, Long parentId) {
        this();
        this.name = name;
        this.description = description;
        this.parentId = parentId;
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
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public Long getParentId() {
        return parentId;
    }
    
    public void setParentId(Long parentId) {
        this.parentId = parentId;
    }
    
    public Integer getLevel() {
        return level;
    }
    
    public void setLevel(Integer level) {
        this.level = level;
    }
    
    public String getPath() {
        return path;
    }
    
    public void setPath(String path) {
        this.path = path;
    }
    
    public Integer getSortOrder() {
        return sortOrder;
    }
    
    public void setSortOrder(Integer sortOrder) {
        this.sortOrder = sortOrder;
    }
    
    public Boolean getIsActive() {
        return isActive;
    }
    
    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
    
    public LocalDateTime getCreateTime() {
        return createTime;
    }
    
    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }
    
    public LocalDateTime getUpdateTime() {
        return updateTime;
    }
    
    public void setUpdateTime(LocalDateTime updateTime) {
        this.updateTime = updateTime;
    }
    
    public List<Category> getChildren() {
        return children;
    }
    
    public void setChildren(List<Category> children) {
        this.children = children;
    }
    
    /**
     * 添加子分类
     * Add child category
     */
    public void addChild(Category child) {
        if (children == null) {
            children = new ArrayList<>();
        }
        children.add(child);
    }
    
    /**
     * 判断是否为根分类
     * Check if this is a root category
     */
    public boolean isRoot() {
        return parentId == null || parentId == 0;
    }
    
    /**
     * 判断是否为叶子节点
     * Check if this is a leaf node
     */
    public boolean isLeaf() {
        return children == null || children.isEmpty();
    }
    
    /**
     * 获取分类的完整路径名称
     * Get full path name of the category
     */
    public String getFullPathName() {
        if (path == null || path.isEmpty()) {
            return name;
        }
        return path + name;
    }
    
    @Override
    public String toString() {
        return "Category{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", parentId=" + parentId +
                ", level=" + level +
                ", path='" + path + '\'' +
                ", isActive=" + isActive +
                '}';
    }
}