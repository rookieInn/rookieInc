package com.example.category.repository;

import com.example.category.model.Category;
import java.util.List;
import java.util.Optional;

/**
 * 分类数据访问接口
 * Category data access interface
 */
public interface CategoryRepository {
    
    /**
     * 保存分类
     * Save category
     */
    Category save(Category category);
    
    /**
     * 根据ID查找分类
     * Find category by ID
     */
    Optional<Category> findById(Long id);
    
    /**
     * 查找所有分类
     * Find all categories
     */
    List<Category> findAll();
    
    /**
     * 根据父ID查找子分类
     * Find child categories by parent ID
     */
    List<Category> findByParentId(Long parentId);
    
    /**
     * 查找根分类（父ID为null或0）
     * Find root categories (parent ID is null or 0)
     */
    List<Category> findRootCategories();
    
    /**
     * 根据路径查找分类
     * Find categories by path
     */
    List<Category> findByPath(String path);
    
    /**
     * 根据名称模糊查询
     * Find categories by name (fuzzy search)
     */
    List<Category> findByNameContaining(String name);
    
    /**
     * 根据层级查找分类
     * Find categories by level
     */
    List<Category> findByLevel(Integer level);
    
    /**
     * 查找所有激活的分类
     * Find all active categories
     */
    List<Category> findByIsActiveTrue();
    
    /**
     * 根据父ID和激活状态查找子分类
     * Find child categories by parent ID and active status
     */
    List<Category> findByParentIdAndIsActiveTrue(Long parentId);
    
    /**
     * 更新分类
     * Update category
     */
    Category update(Category category);
    
    /**
     * 删除分类
     * Delete category
     */
    void deleteById(Long id);
    
    /**
     * 检查分类是否存在
     * Check if category exists
     */
    boolean existsById(Long id);
    
    /**
     * 统计子分类数量
     * Count child categories
     */
    long countByParentId(Long parentId);
    
    /**
     * 根据排序字段查找分类
     * Find categories by sort order
     */
    List<Category> findByParentIdOrderBySortOrderAsc(Long parentId);
}