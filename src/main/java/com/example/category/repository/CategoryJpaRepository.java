package com.example.category.repository;

import com.example.category.entity.CategoryEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 分类JPA仓库接口
 * Category JPA repository interface
 */
@Repository
public interface CategoryJpaRepository extends JpaRepository<CategoryEntity, Long> {
    
    /**
     * 根据父ID查找子分类
     * Find child categories by parent ID
     */
    List<CategoryEntity> findByParentId(Long parentId);
    
    /**
     * 查找根分类（父ID为null或0）
     * Find root categories (parent ID is null or 0)
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.parentId IS NULL OR c.parentId = 0")
    List<CategoryEntity> findRootCategories();
    
    /**
     * 根据路径查找分类
     * Find categories by path
     */
    List<CategoryEntity> findByPathStartingWith(String path);
    
    /**
     * 根据名称模糊查询
     * Find categories by name (fuzzy search)
     */
    List<CategoryEntity> findByNameContainingIgnoreCase(String name);
    
    /**
     * 根据层级查找分类
     * Find categories by level
     */
    List<CategoryEntity> findByLevel(Integer level);
    
    /**
     * 查找所有激活的分类
     * Find all active categories
     */
    List<CategoryEntity> findByIsActiveTrue();
    
    /**
     * 根据父ID和激活状态查找子分类
     * Find child categories by parent ID and active status
     */
    List<CategoryEntity> findByParentIdAndIsActiveTrue(Long parentId);
    
    /**
     * 统计子分类数量
     * Count child categories
     */
    long countByParentId(Long parentId);
    
    /**
     * 根据排序字段查找分类
     * Find categories by sort order
     */
    List<CategoryEntity> findByParentIdOrderBySortOrderAsc(Long parentId);
    
    /**
     * 根据父ID和激活状态查找子分类，按排序字段排序
     * Find child categories by parent ID and active status, ordered by sort order
     */
    List<CategoryEntity> findByParentIdAndIsActiveTrueOrderBySortOrderAsc(Long parentId);
    
    /**
     * 查找指定路径下的所有分类
     * Find all categories under specified path
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.path LIKE :pathPattern")
    List<CategoryEntity> findByPathPattern(@Param("pathPattern") String pathPattern);
    
    /**
     * 查找指定分类的所有后代分类
     * Find all descendant categories of specified category
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.path LIKE :pathPattern AND c.id != :categoryId")
    List<CategoryEntity> findDescendants(@Param("pathPattern") String pathPattern, @Param("categoryId") Long categoryId);
}