package com.example.category.entity;

import javax.persistence.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * 分类JPA实体类 - 用于数据库持久化
 * Category JPA entity class - for database persistence
 */
@Entity
@Table(name = "categories")
public class CategoryEntity {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "name", nullable = false, length = 100)
    private String name;
    
    @Column(name = "description", length = 500)
    private String description;
    
    @Column(name = "parent_id")
    private Long parentId;
    
    @Column(name = "level")
    private Integer level;
    
    @Column(name = "path", length = 500)
    private String path;
    
    @Column(name = "sort_order")
    private Integer sortOrder;
    
    @Column(name = "is_active")
    private Boolean isActive;
    
    @Column(name = "create_time")
    private LocalDateTime createTime;
    
    @Column(name = "update_time")
    private LocalDateTime updateTime;
    
    // 用于树形结构展示的子分类列表（不持久化到数据库）
    @Transient
    private List<CategoryEntity> children = new ArrayList<>();
    
    public CategoryEntity() {
        this.isActive = true;
        this.createTime = LocalDateTime.now();
        this.updateTime = LocalDateTime.now();
    }
    
    public CategoryEntity(String name, String description, Long parentId) {
        this();
        this.name = name;
        this.description = description;
        this.parentId = parentId;
    }
    
    @PrePersist
    protected void onCreate() {
        createTime = LocalDateTime.now();
        updateTime = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updateTime = LocalDateTime.now();
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
    
    public List<CategoryEntity> getChildren() {
        return children;
    }
    
    public void setChildren(List<CategoryEntity> children) {
        this.children = children;
    }
    
    /**
     * 添加子分类
     * Add child category
     */
    public void addChild(CategoryEntity child) {
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
        return "CategoryEntity{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", parentId=" + parentId +
                ", level=" + level +
                ", path='" + path + '\'' +
                ", isActive=" + isActive +
                '}';
    }
}