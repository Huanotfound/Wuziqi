import sys
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QPoint


class GomokuGame(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        # 15x15棋盘，0=空，1=黑棋，2=白棋
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.current_player = 1  # 黑棋先手
        self.game_over = False
        self.winner = 0
        self.last_move = None  # 记录最后一步棋的位置

    def initUI(self):
        self.setWindowTitle('五子棋 - 改进版')
        self.setGeometry(300, 100, 700, 750)

        # 主布局
        main_layout = QVBoxLayout(self)

        # 顶部状态显示
        self.status_label = QLabel("当前回合：黑棋")
        self.status_label.setFont(QFont("SimHei", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        # 重置按钮
        reset_btn = QPushButton("重新开始")
        reset_btn.setFont(QFont("SimHei", 10))
        reset_btn.clicked.connect(self.reset_game)
        main_layout.addWidget(reset_btn)

        # 棋盘区域（自定义绘制）
        self.board_widget = BoardWidget(self)
        main_layout.addWidget(self.board_widget)

        # 底部信息
        info_label = QLabel("规则：左键轮流落子，连成五子获胜")
        info_label.setFont(QFont("SimHei", 9))
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)

        self.setLayout(main_layout)

    def reset_game(self):
        """重置游戏状态"""
        self.board = [[0 for _ in range(15)] for _ in range(15)]
        self.current_player = 1
        self.game_over = False
        self.winner = 0
        self.last_move = None
        self.status_label.setText("当前回合：黑棋")
        self.board_widget.update()

    def place_stone(self, row, col):
        """落子逻辑"""
        if self.game_over or self.board[row][col] != 0:
            return False

        self.board[row][col] = self.current_player
        self.last_move = (row, col)
        self.board_widget.update()

        # 检查胜负
        if self.check_win(row, col, self.current_player):
            self.game_over = True
            self.winner = self.current_player
            winner_text = "黑棋" if self.winner == 1 else "白棋"
            self.status_label.setText(f"游戏结束：{winner_text}获胜！")
            QMessageBox.information(self, "游戏结束", f"{winner_text}获胜！")
            return True

        # 切换玩家
        self.current_player = 2 if self.current_player == 1 else 1
        next_player_text = "黑棋" if self.current_player == 1 else "白棋"
        self.status_label.setText(f"当前回合：{next_player_text}")
        return True

    def check_win(self, row, col, player):
        """检查是否获胜（五子连珠）"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for dr, dc in directions:
            count = 1

            # 正向检查
            r, c = row + dr, col + dc
            while 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == player:
                count += 1
                r += dr
                c += dc

            # 反向检查
            r, c = row - dr, col - dc
            while 0 <= r < 15 and 0 <= c < 15 and self.board[r][c] == player:
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True
        return False


class BoardWidget(QWidget):
    """棋盘绘制和点击处理组件"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumSize(600, 600)
        self.setMaximumSize(600, 600)
        self.cell_size = 40  # 格子大小
        self.margin = 40  # 边距

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制棋盘线条
        self.draw_board_lines(painter)

        # 绘制棋子
        self.draw_stones(painter)

        # 绘制最后一步棋的标记
        self.draw_last_move_marker(painter)

    def draw_board_lines(self, painter):
        """绘制棋盘网格线"""
        pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(pen)

        # 绘制横线和竖线
        for i in range(15):
            # 横线
            y = self.margin + i * self.cell_size
            painter.drawLine(self.margin, y, self.margin + 14 * self.cell_size, y)
            # 竖线
            x = self.margin + i * self.cell_size
            painter.drawLine(x, self.margin, x, self.margin + 14 * self.cell_size)

        # 绘制五个星位点
        star_points = [(3, 3), (3, 11), (7, 7), (11, 3), (11, 11)]
        for x, y in star_points:
            center_x = self.margin + x * self.cell_size
            center_y = self.margin + y * self.cell_size
            painter.setBrush(QBrush(QColor(0, 0, 0)))
            painter.drawEllipse(center_x - 3, center_y - 3, 6, 6)

    def draw_stones(self, painter):
        """绘制棋子"""
        for row in range(15):
            for col in range(15):
                if self.parent.board[row][col] != 0:
                    # 计算棋子中心坐标
                    center_x = self.margin + col * self.cell_size
                    center_y = self.margin + row * self.cell_size

                    # 设置棋子颜色和样式
                    color = QColor(0, 0, 0) if self.parent.board[row][col] == 1 else QColor(255, 255, 255)
                    painter.setBrush(QBrush(color))
                    painter.setPen(QPen(QColor(0, 0, 0), 1))

                    # 绘制棋子（圆形）
                    painter.drawEllipse(center_x - 16, center_y - 16, 32, 32)

    def draw_last_move_marker(self, painter):
        """标记最后一步棋"""
        if self.parent.last_move:
            row, col = self.parent.last_move
            center_x = self.margin + col * self.cell_size
            center_y = self.margin + row * self.cell_size

            # 绘制红色小标记
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.setPen(QPen(QColor(255, 0, 0), 1))
            painter.drawEllipse(center_x - 3, center_y - 3, 6, 6)

    def mousePressEvent(self, event):
        """处理鼠标点击，计算落点并通知主窗口"""
        if event.button() == Qt.LeftButton and not self.parent.game_over:
            # 计算点击位置对应的棋盘坐标
            x = event.pos().x()
            y = event.pos().y()

            # 边界检查
            if x < self.margin - self.cell_size / 2 or x > self.margin + 14 * self.cell_size + self.cell_size / 2:
                return
            if y < self.margin - self.cell_size / 2 or y > self.margin + 14 * self.cell_size + self.cell_size / 2:
                return

            # 计算最近的交叉点
            col = round((x - self.margin) / self.cell_size)
            row = round((y - self.margin) / self.cell_size)

            # 确保坐标在有效范围内
            if 0 <= row < 15 and 0 <= col < 15:
                self.parent.place_stone(row, col)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 确保中文正常显示
    font = QFont("SimHei")
    app.setFont(font)
    game = GomokuGame()
    game.show()
    sys.exit(app.exec_())