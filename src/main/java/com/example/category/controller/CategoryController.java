package com.example.category.controller;

import com.example.category.model.Category;
import com.example.category.service.CategoryService;

import java.util.List;
import java.util.Optional;

/**
 * 分类控制器 - 提供REST API接口
 * Category controller - provides REST API endpoints
 */
public class CategoryController {
    
    private final CategoryService categoryService;
    
    public CategoryController() {
        this.categoryService = new CategoryService();
    }
    
    public CategoryController(CategoryService categoryService) {
        this.categoryService = categoryService;
    }
    
    /**
     * 创建分类
     * Create category
     * POST /api/categories
     */
    public Category createCategory(Category category) {
        return categoryService.createCategory(category);
    }
    
    /**
     * 根据ID获取分类
     * Get category by ID
     * GET /api/categories/{id}
     */
    public Optional<Category> getCategoryById(Long id) {
        return categoryService.getCategoryById(id);
    }
    
    /**
     * 获取所有分类
     * Get all categories
     * GET /api/categories
     */
    public List<Category> getAllCategories() {
        return categoryService.getAllCategories();
    }
    
    /**
     * 获取所有激活的分类
     * Get all active categories
     * GET /api/categories/active
     */
    public List<Category> getAllActiveCategories() {
        return categoryService.getAllActiveCategories();
    }
    
    /**
     * 获取根分类
     * Get root categories
     * GET /api/categories/root
     */
    public List<Category> getRootCategories() {
        return categoryService.getRootCategories();
    }
    
    /**
     * 根据父ID获取子分类
     * Get child categories by parent ID
     * GET /api/categories/parent/{parentId}
     */
    public List<Category> getChildCategories(Long parentId) {
        return categoryService.getChildCategories(parentId);
    }
    
    /**
     * 获取分类树
     * Get category tree
     * GET /api/categories/tree
     */
    public List<Category> getCategoryTree() {
        return categoryService.getCategoryTree();
    }
    
    /**
     * 获取指定分类的子树
     * Get subtree of specified category
     * GET /api/categories/{id}/subtree
     */
    public List<Category> getCategorySubtree(Long id) {
        return categoryService.getCategorySubtree(id);
    }
    
    /**
     * 获取分类的完整路径
     * Get full path of category
     * GET /api/categories/{id}/path
     */
    public List<Category> getCategoryPath(Long id) {
        return categoryService.getCategoryPath(id);
    }
    
    /**
     * 根据名称搜索分类
     * Search categories by name
     * GET /api/categories/search?name={name}
     */
    public List<Category> searchCategoriesByName(String name) {
        return categoryService.searchCategoriesByName(name);
    }
    
    /**
     * 根据层级获取分类
     * Get categories by level
     * GET /api/categories/level/{level}
     */
    public List<Category> getCategoriesByLevel(Integer level) {
        return categoryService.getCategoriesByLevel(level);
    }
    
    /**
     * 更新分类
     * Update category
     * PUT /api/categories/{id}
     */
    public Category updateCategory(Long id, Category category) {
        category.setId(id);
        return categoryService.updateCategory(category);
    }
    
    /**
     * 移动分类到新的父分类下
     * Move category to new parent
     * PUT /api/categories/{id}/move?parentId={parentId}
     */
    public Category moveCategory(Long id, Long parentId) {
        return categoryService.moveCategory(id, parentId);
    }
    
    /**
     * 删除分类
     * Delete category
     * DELETE /api/categories/{id}
     */
    public void deleteCategory(Long id) {
        categoryService.deleteCategory(id);
    }
    
    /**
     * 软删除分类
     * Soft delete category
     * DELETE /api/categories/{id}/soft
     */
    public void softDeleteCategory(Long id) {
        categoryService.softDeleteCategory(id);
    }
}