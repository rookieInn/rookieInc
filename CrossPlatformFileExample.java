import java.io.*;
import java.nio.file.*;

/**
 * Comprehensive example demonstrating cross-platform file handling in Java
 * This example shows how to handle file paths that work on both Windows and Linux
 */
public class CrossPlatformFileExample {
    
    public static void main(String[] args) {
        System.out.println("=== Cross-Platform File Handling Example ===\n");
        
        // Display system information
        CrossPlatformFileUtils.displaySystemInfo();
        System.out.println();
        
        // Example 1: Basic path operations
        demonstrateBasicPathOperations();
        System.out.println();
        
        // Example 2: Path joining
        demonstratePathJoining();
        System.out.println();
        
        // Example 3: File operations
        demonstrateFileOperations();
        System.out.println();
        
        // Example 4: Directory operations
        demonstrateDirectoryOperations();
        System.out.println();
        
        // Example 5: Mixed path formats
        demonstrateMixedPathFormats();
        System.out.println();
        
        // Example 6: Real-world scenarios
        demonstrateRealWorldScenarios();
    }
    
    /**
     * Example 1: Basic path operations
     */
    private static void demonstrateBasicPathOperations() {
        System.out.println("--- Example 1: Basic Path Operations ---");
        
        // Test various path formats
        String[] testPaths = {
            "folder/file.txt",
            "folder\\file.txt",
            "/absolute/path/file.txt",
            "C:\\Windows\\System32\\file.txt",
            "folder//file.txt",
            "folder\\\\file.txt",
            "folder/../file.txt",
            "folder\\..\\file.txt"
        };
        
        for (String path : testPaths) {
            String normalized = CrossPlatformFileUtils.normalizePath(path);
            System.out.println("Original: " + path);
            System.out.println("Normalized: " + normalized);
            System.out.println("Forward slashes: " + CrossPlatformFileUtils.toForwardSlashes(normalized));
            System.out.println("Back slashes: " + CrossPlatformFileUtils.toBackSlashes(normalized));
            System.out.println();
        }
    }
    
    /**
     * Example 2: Path joining
     */
    private static void demonstratePathJoining() {
        System.out.println("--- Example 2: Path Joining ---");
        
        // Test various path joining scenarios
        String[][] testCases = {
            {"folder1", "folder2", "file.txt"},
            {"C:", "Users", "username", "Documents"},
            {"/home", "user", "projects", "myapp"},
            {"folder1/", "/folder2", "file.txt"},
            {"folder1\\", "\\folder2", "file.txt"},
            {"", "folder", "file.txt"},
            {"folder", "", "file.txt"},
            {"folder", null, "file.txt"}
        };
        
        for (String[] components : testCases) {
            String joined = CrossPlatformFileUtils.joinPath(components);
            System.out.println("Components: " + java.util.Arrays.toString(components));
            System.out.println("Joined: " + joined);
            System.out.println();
        }
    }
    
    /**
     * Example 3: File operations
     */
    private static void demonstrateFileOperations() {
        System.out.println("--- Example 3: File Operations ---");
        
        try {
            // Create test files using cross-platform paths
            String testDir = CrossPlatformFileUtils.joinPath("test", "cross", "platform");
            Files.createDirectories(CrossPlatformFileUtils.createPath(testDir));
            
            // Create files with different path formats
            String[] filePaths = {
                CrossPlatformFileUtils.joinPath(testDir, "file1.txt"),
                CrossPlatformFileUtils.joinPath(testDir, "subdir", "file2.txt"),
                CrossPlatformFileUtils.normalizePath(testDir + "/file3.txt")
            };
            
            for (String filePath : filePaths) {
                Path path = CrossPlatformFileUtils.createPath(filePath);
                
                // Create parent directories if needed
                if (path.getParent() != null) {
                    Files.createDirectories(path.getParent());
                }
                
                // Create file
                Files.write(path, ("Content of " + path.getFileName()).getBytes());
                System.out.println("Created file: " + path);
            }
            
            // List files in test directory
            System.out.println("\nFiles in test directory:");
            Files.walk(CrossPlatformFileUtils.createPath(testDir))
                .filter(Files::isRegularFile)
                .forEach(file -> System.out.println("  " + file));
                
        } catch (IOException e) {
            System.err.println("Error in file operations: " + e.getMessage());
        }
    }
    
    /**
     * Example 4: Directory operations
     */
    private static void demonstrateDirectoryOperations() {
        System.out.println("--- Example 4: Directory Operations ---");
        
        try {
            // Create nested directory structure
            String baseDir = CrossPlatformFileUtils.joinPath("test", "nested", "dirs");
            String[] subDirs = {"level1", "level2", "level3"};
            
            String currentPath = baseDir;
            for (String subDir : subDirs) {
                currentPath = CrossPlatformFileUtils.joinPath(currentPath, subDir);
                Files.createDirectories(CrossPlatformFileUtils.createPath(currentPath));
                System.out.println("Created directory: " + currentPath);
            }
            
            // Create files in each level
            for (int i = 0; i < subDirs.length; i++) {
                String filePath = CrossPlatformFileUtils.joinPath(baseDir, 
                    subDirs[0], subDirs[1], subDirs[2], "file" + (i + 1) + ".txt");
                Files.write(CrossPlatformFileUtils.createPath(filePath), 
                    ("File at level " + (i + 1)).getBytes());
                System.out.println("Created file: " + filePath);
            }
            
        } catch (IOException e) {
            System.err.println("Error in directory operations: " + e.getMessage());
        }
    }
    
    /**
     * Example 5: Mixed path formats
     */
    private static void demonstrateMixedPathFormats() {
        System.out.println("--- Example 5: Mixed Path Formats ---");
        
        // Simulate paths that might come from different sources
        String[] mixedPaths = {
            "C:/Users/username/Documents\\project\\src/main/java",
            "/home/user/projects\\myapp\\src/main/java",
            "folder1/folder2\\folder3/folder4",
            "C:\\Windows\\System32\\drivers\\etc/hosts"
        };
        
        for (String mixedPath : mixedPaths) {
            System.out.println("Mixed path: " + mixedPath);
            System.out.println("Normalized: " + CrossPlatformFileUtils.normalizePath(mixedPath));
            
            // Show how to handle different scenarios
            if (CrossPlatformFileUtils.isWindows()) {
                System.out.println("Windows format: " + CrossPlatformFileUtils.toBackSlashes(mixedPath));
            } else {
                System.out.println("Unix format: " + CrossPlatformFileUtils.toForwardSlashes(mixedPath));
            }
            System.out.println();
        }
    }
    
    /**
     * Example 6: Real-world scenarios
     */
    private static void demonstrateRealWorldScenarios() {
        System.out.println("--- Example 6: Real-World Scenarios ---");
        
        // Scenario 1: Configuration file paths
        String configDir = CrossPlatformFileUtils.joinPath(
            CrossPlatformFileUtils.getUserHome(), 
            ".myapp", 
            "config"
        );
        String configFile = CrossPlatformFileUtils.joinPath(configDir, "settings.properties");
        System.out.println("Config file path: " + configFile);
        
        // Scenario 2: Log file paths
        String logDir = CrossPlatformFileUtils.joinPath(
            CrossPlatformFileUtils.getTempDirectory(),
            "myapp",
            "logs"
        );
        String logFile = CrossPlatformFileUtils.joinPath(logDir, "application.log");
        System.out.println("Log file path: " + logFile);
        
        // Scenario 3: Resource paths (for JAR files)
        String resourcePath = CrossPlatformFileUtils.normalizePath("com/example/resources/data.txt");
        System.out.println("Resource path: " + resourcePath);
        
        // Scenario 4: Backup file naming
        String backupDir = CrossPlatformFileUtils.joinPath(
            CrossPlatformFileUtils.getCurrentDirectory(),
            "backups"
        );
        String timestamp = java.time.LocalDateTime.now().format(
            java.time.format.DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")
        );
        String backupFile = CrossPlatformFileUtils.joinPath(backupDir, "backup_" + timestamp + ".zip");
        System.out.println("Backup file path: " + backupFile);
        
        // Scenario 5: Cross-platform file copying
        try {
            String sourceFile = CrossPlatformFileUtils.joinPath("test", "source.txt");
            String destFile = CrossPlatformFileUtils.joinPath("test", "dest.txt");
            
            // Create source file
            Files.createDirectories(CrossPlatformFileUtils.createPath("test"));
            Files.write(CrossPlatformFileUtils.createPath(sourceFile), "Test content".getBytes());
            
            // Copy file using cross-platform paths
            Files.copy(
                CrossPlatformFileUtils.createPath(sourceFile),
                CrossPlatformFileUtils.createPath(destFile),
                StandardCopyOption.REPLACE_EXISTING
            );
            
            System.out.println("Copied file from: " + sourceFile);
            System.out.println("Copied file to: " + destFile);
            
        } catch (IOException e) {
            System.err.println("Error in file copying: " + e.getMessage());
        }
    }
}