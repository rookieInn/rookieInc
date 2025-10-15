package com.example.category.controller;

import com.example.category.model.Category;
import com.example.category.service.CategoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

/**
 * 分类REST控制器 - Spring Boot版本
 * Category REST Controller - Spring Boot version
 */
@RestController
@RequestMapping("/api/categories")
@CrossOrigin(origins = "*")
public class CategoryRestController {
    
    @Autowired
    private CategoryService categoryService;
    
    /**
     * 创建分类
     * Create category
     */
    @PostMapping
    public ResponseEntity<Category> createCategory(@RequestBody Category category) {
        try {
            Category createdCategory = categoryService.createCategory(category);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdCategory);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 根据ID获取分类
     * Get category by ID
     */
    @GetMapping("/{id}")
    public ResponseEntity<Category> getCategoryById(@PathVariable Long id) {
        Optional<Category> category = categoryService.getCategoryById(id);
        return category.map(ResponseEntity::ok)
                      .orElse(ResponseEntity.notFound().build());
    }
    
    /**
     * 获取所有分类
     * Get all categories
     */
    @GetMapping
    public ResponseEntity<List<Category>> getAllCategories() {
        List<Category> categories = categoryService.getAllCategories();
        return ResponseEntity.ok(categories);
    }
    
    /**
     * 获取所有激活的分类
     * Get all active categories
     */
    @GetMapping("/active")
    public ResponseEntity<List<Category>> getAllActiveCategories() {
        List<Category> categories = categoryService.getAllActiveCategories();
        return ResponseEntity.ok(categories);
    }
    
    /**
     * 获取根分类
     * Get root categories
     */
    @GetMapping("/root")
    public ResponseEntity<List<Category>> getRootCategories() {
        List<Category> categories = categoryService.getRootCategories();
        return ResponseEntity.ok(categories);
    }
    
    /**
     * 根据父ID获取子分类
     * Get child categories by parent ID
     */
    @GetMapping("/parent/{parentId}")
    public ResponseEntity<List<Category>> getChildCategories(@PathVariable Long parentId) {
        List<Category> categories = categoryService.getChildCategories(parentId);
        return ResponseEntity.ok(categories);
    }
    
    /**
     * 获取分类树
     * Get category tree
     */
    @GetMapping("/tree")
    public ResponseEntity<List<Category>> getCategoryTree() {
        List<Category> categories = categoryService.getCategoryTree();
        return ResponseEntity.ok(categories);
    }
    
    /**
     * 获取指定分类的子树
     * Get subtree of specified category
     */
    @GetMapping("/{id}/subtree")
    public ResponseEntity<List<Category>> getCategorySubtree(@PathVariable Long id) {
        List<Category> categories = categoryService.getCategorySubtree(id);
        return ResponseEntity.ok(categories);
    }
    
    /**
     * 获取分类的完整路径
     * Get full path of category
     */
    @GetMapping("/{id}/path")
    public ResponseEntity<List<Category>> getCategoryPath(@PathVariable Long id) {
        List<Category> path = categoryService.getCategoryPath(id);
        return ResponseEntity.ok(path);
    }
    
    /**
     * 根据名称搜索分类
     * Search categories by name
     */
    @GetMapping("/search")
    public ResponseEntity<List<Category>> searchCategoriesByName(@RequestParam String name) {
        List<Category> categories = categoryService.searchCategoriesByName(name);
        return ResponseEntity.ok(categories);
    }
    
    /**
     * 根据层级获取分类
     * Get categories by level
     */
    @GetMapping("/level/{level}")
    public ResponseEntity<List<Category>> getCategoriesByLevel(@PathVariable Integer level) {
        List<Category> categories = categoryService.getCategoriesByLevel(level);
        return ResponseEntity.ok(categories);
    }
    
    /**
     * 更新分类
     * Update category
     */
    @PutMapping("/{id}")
    public ResponseEntity<Category> updateCategory(@PathVariable Long id, @RequestBody Category category) {
        try {
            category.setId(id);
            Category updatedCategory = categoryService.updateCategory(category);
            return ResponseEntity.ok(updatedCategory);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 移动分类到新的父分类下
     * Move category to new parent
     */
    @PutMapping("/{id}/move")
    public ResponseEntity<Category> moveCategory(@PathVariable Long id, @RequestParam Long parentId) {
        try {
            Category movedCategory = categoryService.moveCategory(id, parentId);
            return ResponseEntity.ok(movedCategory);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 删除分类
     * Delete category
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteCategory(@PathVariable Long id) {
        try {
            categoryService.deleteCategory(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
    
    /**
     * 软删除分类
     * Soft delete category
     */
    @DeleteMapping("/{id}/soft")
    public ResponseEntity<Void> softDeleteCategory(@PathVariable Long id) {
        try {
            categoryService.softDeleteCategory(id);
            return ResponseEntity.noContent().build();
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }
}