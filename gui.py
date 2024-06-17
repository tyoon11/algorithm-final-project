import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from game import HoldemGame
from player import Player


class PokerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("홀덤 게임 관리 시스템")
        self.master.geometry("1200x800")  # 윈도우 크기 조정

        self.players = [Player("Alice"), Player("Bob")]  # 플레이어 생성
        self.game = HoldemGame(self.players)  # 게임 인스턴스 생성
        self.game.start_game()  # 게임 시작

        self.card_images = {}
        self.load_card_images()  # 카드 이미지 로드

        self.setup_ui()  # UI 설정

    def load_card_images(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        for suit in suits:
            for rank in ranks:
                card_name = f"{rank}_of_{suit}.png"
                image_path = f"images/{card_name}"
                image = Image.open(image_path)
                image = image.resize((100, 150))  # 이미지 크기 조정
                self.card_images[f"{rank} of {suit}"] = ImageTk.PhotoImage(image)  # 카드 이미지를 딕셔너리에 저장

    def setup_ui(self):
        self.player_frame_top = tk.Frame(self.master)
        self.player_frame_top.pack(side=tk.TOP, pady=20)

        self.table_frame = tk.Frame(self.master)
        self.table_frame.pack(pady=20)

        self.player_frame_bottom = tk.Frame(self.master)
        self.player_frame_bottom.pack(side=tk.BOTTOM, pady=20)

        self.table_label = tk.Label(self.table_frame, text="Table Cards: ")
        self.table_label.pack()

        self.player_labels = []
        self.prob_labels = []
        self.hand_frames = []
        self.hand_description_labels = []  # 각 플레이어의 핸드 족보를 표시할 레이블

        for i, player in enumerate(self.players):
            if i == 0:
                player_frame = self.player_frame_top
            else:
                player_frame = self.player_frame_bottom

            hand_frame = tk.Frame(player_frame)
            hand_frame.pack()
            hand_cards = []
            for _ in range(2):
                card_label = tk.Label(hand_frame)
                card_label.pack(side=tk.LEFT)
                hand_cards.append(card_label)
            self.hand_frames.append(hand_cards)
            player_label = tk.Label(player_frame, text=f"{player.name}'s Hand:")
            player_label.pack()
            self.player_labels.append(player_label)
            prob_label = tk.Label(player_frame, text=f"{player.name}'s Win Probability: 0%")
            prob_label.pack()
            self.prob_labels.append(prob_label)
            hand_description_label = tk.Label(player_frame, text="Hand Description: ")
            hand_description_label.pack()
            self.hand_description_labels.append(hand_description_label)

        self.table_cards_labels = []
        for _ in range(5):
            card_label = tk.Label(self.table_frame)
            card_label.pack(side=tk.LEFT)
            self.table_cards_labels.append(card_label)

        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=10)

        self.flop_button = tk.Button(self.button_frame, text="Reveal Flop", command=self.reveal_flop)
        self.flop_button.pack(side=tk.LEFT, padx=5)
        self.turn_button = tk.Button(self.button_frame, text="Reveal Turn", command=self.reveal_turn)
        self.turn_button.pack(side=tk.LEFT, padx=5)
        self.river_button = tk.Button(self.button_frame, text="Reveal River", command=self.reveal_river)
        self.river_button.pack(side=tk.LEFT, padx=5)
        self.winner_button = tk.Button(self.button_frame, text="Determine Winner", command=self.determine_winner)
        self.winner_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = tk.Button(self.button_frame, text="Reset", command=self.reset)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.update_ui()

    def reset(self):
        self.game.reset_game()  # 게임 초기화
        self.game.start_game()  # 게임 시작
        self.update_ui()  # UI 업데이트

    def reveal_flop(self):
        try:
            self.game.reveal_flop()  # 플랍 공개
            self.update_ui()  # UI 업데이트
        except Exception as e:
            messagebox.showerror("Error", str(e))  # 예외 발생 시 에러 메시지 박스

    def reveal_turn(self):
        try:
            self.game.reveal_turn()  # 턴 공개
            self.update_ui()  # UI 업데이트
        except Exception as e:
            messagebox.showerror("Error", str(e))  # 예외 발생 시 에러 메시지 박스

    def reveal_river(self):
        try:
            self.game.reveal_river()  # 리버 공개
            self.update_ui()  # UI 업데이트
        except Exception as e:
            messagebox.showerror("Error", str(e))  # 예외 발생 시 에러 메시지 박스

    def determine_winner(self):
        try:
            winner, score = self.game.determine_winner()  # 승자 결정
            hand_description = self.game.hand_description(self.game.get_best_hand(
                self.players[[player.name for player in self.players].index(winner)].hand + self.game.table_cards))
            messagebox.showinfo("Winner", f"Winner: {winner} with hand: {hand_description}")  # 승자 정보 표시
        except Exception as e:
            messagebox.showerror("Error", str(e))  # 예외 발생 시 에러 메시지 박스

    def update_ui(self):
        self.update_table_cards()  # 테이블 카드 업데이트
        self.update_player_hands()  # 플레이어 핸드 업데이트
        win_probs = self.game.calculate_win_probability()  # 승리 확률 계산
        for i, player in enumerate(self.players):
            self.prob_labels[i].config(text=f"{player.name}'s Win Probability: {win_probs[player.name]:.2f}%")
            if len(self.game.table_cards) > 0:
                best_hand = self.game.get_best_hand(player.hand + self.game.table_cards)
                hand_description = self.game.hand_description(best_hand)
            else:
                hand_description = "No table cards yet"
            self.hand_description_labels[i].config(text=f"Hand Description: {hand_description}")

    def update_table_cards(self):
        for i, card_label in enumerate(self.table_cards_labels):
            if i < len(self.game.table_cards):
                card = self.game.table_cards[i]
                card_label.config(image=self.card_images[str(card)])
            else:
                card_label.config(image='')

    def update_player_hands(self):
        for i, player in enumerate(self.players):
            hand_frames = self.hand_frames[i]
            for j, card_label in enumerate(hand_frames):
                card = player.hand[j]
                card_label.config(image=self.card_images[str(card)])
