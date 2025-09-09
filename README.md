# Java Directory Copy Examples

This project demonstrates three different methods for copying directories in Java:

## Methods Included

### 1. Simple Directory Copy (`Files.copy()`)
- Uses `Files.copy()` from Java NIO
- **Note**: This only copies the directory itself, not its contents
- Good for creating empty directory structures

### 2. Recursive Directory Copy (`Files.walk()`)
- Uses `Files.walk()` to traverse all files and subdirectories
- Preserves file attributes and timestamps
- Copies all contents recursively
- Most comprehensive native Java solution

### 3. Apache Commons IO (`FileUtils.copyDirectory()`)
- Uses Apache Commons IO library
- Simplest and most convenient method
- Handles all edge cases automatically
- Requires external dependency

## How to Run

### Using Maven (Recommended)
```bash
# Compile and run
mvn compile exec:java

# Or just run if already compiled
mvn exec:java
```

### Using Java directly
```bash
# Compile
javac -cp ".:lib/commons-io-2.11.0.jar" DirectoryCopyExample.java

# Run
java -cp ".:lib/commons-io-2.11.0.jar" DirectoryCopyExample
```

## Dependencies

The project uses Apache Commons IO 2.11.0, which is included in the `pom.xml` file.

## Sample Output

The program will:
1. Create a sample directory structure with files and subdirectories
2. Demonstrate all three copying methods
3. Show the results of each method

## Key Features

- **Error Handling**: Proper exception handling for file operations
- **Directory Creation**: Automatically creates destination directories
- **File Preservation**: Maintains file attributes and timestamps
- **Recursive Copying**: Handles nested directory structures
- **Multiple Approaches**: Shows different ways to achieve the same goal

## Use Cases

- **Method 1**: When you only need to create directory structure
- **Method 2**: When you need full control over the copying process
- **Method 3**: When you want the simplest, most reliable solution