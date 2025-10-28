import java.text.DecimalFormat;
import java.util.Formatter;

/**
 * Java生成补0数字的几种方法示例
 */
public class ZeroPaddingExample {
    
    public static void main(String[] args) {
        int number = 42;
        int totalWidth = 5; // 总宽度为5位
        
        System.out.println("原始数字: " + number);
        System.out.println("目标宽度: " + totalWidth + "位");
        System.out.println("========================");
        
        // 方法1: 使用String.format() - 最常用
        String result1 = String.format("%0" + totalWidth + "d", number);
        System.out.println("方法1 - String.format(): " + result1);
        
        // 方法2: 使用DecimalFormat
        DecimalFormat df = new DecimalFormat("00000"); // 5个0表示5位数字
        String result2 = df.format(number);
        System.out.println("方法2 - DecimalFormat: " + result2);
        
        // 方法3: 使用StringBuilder手动补0
        String result3 = padWithZeros(number, totalWidth);
        System.out.println("方法3 - 手动补0: " + result3);
        
        // 方法4: 使用Formatter
        Formatter formatter = new Formatter();
        String result4 = formatter.format("%0" + totalWidth + "d", number).toString();
        System.out.println("方法4 - Formatter: " + result4);
        formatter.close();
        
        // 方法5: 使用Apache Commons Lang (需要添加依赖)
        // String result5 = StringUtils.leftPad(String.valueOf(number), totalWidth, '0');
        // System.out.println("方法5 - Apache Commons: " + result5);
        
        System.out.println("\n========================");
        System.out.println("更多示例:");
        
        // 不同宽度的示例
        int[] widths = {3, 6, 8};
        for (int width : widths) {
            String padded = String.format("%0" + width + "d", number);
            System.out.println("宽度" + width + "位: " + padded);
        }
        
        // 不同数字的示例
        int[] numbers = {1, 123, 9999, 12345};
        for (int num : numbers) {
            String padded = String.format("%05d", num);
            System.out.println("数字" + num + "补0后: " + padded);
        }
    }
    
    /**
     * 手动补0的方法
     * @param number 要补0的数字
     * @param width 目标宽度
     * @return 补0后的字符串
     */
    public static String padWithZeros(int number, int width) {
        String numStr = String.valueOf(number);
        if (numStr.length() >= width) {
            return numStr;
        }
        
        StringBuilder sb = new StringBuilder();
        int zerosToAdd = width - numStr.length();
        for (int i = 0; i < zerosToAdd; i++) {
            sb.append('0');
        }
        sb.append(numStr);
        return sb.toString();
    }
}