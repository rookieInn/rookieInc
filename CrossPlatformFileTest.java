import java.io.*;
import java.nio.file.*;
import java.util.*;

/**
 * Test class for cross-platform file handling
 * This class tests various scenarios to ensure compatibility
 */
public class CrossPlatformFileTest {
    
    public static void main(String[] args) {
        System.out.println("=== Cross-Platform File Handling Tests ===\n");
        
        int passedTests = 0;
        int totalTests = 0;
        
        // Test 1: Path normalization
        totalTests++;
        if (testPathNormalization()) {
            passedTests++;
            System.out.println("✓ Path normalization test passed");
        } else {
            System.out.println("✗ Path normalization test failed");
        }
        
        // Test 2: Path joining
        totalTests++;
        if (testPathJoining()) {
            passedTests++;
            System.out.println("✓ Path joining test passed");
        } else {
            System.out.println("✗ Path joining test failed");
        }
        
        // Test 3: File creation
        totalTests++;
        if (testFileCreation()) {
            passedTests++;
            System.out.println("✓ File creation test passed");
        } else {
            System.out.println("✗ File creation test failed");
        }
        
        // Test 4: Directory operations
        totalTests++;
        if (testDirectoryOperations()) {
            passedTests++;
            System.out.println("✓ Directory operations test passed");
        } else {
            System.out.println("✗ Directory operations test failed");
        }
        
        // Test 5: Cross-platform compatibility
        totalTests++;
        if (testCrossPlatformCompatibility()) {
            passedTests++;
            System.out.println("✓ Cross-platform compatibility test passed");
        } else {
            System.out.println("✗ Cross-platform compatibility test failed");
        }
        
        // Test 6: Edge cases
        totalTests++;
        if (testEdgeCases()) {
            passedTests++;
            System.out.println("✓ Edge cases test passed");
        } else {
            System.out.println("✗ Edge cases test failed");
        }
        
        System.out.println("\n=== Test Results ===");
        System.out.println("Passed: " + passedTests + "/" + totalTests);
        System.out.println("Success rate: " + (passedTests * 100 / totalTests) + "%");
        
        if (passedTests == totalTests) {
            System.out.println("🎉 All tests passed! Cross-platform file handling is working correctly.");
        } else {
            System.out.println("⚠️  Some tests failed. Please check the implementation.");
        }
    }
    
    /**
     * Test path normalization functionality
     */
    private static boolean testPathNormalization() {
        try {
            // Test cases: [input, expected_contains]
            String[][] testCases = {
                {"folder/file.txt", "folder" + CrossPlatformFileUtils.getFileSeparator() + "file.txt"},
                {"folder\\file.txt", "folder" + CrossPlatformFileUtils.getFileSeparator() + "file.txt"},
                {"folder//file.txt", "folder" + CrossPlatformFileUtils.getFileSeparator() + "file.txt"},
                {"folder\\\\file.txt", "folder" + CrossPlatformFileUtils.getFileSeparator() + "file.txt"},
                {"", ""},
                {null, null}
            };
            
            for (String[] testCase : testCases) {
                String input = testCase[0];
                String expected = testCase[1];
                String result = CrossPlatformFileUtils.normalizePath(input);
                
                if (expected == null && result != null) return false;
                if (expected != null && !result.equals(expected)) return false;
            }
            
            return true;
        } catch (Exception e) {
            System.err.println("Error in path normalization test: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Test path joining functionality
     */
    private static boolean testPathJoining() {
        try {
            // Test cases: [components, expected_contains]
            String[][][] testCases = {
                {{"folder1", "folder2", "file.txt"}, {"folder1", "folder2", "file.txt"}},
                {{"C:", "Users", "username"}, {"C:", "Users", "username"}},
                {{"/", "home", "user"}, {"/", "home", "user"}},
                {{"folder", "", "file.txt"}, {"folder", "file.txt"}},
                {{"folder", null, "file.txt"}, {"folder", "file.txt"}}
            };
            
            for (String[][] testCase : testCases) {
                String[] components = testCase[0];
                String[] expectedParts = testCase[1];
                String result = CrossPlatformFileUtils.joinPath(components);
                
                // Check if all expected parts are in the result
                for (String part : expectedParts) {
                    if (part != null && !result.contains(part)) {
                        return false;
                    }
                }
            }
            
            return true;
        } catch (Exception e) {
            System.err.println("Error in path joining test: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Test file creation functionality
     */
    private static boolean testFileCreation() {
        try {
            // Create test directory
            String testDir = CrossPlatformFileUtils.joinPath("test", "file_creation");
            Files.createDirectories(CrossPlatformFileUtils.createPath(testDir));
            
            // Test file creation with different path formats
            String[] filePaths = {
                CrossPlatformFileUtils.joinPath(testDir, "file1.txt"),
                CrossPlatformFileUtils.normalizePath(testDir + "/file2.txt"),
                CrossPlatformFileUtils.normalizePath(testDir + "\\file3.txt")
            };
            
            for (String filePath : filePaths) {
                Path path = CrossPlatformFileUtils.createPath(filePath);
                Files.write(path, "Test content".getBytes());
                
                if (!Files.exists(path)) {
                    return false;
                }
            }
            
            // Clean up
            Files.walk(CrossPlatformFileUtils.createPath(testDir))
                .sorted(Comparator.reverseOrder())
                .map(Path::toFile)
                .forEach(File::delete);
            
            return true;
        } catch (Exception e) {
            System.err.println("Error in file creation test: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Test directory operations
     */
    private static boolean testDirectoryOperations() {
        try {
            // Create nested directory structure
            String baseDir = CrossPlatformFileUtils.joinPath("test", "nested", "test");
            String[] subDirs = {"level1", "level2", "level3"};
            
            String currentPath = baseDir;
            for (String subDir : subDirs) {
                currentPath = CrossPlatformFileUtils.joinPath(currentPath, subDir);
                Files.createDirectories(CrossPlatformFileUtils.createPath(currentPath));
                
                if (!Files.exists(CrossPlatformFileUtils.createPath(currentPath))) {
                    return false;
                }
            }
            
            // Clean up
            Files.walk(CrossPlatformFileUtils.createPath("test"))
                .sorted(Comparator.reverseOrder())
                .map(Path::toFile)
                .forEach(File::delete);
            
            return true;
        } catch (Exception e) {
            System.err.println("Error in directory operations test: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Test cross-platform compatibility
     */
    private static boolean testCrossPlatformCompatibility() {
        try {
            // Test that the same path works on different systems
            String[] testPaths = {
                "folder/file.txt",
                "folder\\file.txt",
                "C:/Users/username/file.txt",
                "/home/user/file.txt"
            };
            
            for (String path : testPaths) {
                String normalized = CrossPlatformFileUtils.normalizePath(path);
                
                // Check that normalized path uses correct separator
                String separator = CrossPlatformFileUtils.getFileSeparator();
                if (normalized.contains("/") && !separator.equals("/")) {
                    // Should not contain forward slashes on Windows
                    if (CrossPlatformFileUtils.isWindows()) {
                        return false;
                    }
                }
                if (normalized.contains("\\") && !separator.equals("\\")) {
                    // Should not contain backslashes on Unix
                    if (CrossPlatformFileUtils.isUnix()) {
                        return false;
                    }
                }
            }
            
            return true;
        } catch (Exception e) {
            System.err.println("Error in cross-platform compatibility test: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Test edge cases
     */
    private static boolean testEdgeCases() {
        try {
            // Test null and empty inputs
            String[] edgeCases = {null, "", "   ", "///", "\\\\\\"};
            
            for (String edgeCase : edgeCases) {
                String result = CrossPlatformFileUtils.normalizePath(edgeCase);
                // Should not throw exception
            }
            
            // Test very long paths
            StringBuilder longPath = new StringBuilder();
            for (int i = 0; i < 100; i++) {
                longPath.append("folder").append(i).append(CrossPlatformFileUtils.getFileSeparator());
            }
            longPath.append("file.txt");
            
            String normalized = CrossPlatformFileUtils.normalizePath(longPath.toString());
            if (normalized == null || normalized.isEmpty()) {
                return false;
            }
            
            return true;
        } catch (Exception e) {
            System.err.println("Error in edge cases test: " + e.getMessage());
            return false;
        }
    }
}