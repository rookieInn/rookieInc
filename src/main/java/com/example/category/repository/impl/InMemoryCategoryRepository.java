package com.example.category.repository.impl;

import com.example.category.model.Category;
import com.example.category.repository.CategoryRepository;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

/**
 * 内存存储的分类仓库实现
 * In-memory category repository implementation
 */
public class InMemoryCategoryRepository implements CategoryRepository {
    
    private final Map<Long, Category> categories = new HashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);
    
    @Override
    public Category save(Category category) {
        if (category.getId() == null) {
            category.setId(idGenerator.getAndIncrement());
            category.setCreateTime(LocalDateTime.now());
        }
        category.setUpdateTime(LocalDateTime.now());
        categories.put(category.getId(), category);
        return category;
    }
    
    @Override
    public Optional<Category> findById(Long id) {
        return Optional.ofNullable(categories.get(id));
    }
    
    @Override
    public List<Category> findAll() {
        return new ArrayList<>(categories.values());
    }
    
    @Override
    public List<Category> findByParentId(Long parentId) {
        return categories.values().stream()
                .filter(category -> Objects.equals(category.getParentId(), parentId))
                .collect(Collectors.toList());
    }
    
    @Override
    public List<Category> findRootCategories() {
        return categories.values().stream()
                .filter(category -> category.getParentId() == null || category.getParentId() == 0)
                .collect(Collectors.toList());
    }
    
    @Override
    public List<Category> findByPath(String path) {
        return categories.values().stream()
                .filter(category -> category.getPath() != null && category.getPath().startsWith(path))
                .collect(Collectors.toList());
    }
    
    @Override
    public List<Category> findByNameContaining(String name) {
        return categories.values().stream()
                .filter(category -> category.getName() != null && 
                        category.getName().toLowerCase().contains(name.toLowerCase()))
                .collect(Collectors.toList());
    }
    
    @Override
    public List<Category> findByLevel(Integer level) {
        return categories.values().stream()
                .filter(category -> Objects.equals(category.getLevel(), level))
                .collect(Collectors.toList());
    }
    
    @Override
    public List<Category> findByIsActiveTrue() {
        return categories.values().stream()
                .filter(category -> Boolean.TRUE.equals(category.getIsActive()))
                .collect(Collectors.toList());
    }
    
    @Override
    public List<Category> findByParentIdAndIsActiveTrue(Long parentId) {
        return categories.values().stream()
                .filter(category -> Objects.equals(category.getParentId(), parentId) && 
                        Boolean.TRUE.equals(category.getIsActive()))
                .collect(Collectors.toList());
    }
    
    @Override
    public Category update(Category category) {
        if (category.getId() != null && categories.containsKey(category.getId())) {
            category.setUpdateTime(LocalDateTime.now());
            categories.put(category.getId(), category);
            return category;
        }
        throw new IllegalArgumentException("Category not found with id: " + category.getId());
    }
    
    @Override
    public void deleteById(Long id) {
        categories.remove(id);
    }
    
    @Override
    public boolean existsById(Long id) {
        return categories.containsKey(id);
    }
    
    @Override
    public long countByParentId(Long parentId) {
        return categories.values().stream()
                .filter(category -> Objects.equals(category.getParentId(), parentId))
                .count();
    }
    
    @Override
    public List<Category> findByParentIdOrderBySortOrderAsc(Long parentId) {
        return categories.values().stream()
                .filter(category -> Objects.equals(category.getParentId(), parentId))
                .sorted(Comparator.comparing(category -> 
                        category.getSortOrder() != null ? category.getSortOrder() : 0))
                .collect(Collectors.toList());
    }
}