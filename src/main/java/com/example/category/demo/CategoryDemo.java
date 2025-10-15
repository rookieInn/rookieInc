package com.example.category.demo;

import com.example.category.controller.CategoryController;
import com.example.category.model.Category;

import java.util.List;
import java.util.Optional;

/**
 * 分类系统演示程序
 * Category system demo application
 */
public class CategoryDemo {
    
    public static void main(String[] args) {
        System.out.println("=== 多级分类系统演示 / Multi-Level Category System Demo ===\n");
        
        CategoryController controller = new CategoryController();
        
        // 1. 创建根分类 / Create root categories
        System.out.println("1. 创建根分类 / Creating root categories:");
        Category electronics = new Category("电子产品", "各种电子设备和配件", null);
        Category clothing = new Category("服装", "各种服装和配饰", null);
        Category books = new Category("图书", "各种书籍和出版物", null);
        
        electronics = controller.createCategory(electronics);
        clothing = controller.createCategory(clothing);
        books = controller.createCategory(books);
        
        System.out.println("创建了根分类: " + electronics.getName() + " (ID: " + electronics.getId() + ")");
        System.out.println("创建了根分类: " + clothing.getName() + " (ID: " + clothing.getId() + ")");
        System.out.println("创建了根分类: " + books.getName() + " (ID: " + books.getId() + ")");
        System.out.println();
        
        // 2. 创建二级分类 / Create second level categories
        System.out.println("2. 创建二级分类 / Creating second level categories:");
        
        // 电子产品子分类
        Category smartphones = new Category("智能手机", "各种品牌的智能手机", electronics.getId());
        Category laptops = new Category("笔记本电脑", "各种品牌的笔记本电脑", electronics.getId());
        Category accessories = new Category("配件", "电子设备配件", electronics.getId());
        
        smartphones = controller.createCategory(smartphones);
        laptops = controller.createCategory(laptops);
        accessories = controller.createCategory(accessories);
        
        // 服装子分类
        Category mensClothing = new Category("男装", "男性服装", clothing.getId());
        Category womensClothing = new Category("女装", "女性服装", clothing.getId());
        Category shoes = new Category("鞋类", "各种鞋子", clothing.getId());
        
        mensClothing = controller.createCategory(mensClothing);
        womensClothing = controller.createCategory(womensClothing);
        shoes = controller.createCategory(shoes);
        
        // 图书子分类
        Category fiction = new Category("小说", "各种小说作品", books.getId());
        Category technology = new Category("技术书籍", "计算机和技术相关书籍", books.getId());
        Category education = new Category("教育", "教育相关书籍", books.getId());
        
        fiction = controller.createCategory(fiction);
        technology = controller.createCategory(technology);
        education = controller.createCategory(education);
        
        System.out.println("创建了二级分类: " + smartphones.getName() + " (父分类: " + electronics.getName() + ")");
        System.out.println("创建了二级分类: " + laptops.getName() + " (父分类: " + electronics.getName() + ")");
        System.out.println("创建了二级分类: " + mensClothing.getName() + " (父分类: " + clothing.getName() + ")");
        System.out.println("创建了二级分类: " + fiction.getName() + " (父分类: " + books.getName() + ")");
        System.out.println();
        
        // 3. 创建三级分类 / Create third level categories
        System.out.println("3. 创建三级分类 / Creating third level categories:");
        
        // 智能手机子分类
        Category androidPhones = new Category("安卓手机", "基于Android系统的智能手机", smartphones.getId());
        Category iphones = new Category("iPhone", "苹果iPhone系列", smartphones.getId());
        
        androidPhones = controller.createCategory(androidPhones);
        iphones = controller.createCategory(iphones);
        
        // 笔记本电脑子分类
        Category gamingLaptops = new Category("游戏本", "专为游戏设计的笔记本电脑", laptops.getId());
        Category businessLaptops = new Category("商务本", "商务办公用笔记本电脑", laptops.getId());
        
        gamingLaptops = controller.createCategory(gamingLaptops);
        businessLaptops = controller.createCategory(businessLaptops);
        
        // 男装子分类
        Category mensShirts = new Category("男式衬衫", "各种男式衬衫", mensClothing.getId());
        Category mensPants = new Category("男式裤子", "各种男式裤子", mensClothing.getId());
        
        mensShirts = controller.createCategory(mensShirts);
        mensPants = controller.createCategory(mensPants);
        
        System.out.println("创建了三级分类: " + androidPhones.getName() + " (父分类: " + smartphones.getName() + ")");
        System.out.println("创建了三级分类: " + gamingLaptops.getName() + " (父分类: " + laptops.getName() + ")");
        System.out.println("创建了三级分类: " + mensShirts.getName() + " (父分类: " + mensClothing.getName() + ")");
        System.out.println();
        
        // 4. 查询所有分类 / Query all categories
        System.out.println("4. 查询所有分类 / Query all categories:");
        List<Category> allCategories = controller.getAllCategories();
        System.out.println("总分类数: " + allCategories.size());
        for (Category category : allCategories) {
            System.out.println("- " + category.getName() + " (ID: " + category.getId() + 
                             ", 层级: " + category.getLevel() + 
                             ", 路径: " + category.getPath() + ")");
        }
        System.out.println();
        
        // 5. 查询根分类 / Query root categories
        System.out.println("5. 查询根分类 / Query root categories:");
        List<Category> rootCategories = controller.getRootCategories();
        for (Category category : rootCategories) {
            System.out.println("- " + category.getName() + " (ID: " + category.getId() + ")");
        }
        System.out.println();
        
        // 6. 查询子分类 / Query child categories
        System.out.println("6. 查询电子产品子分类 / Query electronics child categories:");
        List<Category> electronicsChildren = controller.getChildCategories(electronics.getId());
        for (Category category : electronicsChildren) {
            System.out.println("- " + category.getName() + " (ID: " + category.getId() + ")");
        }
        System.out.println();
        
        // 7. 查询分类树 / Query category tree
        System.out.println("7. 查询完整分类树 / Query complete category tree:");
        List<Category> categoryTree = controller.getCategoryTree();
        printCategoryTree(categoryTree, 0);
        System.out.println();
        
        // 8. 搜索分类 / Search categories
        System.out.println("8. 搜索包含'手机'的分类 / Search categories containing '手机':");
        List<Category> searchResults = controller.searchCategoriesByName("手机");
        for (Category category : searchResults) {
            System.out.println("- " + category.getName() + " (ID: " + category.getId() + ")");
        }
        System.out.println();
        
        // 9. 查询分类路径 / Query category path
        System.out.println("9. 查询iPhone分类的完整路径 / Query iPhone category full path:");
        List<Category> iphonePath = controller.getCategoryPath(iphones.getId());
        System.out.print("路径: ");
        for (int i = 0; i < iphonePath.size(); i++) {
            System.out.print(iphonePath.get(i).getName());
            if (i < iphonePath.size() - 1) {
                System.out.print(" > ");
            }
        }
        System.out.println();
        System.out.println();
        
        // 10. 移动分类 / Move category
        System.out.println("10. 移动分类 / Move category:");
        System.out.println("将配件分类移动到智能手机下 / Move accessories category under smartphones");
        Category movedAccessories = controller.moveCategory(accessories.getId(), smartphones.getId());
        System.out.println("移动后的配件分类路径: " + movedAccessories.getPath());
        System.out.println();
        
        // 11. 更新分类 / Update category
        System.out.println("11. 更新分类 / Update category:");
        System.out.println("更新iPhone分类描述 / Update iPhone category description");
        iphones.setDescription("苹果公司生产的iPhone系列智能手机，包括最新型号");
        controller.updateCategory(iphones.getId(), iphones);
        System.out.println("更新后的描述: " + iphones.getDescription());
        System.out.println();
        
        // 12. 软删除分类 / Soft delete category
        System.out.println("12. 软删除分类 / Soft delete category:");
        System.out.println("软删除教育分类 / Soft delete education category");
        controller.softDeleteCategory(education.getId());
        System.out.println("教育分类已软删除 / Education category soft deleted");
        System.out.println();
        
        // 13. 最终分类树 / Final category tree
        System.out.println("13. 最终分类树（仅激活的分类）/ Final category tree (active categories only):");
        List<Category> finalTree = controller.getCategoryTree();
        printCategoryTree(finalTree, 0);
        
        System.out.println("\n=== 演示完成 / Demo completed ===");
    }
    
    /**
     * 打印分类树
     * Print category tree
     */
    private static void printCategoryTree(List<Category> categories, int depth) {
        for (Category category : categories) {
            if (Boolean.TRUE.equals(category.getIsActive())) {
                for (int i = 0; i < depth; i++) {
                    System.out.print("  ");
                }
                System.out.println("- " + category.getName() + " (ID: " + category.getId() + 
                                 ", 层级: " + category.getLevel() + ")");
                
                if (!category.getChildren().isEmpty()) {
                    printCategoryTree(category.getChildren(), depth + 1);
                }
            }
        }
    }
}