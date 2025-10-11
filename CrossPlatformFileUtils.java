import java.io.File;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.FileSystems;

/**
 * Utility class for cross-platform file path handling
 * Handles both Windows ("\") and Linux/Unix ("/") file separators
 */
public class CrossPlatformFileUtils {
    
    /**
     * Get the file separator for the current operating system
     * @return String - "/" for Unix/Linux/Mac, "\" for Windows
     */
    public static String getFileSeparator() {
        return FileSystems.getDefault().getSeparator();
    }
    
    /**
     * Normalize a path to use the correct file separator for the current OS
     * @param path the path to normalize
     * @return normalized path with correct separators
     */
    public static String normalizePath(String path) {
        if (path == null || path.isEmpty()) {
            return path;
        }
        
        // Replace both forward and backward slashes with the system separator
        String normalized = path.replace("/", getFileSeparator())
                              .replace("\\", getFileSeparator());
        
        // Remove duplicate separators
        String separator = getFileSeparator();
        String doubleSeparator = separator + separator;
        while (normalized.contains(doubleSeparator)) {
            normalized = normalized.replace(doubleSeparator, separator);
        }
        
        return normalized;
    }
    
    /**
     * Build a path by joining multiple path components with the correct separator
     * @param components path components to join
     * @return joined path with correct separators
     */
    public static String joinPath(String... components) {
        if (components == null || components.length == 0) {
            return "";
        }
        
        StringBuilder path = new StringBuilder();
        String separator = getFileSeparator();
        
        for (int i = 0; i < components.length; i++) {
            if (components[i] == null || components[i].isEmpty()) {
                continue;
            }
            
            String component = components[i].trim();
            
            // Remove leading and trailing separators from component
            while (component.startsWith(separator) || component.startsWith("/") || component.startsWith("\\")) {
                component = component.substring(1);
            }
            while (component.endsWith(separator) || component.endsWith("/") || component.endsWith("\\")) {
                component = component.substring(0, component.length() - 1);
            }
            
            if (component.isEmpty()) {
                continue;
            }
            
            if (path.length() > 0) {
                path.append(separator);
            }
            path.append(component);
        }
        
        return path.toString();
    }
    
    /**
     * Create a Path object using the correct file separator
     * @param first path component
     * @param more additional path components
     * @return Path object
     */
    public static Path createPath(String first, String... more) {
        if (more == null || more.length == 0) {
            return Paths.get(first);
        }
        return Paths.get(first, more);
    }
    
    /**
     * Create a File object using the correct file separator
     * @param path the file path
     * @return File object
     */
    public static File createFile(String path) {
        return new File(normalizePath(path));
    }
    
    /**
     * Create a File object by joining multiple path components
     * @param components path components to join
     * @return File object
     */
    public static File createFile(String... components) {
        return new File(joinPath(components));
    }
    
    /**
     * Check if the current OS is Windows
     * @return true if Windows, false otherwise
     */
    public static boolean isWindows() {
        return getFileSeparator().equals("\\");
    }
    
    /**
     * Check if the current OS is Unix-like (Linux, Mac, etc.)
     * @return true if Unix-like, false otherwise
     */
    public static boolean isUnix() {
        return getFileSeparator().equals("/");
    }
    
    /**
     * Get the current working directory as a normalized path
     * @return current working directory path
     */
    public static String getCurrentDirectory() {
        return normalizePath(System.getProperty("user.dir"));
    }
    
    /**
     * Get the user home directory as a normalized path
     * @return user home directory path
     */
    public static String getUserHome() {
        return normalizePath(System.getProperty("user.home"));
    }
    
    /**
     * Get the temporary directory as a normalized path
     * @return temporary directory path
     */
    public static String getTempDirectory() {
        return normalizePath(System.getProperty("java.io.tmpdir"));
    }
    
    /**
     * Convert a path to use forward slashes (useful for URLs or cross-platform compatibility)
     * @param path the path to convert
     * @return path with forward slashes
     */
    public static String toForwardSlashes(String path) {
        if (path == null) return null;
        return path.replace("\\", "/");
    }
    
    /**
     * Convert a path to use backslashes (useful for Windows-specific operations)
     * @param path the path to convert
     * @return path with backslashes
     */
    public static String toBackSlashes(String path) {
        if (path == null) return null;
        return path.replace("/", "\\");
    }
    
    /**
     * Display system information about file separators
     */
    public static void displaySystemInfo() {
        System.out.println("=== Cross-Platform File System Information ===");
        System.out.println("Operating System: " + System.getProperty("os.name"));
        System.out.println("File Separator: '" + getFileSeparator() + "'");
        System.out.println("Path Separator: '" + File.pathSeparator + "'");
        System.out.println("Current Directory: " + getCurrentDirectory());
        System.out.println("User Home: " + getUserHome());
        System.out.println("Temp Directory: " + getTempDirectory());
        System.out.println("Is Windows: " + isWindows());
        System.out.println("Is Unix: " + isUnix());
        System.out.println("=============================================");
    }
}