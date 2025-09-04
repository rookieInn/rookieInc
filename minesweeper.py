import tkinter as tk
from tkinter import messagebox
import random
from typing import List, Tuple, Optional

class MinesweeperGame:
    def __init__(self, rows: int = 16, cols: int = 16, mines: int = 40):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = [[0 for _ in range(cols)] for _ in range(rows)]
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]
        self.flagged = [[False for _ in range(cols)] for _ in range(rows)]
        self.game_over = False
        self.first_click = True
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("扫雷游戏")
        self.root.resizable(False, False)
        
        # 创建游戏界面
        self.create_widgets()
        self.setup_board()
        
    def create_widgets(self):
        """创建游戏界面组件"""
        # 顶部信息栏
        self.info_frame = tk.Frame(self.root)
        self.info_frame.pack(pady=10)
        
        # 剩余地雷数显示
        self.mines_label = tk.Label(self.info_frame, text=f"地雷: {self.mines}", 
                                   font=("Arial", 12, "bold"))
        self.mines_label.pack(side=tk.LEFT, padx=10)
        
        # 重新开始按钮
        self.restart_button = tk.Button(self.info_frame, text="重新开始", 
                                       command=self.restart_game, font=("Arial", 10))
        self.restart_button.pack(side=tk.RIGHT, padx=10)
        
        # 游戏板
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(padx=10, pady=5)
        
        # 创建按钮网格
        self.buttons = []
        for i in range(self.rows):
            button_row = []
            for j in range(self.cols):
                btn = tk.Button(self.game_frame, width=2, height=1, 
                               font=("Arial", 8, "bold"),
                               command=lambda r=i, c=j: self.on_click(r, c),
                               relief=tk.RAISED)
                btn.grid(row=i, column=j, padx=1, pady=1)
                btn.bind("<Button-3>", lambda event, r=i, c=j: self.on_right_click(r, c))
                button_row.append(btn)
            self.buttons.append(button_row)
    
    def setup_board(self):
        """初始化游戏板"""
        # 重置所有状态
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flagged = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.game_over = False
        self.first_click = True
        
        # 更新按钮显示
        for i in range(self.rows):
            for j in range(self.cols):
                self.buttons[i][j].config(text="", bg="lightgray", state=tk.NORMAL)
        
        # 更新地雷计数
        self.mines_label.config(text=f"地雷: {self.mines}")
    
    def place_mines(self, exclude_row: int, exclude_col: int):
        """布置地雷，排除首次点击位置"""
        mines_placed = 0
        while mines_placed < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            
            # 确保不在排除位置放置地雷，且该位置没有地雷
            if (row != exclude_row or col != exclude_col) and self.board[row][col] != -1:
                self.board[row][col] = -1  # -1 表示地雷
                mines_placed += 1
        
        # 计算每个格子周围的地雷数
        self.calculate_numbers()
    
    def calculate_numbers(self):
        """计算每个格子周围的地雷数量"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != -1:  # 如果不是地雷
                    count = 0
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            ni, nj = i + di, j + dj
                            if (0 <= ni < self.rows and 0 <= nj < self.cols and 
                                self.board[ni][nj] == -1):
                                count += 1
                    self.board[i][j] = count
    
    def on_click(self, row: int, col: int):
        """处理左键点击"""
        if self.game_over or self.revealed[row][col] or self.flagged[row][col]:
            return
        
        # 首次点击时布置地雷
        if self.first_click:
            self.place_mines(row, col)
            self.first_click = False
        
        self.reveal_cell(row, col)
        self.update_display()
        
        # 检查游戏状态
        if self.board[row][col] == -1:
            self.game_over = True
            self.reveal_all_mines()
            messagebox.showinfo("游戏结束", "你踩到地雷了！")
        elif self.check_win():
            self.game_over = True
            messagebox.showinfo("恭喜", "你赢了！")
    
    def on_right_click(self, row: int, col: int):
        """处理右键点击（标记/取消标记）"""
        if self.game_over or self.revealed[row][col]:
            return
        
        self.flagged[row][col] = not self.flagged[row][col]
        self.update_display()
    
    def reveal_cell(self, row: int, col: int):
        """揭示格子"""
        if (row < 0 or row >= self.rows or col < 0 or col >= self.cols or 
            self.revealed[row][col] or self.flagged[row][col]):
            return
        
        self.revealed[row][col] = True
        
        # 如果是空白格子，自动揭示周围格子
        if self.board[row][col] == 0:
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    self.reveal_cell(row + di, col + dj)
    
    def reveal_all_mines(self):
        """揭示所有地雷"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == -1:
                    self.revealed[i][j] = True
        self.update_display()
    
    def check_win(self) -> bool:
        """检查是否获胜"""
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != -1 and not self.revealed[i][j]:
                    return False
        return True
    
    def update_display(self):
        """更新界面显示"""
        flagged_count = 0
        
        for i in range(self.rows):
            for j in range(self.cols):
                btn = self.buttons[i][j]
                
                if self.flagged[i][j]:
                    btn.config(text="🚩", bg="lightcoral")
                    flagged_count += 1
                elif self.revealed[i][j]:
                    if self.board[i][j] == -1:
                        btn.config(text="💣", bg="red")
                    elif self.board[i][j] == 0:
                        btn.config(text="", bg="white")
                    else:
                        # 根据数字设置不同颜色
                        colors = ["", "blue", "green", "red", "purple", 
                                "brown", "pink", "black", "gray"]
                        color = colors[min(self.board[i][j], len(colors) - 1)]
                        btn.config(text=str(self.board[i][j]), 
                                 fg=color, bg="white")
                else:
                    btn.config(text="", bg="lightgray")
        
        # 更新剩余地雷数
        remaining_mines = self.mines - flagged_count
        self.mines_label.config(text=f"地雷: {remaining_mines}")
    
    def restart_game(self):
        """重新开始游戏"""
        self.setup_board()
    
    def run(self):
        """运行游戏"""
        self.root.mainloop()

def main():
    """主函数"""
    # 创建并运行扫雷游戏
    game = MinesweeperGame(rows=16, cols=16, mines=40)
    game.run()

if __name__ == "__main__":
    main()