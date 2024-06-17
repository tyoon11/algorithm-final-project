import random
from collections import deque, Counter
from itertools import combinations
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def value(self):
        card_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        return card_values.index(self.rank) + 2

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']
                      for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def receive_card(self, card):
        self.hand.append(card)

    def show_hand(self):
        return ', '.join(map(str, self.hand))


class HoldemGame:
    def __init__(self, players):
        self.deck = Deck()
        self.players = players
        self.pot = 0
        self.table_cards = []
        self.current_bet = 0
        self.scores = {}
        self.history = deque()  # 게임 상태를 저장하기 위한 스택
        self.state = "start"  # 게임 상태: start, flop, turn, river

    def start_game(self):
        # 각 플레이어에게 두 장의 카드를 나눠줌
        self.history.append((self.players.copy(), self.table_cards.copy()))
        for _ in range(2):
            for player in self.players:
                player.receive_card(self.deck.deal())
        self.state = "start"

    def betting_round(self):
        # 단순 베팅 로직 구현
        self.history.append((self.players.copy(), self.table_cards.copy()))
        pass

    def reveal_flop(self):
        if self.state != "start":
            raise Exception("플랍을 먼저 공개해야 합니다.")
        # 테이블에 세 장의 카드를 공개
        self.history.append((self.players.copy(), self.table_cards.copy()))
        self.table_cards.extend([self.deck.deal() for _ in range(3)])
        self.state = "flop"

    def reveal_turn(self):
        if self.state != "flop":
            raise Exception("턴을 공개하려면 플랍을 먼저 공개해야 합니다.")
        # 테이블에 한 장의 카드를 추가로 공개
        self.history.append((self.players.copy(), self.table_cards.copy()))
        self.table_cards.append(self.deck.deal())
        self.state = "turn"

    def reveal_river(self):
        if self.state != "turn":
            raise Exception("리버를 공개하려면 턴을 먼저 공개해야 합니다.")
        # 테이블에 마지막 한 장의 카드를 추가로 공개
        self.history.append((self.players.copy(), self.table_cards.copy()))
        self.table_cards.append(self.deck.deal())
        self.state = "river"

    def show_table(self):
        return ', '.join(map(str, self.table_cards))

    def calculate_scores(self):
        # 점수 계산 로직 구현 (족보 포함)
        self.history.append((self.players.copy(), self.table_cards.copy()))
        for player in self.players:
            best_hand = self.get_best_hand(player.hand + self.table_cards)
            self.scores[player.name] = self.hand_rank(best_hand)

    def hand_rank(self, hand):
        ranks = sorted([card.value() for card in hand], reverse=True)
        suits = [card.suit for card in hand]

        is_flush = len(set(suits)) == 1
        is_straight = ranks == list(range(ranks[0], ranks[0] - 5, -1))

        rank_counts = Counter(ranks)
        counts = sorted(rank_counts.values(), reverse=True)
        unique_ranks = sorted(rank_counts.keys(), reverse=True)

        if is_flush and is_straight:
            return (8, ranks)  # Straight flush
        elif counts == [4, 1]:
            return (7, unique_ranks)  # Four of a kind
        elif counts == [3, 2]:
            return (6, unique_ranks)  # Full house
        elif is_flush:
            return (5, ranks)  # Flush
        elif is_straight:
            return (4, ranks)  # Straight
        elif counts == [3, 1, 1]:
            return (3, unique_ranks)  # Three of a kind
        elif counts == [2, 2, 1]:
            return (2, unique_ranks)  # Two pair
        elif counts == [2, 1, 1, 1]:
            return (1, unique_ranks)  # One pair
        else:
            return (0, ranks)  # High card

    def get_best_hand(self, cards):
        return max(combinations(cards, 5), key=self.hand_rank)

    def determine_winner(self):
        # 승자 결정 로직 구현
        self.calculate_scores()
        winner = max(self.scores, key=self.scores.get)
        return winner, self.scores[winner]

    def calculate_win_probability(self):
        # 각 플레이어의 승리 확률 계산
        remaining_deck = self.deck.cards.copy()
        total_simulations = 1000
        win_counts = {player.name: 0 for player in self.players}

        for _ in range(total_simulations):
            random.shuffle(remaining_deck)
            for player in self.players:
                simulated_hand = player.hand + self.table_cards + remaining_deck[:5 - len(self.table_cards)]
                best_hand = self.get_best_hand(simulated_hand)
                win_counts[player.name] += self.hand_rank(best_hand)[0]  # 랭킹 점수의 첫 번째 요소 사용

        total_score = sum(win_counts.values())
        for player in self.players:
            win_counts[player.name] = (win_counts[player.name] / total_score) * 100

        return win_counts

    def undo(self):
        # 게임 상태를 이전 상태로 되돌리기
        if self.history:
            previous_state = self.history.pop()
            self.players, self.table_cards = previous_state


# GUI 구현
class PokerGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("홀덤 게임 관리 시스템")
        self.master.geometry("1200x800")  # 윈도우 크기 조정

        self.players = [Player("Alice"), Player("Bob")]
        self.game = HoldemGame(self.players)
        self.game.start_game()

        self.card_images = {}
        self.load_card_images()

        self.setup_ui()

    def load_card_images(self):
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        for suit in suits:
            for rank in ranks:
                card_name = f"{rank}_of_{suit}.png"
                image_path = f"images/{card_name}"
                image = Image.open(image_path)
                image = image.resize((100, 150), Image.ANTIALIAS)  # 이미지 크기 조정
                self.card_images[f"{rank} of {suit}"] = ImageTk.PhotoImage(image)

    def setup_ui(self):


        self.player_frame_top = tk.Frame(self.master)
        self.player_frame_top.pack(side=tk.TOP, pady=20)

        self.player_frame_bottom = tk.Frame(self.master)
        self.player_frame_bottom.pack(side=tk.BOTTOM, pady=20)

        self.table_frame = tk.Frame(self.master)
        self.table_frame.pack(pady=20)

        self.table_label = tk.Label(self.table_frame, text="Table Cards: ")
        self.table_label.pack()

        self.player_labels = []
        self.prob_labels = []
        self.hand_frames = []
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

        self.update_ui()

    def reveal_flop(self):
        try:
            self.game.reveal_flop()
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reveal_turn(self):
        try:
            self.game.reveal_turn()
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reveal_river(self):
        try:
            self.game.reveal_river()
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def determine_winner(self):
        try:
            winner, score = self.game.determine_winner()
            messagebox.showinfo("Winner", f"Winner: {winner} with score: {score}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_ui(self):
        self.update_table_cards()
        self.update_player_hands()
        win_probs = self.game.calculate_win_probability()
        for i, player in enumerate(self.players):
            self.prob_labels[i].config(text=f"{player.name}'s Win Probability: {win_probs[player.name]:.2f}%")

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


if __name__ == "__main__":
    root = tk.Tk()
    app = PokerGUI(root)
    root.mainloop()
