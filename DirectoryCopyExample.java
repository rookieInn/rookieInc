import java.io.*;
import java.nio.file.*;
import java.util.stream.Stream;

public class DirectoryCopyExample {
    
    public static void main(String[] args) {
        String sourceDir = "source";
        String destDir = "destination";
        
        try {
            // Create sample directory structure for testing
            System.out.println("Creating sample directory structure...");
            createSampleDirectory();
            System.out.println();
            
            // Method 1: Using Files.copy() for simple directory copy
            System.out.println("Method 1: Simple directory copy");
            copyDirectorySimple(sourceDir, destDir + "_1");
            System.out.println();
            
            // Method 2: Using Files.walk() for recursive copy with file preservation
            System.out.println("Method 2: Recursive copy with file preservation");
            copyDirectoryRecursive(sourceDir, destDir + "_2");
            System.out.println();
            
            // Method 3: Using traditional Java IO
            System.out.println("Method 3: Using traditional Java IO");
            copyDirectoryTraditional(sourceDir, destDir + "_3");
            System.out.println();
            
            System.out.println("All directory copy methods completed!");
            
        } catch (IOException e) {
            System.err.println("Error copying directory: " + e.getMessage());
        }
    }
    
    /**
     * Method 1: Simple directory copy using Files.copy()
     * Note: This only copies the directory itself, not its contents
     */
    public static void copyDirectorySimple(String source, String destination) throws IOException {
        Path sourcePath = Paths.get(source);
        Path destPath = Paths.get(destination);
        
        if (!Files.exists(sourcePath)) {
            System.out.println("Source directory does not exist: " + source);
            return;
        }
        
        // Create destination directory if it doesn't exist
        if (destPath.getParent() != null) {
            Files.createDirectories(destPath.getParent());
        }
        
        // Copy the directory
        Files.copy(sourcePath, destPath, StandardCopyOption.REPLACE_EXISTING);
        System.out.println("Directory copied from " + source + " to " + destination);
    }
    
    /**
     * Method 2: Recursive directory copy preserving file attributes
     * This method copies all files and subdirectories recursively
     */
    public static void copyDirectoryRecursive(String source, String destination) throws IOException {
        Path sourcePath = Paths.get(source);
        Path destPath = Paths.get(destination);
        
        if (!Files.exists(sourcePath)) {
            System.out.println("Source directory does not exist: " + source);
            return;
        }
        
        // Create destination directory
        Files.createDirectories(destPath);
        
        // Walk through all files and directories
        try (Stream<Path> stream = Files.walk(sourcePath)) {
            stream.forEach(sourceFile -> {
                try {
                    Path targetFile = destPath.resolve(sourcePath.relativize(sourceFile));
                    
                    if (Files.isDirectory(sourceFile)) {
                        // Create directory
                        Files.createDirectories(targetFile);
                    } else {
                        // Copy file with attributes
                        Files.copy(sourceFile, targetFile, 
                                 StandardCopyOption.REPLACE_EXISTING,
                                 StandardCopyOption.COPY_ATTRIBUTES);
                    }
                } catch (IOException e) {
                    System.err.println("Error copying " + sourceFile + ": " + e.getMessage());
                }
            });
        }
        
        System.out.println("Recursive copy completed from " + source + " to " + destination);
    }
    
    /**
     * Method 3: Using traditional Java IO (FileInputStream/FileOutputStream)
     * This method provides more control over the copying process
     */
    public static void copyDirectoryTraditional(String source, String destination) throws IOException {
        File sourceDir = new File(source);
        File destDir = new File(destination);
        
        if (!sourceDir.exists()) {
            System.out.println("Source directory does not exist: " + source);
            return;
        }
        
        if (!sourceDir.isDirectory()) {
            System.out.println("Source is not a directory: " + source);
            return;
        }
        
        // Create destination directory
        if (!destDir.exists()) {
            destDir.mkdirs();
        }
        
        // Get all files and directories
        File[] files = sourceDir.listFiles();
        if (files != null) {
            for (File file : files) {
                File destFile = new File(destDir, file.getName());
                
                if (file.isDirectory()) {
                    // Recursively copy subdirectory
                    copyDirectoryTraditional(file.getAbsolutePath(), destFile.getAbsolutePath());
                } else {
                    // Copy file
                    copyFile(file, destFile);
                }
            }
        }
        
        System.out.println("Traditional copy completed from " + source + " to " + destination);
    }
    
    /**
     * Helper method to copy a single file using traditional Java IO
     */
    private static void copyFile(File source, File destination) throws IOException {
        try (FileInputStream fis = new FileInputStream(source);
             FileOutputStream fos = new FileOutputStream(destination)) {
            
            byte[] buffer = new byte[1024];
            int length;
            while ((length = fis.read(buffer)) > 0) {
                fos.write(buffer, 0, length);
            }
        }
    }
    
    /**
     * Utility method to create a sample directory structure for testing
     */
    public static void createSampleDirectory() throws IOException {
        // Create source directory with some files and subdirectories
        Files.createDirectories(Paths.get("source/subdir1"));
        Files.createDirectories(Paths.get("source/subdir2"));
        
        // Create some sample files
        Files.write(Paths.get("source/file1.txt"), "Hello World!".getBytes());
        Files.write(Paths.get("source/file2.txt"), "Java Directory Copy Example".getBytes());
        Files.write(Paths.get("source/subdir1/file3.txt"), "Nested file content".getBytes());
        Files.write(Paths.get("source/subdir2/file4.txt"), "Another nested file".getBytes());
        
        System.out.println("Sample directory structure created in 'source' folder");
    }
}