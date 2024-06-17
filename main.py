import tkinter as tk
from gui import PokerGUI

root = tk.Tk()
app = PokerGUI(root)  # PokerGUI 인스턴스 생성 및 루트 윈도우에 연결
root.mainloop()  # Tkinter 이벤트 루프 시작
