package com.example.category.service;

import com.example.category.model.Category;
import com.example.category.repository.CategoryRepository;
import com.example.category.repository.impl.InMemoryCategoryRepository;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 分类服务类 - 提供分类的增删改查和树形结构操作
 * Category service class - provides CRUD operations and tree structure operations
 */
@Service
public class CategoryService {
    
    private final CategoryRepository categoryRepository;
    
    public CategoryService() {
        this.categoryRepository = new InMemoryCategoryRepository();
    }
    
    public CategoryService(CategoryRepository categoryRepository) {
        this.categoryRepository = categoryRepository;
    }
    
    /**
     * 创建分类
     * Create category
     */
    public Category createCategory(Category category) {
        validateCategory(category);
        
        // 设置层级和路径
        setCategoryLevelAndPath(category);
        
        // 设置排序顺序
        if (category.getSortOrder() == null) {
            long nextSortOrder = categoryRepository.countByParentId(category.getParentId()) + 1;
            category.setSortOrder((int) nextSortOrder);
        }
        
        return categoryRepository.save(category);
    }
    
    /**
     * 根据ID获取分类
     * Get category by ID
     */
    public Optional<Category> getCategoryById(Long id) {
        return categoryRepository.findById(id);
    }
    
    /**
     * 获取所有分类
     * Get all categories
     */
    public List<Category> getAllCategories() {
        return categoryRepository.findAll();
    }
    
    /**
     * 获取所有激活的分类
     * Get all active categories
     */
    public List<Category> getAllActiveCategories() {
        return categoryRepository.findByIsActiveTrue();
    }
    
    /**
     * 根据父ID获取子分类
     * Get child categories by parent ID
     */
    public List<Category> getChildCategories(Long parentId) {
        return categoryRepository.findByParentIdAndIsActiveTrue(parentId);
    }
    
    /**
     * 获取根分类
     * Get root categories
     */
    public List<Category> getRootCategories() {
        return categoryRepository.findRootCategories().stream()
                .filter(category -> Boolean.TRUE.equals(category.getIsActive()))
                .collect(Collectors.toList());
    }
    
    /**
     * 根据名称搜索分类
     * Search categories by name
     */
    public List<Category> searchCategoriesByName(String name) {
        return categoryRepository.findByNameContaining(name);
    }
    
    /**
     * 根据层级获取分类
     * Get categories by level
     */
    public List<Category> getCategoriesByLevel(Integer level) {
        return categoryRepository.findByLevel(level);
    }
    
    /**
     * 更新分类
     * Update category
     */
    public Category updateCategory(Category category) {
        if (category.getId() == null) {
            throw new IllegalArgumentException("Category ID cannot be null for update");
        }
        
        Optional<Category> existingCategory = categoryRepository.findById(category.getId());
        if (existingCategory.isEmpty()) {
            throw new IllegalArgumentException("Category not found with id: " + category.getId());
        }
        
        validateCategory(category);
        
        // 如果父分类发生变化，重新计算层级和路径
        Category existing = existingCategory.get();
        if (!Objects.equals(existing.getParentId(), category.getParentId())) {
            setCategoryLevelAndPath(category);
        }
        
        return categoryRepository.update(category);
    }
    
    /**
     * 删除分类
     * Delete category
     */
    public void deleteCategory(Long id) {
        // 检查是否有子分类
        long childCount = categoryRepository.countByParentId(id);
        if (childCount > 0) {
            throw new IllegalStateException("Cannot delete category with child categories. Please delete child categories first.");
        }
        
        categoryRepository.deleteById(id);
    }
    
    /**
     * 软删除分类（设置为非激活状态）
     * Soft delete category (set as inactive)
     */
    public void softDeleteCategory(Long id) {
        Optional<Category> category = categoryRepository.findById(id);
        if (category.isPresent()) {
            Category cat = category.get();
            cat.setIsActive(false);
            categoryRepository.update(cat);
        }
    }
    
    /**
     * 获取分类树（所有分类的树形结构）
     * Get category tree (tree structure of all categories)
     */
    public List<Category> getCategoryTree() {
        List<Category> allCategories = categoryRepository.findByIsActiveTrue();
        return buildCategoryTree(allCategories, null);
    }
    
    /**
     * 获取指定分类的子树
     * Get subtree of specified category
     */
    public List<Category> getCategorySubtree(Long parentId) {
        List<Category> allCategories = categoryRepository.findByIsActiveTrue();
        return buildCategoryTree(allCategories, parentId);
    }
    
    /**
     * 获取分类的完整路径
     * Get full path of category
     */
    public List<Category> getCategoryPath(Long categoryId) {
        List<Category> path = new ArrayList<>();
        Optional<Category> category = categoryRepository.findById(categoryId);
        
        while (category.isPresent()) {
            path.add(0, category.get()); // 添加到列表开头
            category = category.get().getParentId() != null ? 
                    categoryRepository.findById(category.get().getParentId()) : 
                    Optional.empty();
        }
        
        return path;
    }
    
    /**
     * 移动分类到新的父分类下
     * Move category to new parent
     */
    public Category moveCategory(Long categoryId, Long newParentId) {
        Optional<Category> category = categoryRepository.findById(categoryId);
        if (category.isEmpty()) {
            throw new IllegalArgumentException("Category not found with id: " + categoryId);
        }
        
        // 检查新父分类是否存在
        if (newParentId != null) {
            Optional<Category> newParent = categoryRepository.findById(newParentId);
            if (newParent.isEmpty()) {
                throw new IllegalArgumentException("New parent category not found with id: " + newParentId);
            }
            
            // 检查是否会形成循环引用
            if (wouldCreateCircularReference(categoryId, newParentId)) {
                throw new IllegalArgumentException("Cannot move category: would create circular reference");
            }
        }
        
        Category cat = category.get();
        cat.setParentId(newParentId);
        setCategoryLevelAndPath(cat);
        
        return categoryRepository.update(cat);
    }
    
    /**
     * 构建分类树
     * Build category tree
     */
    private List<Category> buildCategoryTree(List<Category> allCategories, Long rootParentId) {
        Map<Long, List<Category>> categoryMap = allCategories.stream()
                .collect(Collectors.groupingBy(category -> 
                        category.getParentId() != null ? category.getParentId() : 0L));
        
        List<Category> rootCategories = categoryMap.getOrDefault(rootParentId, new ArrayList<>());
        
        for (Category category : rootCategories) {
            buildChildren(category, categoryMap);
        }
        
        return rootCategories;
    }
    
    /**
     * 递归构建子分类
     * Recursively build child categories
     */
    private void buildChildren(Category parent, Map<Long, List<Category>> categoryMap) {
        List<Category> children = categoryMap.getOrDefault(parent.getId(), new ArrayList<>());
        parent.setChildren(children);
        
        for (Category child : children) {
            buildChildren(child, categoryMap);
        }
    }
    
    /**
     * 设置分类的层级和路径
     * Set category level and path
     */
    private void setCategoryLevelAndPath(Category category) {
        if (category.getParentId() == null || category.getParentId() == 0) {
            // 根分类
            category.setLevel(1);
            category.setPath("/");
        } else {
            Optional<Category> parent = categoryRepository.findById(category.getParentId());
            if (parent.isPresent()) {
                category.setLevel(parent.get().getLevel() + 1);
                category.setPath(parent.get().getPath() + parent.get().getId() + "/");
            } else {
                throw new IllegalArgumentException("Parent category not found with id: " + category.getParentId());
            }
        }
    }
    
    /**
     * 验证分类数据
     * Validate category data
     */
    private void validateCategory(Category category) {
        if (category.getName() == null || category.getName().trim().isEmpty()) {
            throw new IllegalArgumentException("Category name cannot be empty");
        }
        
        if (category.getName().length() > 100) {
            throw new IllegalArgumentException("Category name cannot exceed 100 characters");
        }
    }
    
    /**
     * 检查是否会形成循环引用
     * Check if moving would create circular reference
     */
    private boolean wouldCreateCircularReference(Long categoryId, Long newParentId) {
        if (categoryId.equals(newParentId)) {
            return true;
        }
        
        Optional<Category> parent = categoryRepository.findById(newParentId);
        while (parent.isPresent()) {
            if (parent.get().getId().equals(categoryId)) {
                return true;
            }
            parent = parent.get().getParentId() != null ? 
                    categoryRepository.findById(parent.get().getParentId()) : 
                    Optional.empty();
        }
        
        return false;
    }
}