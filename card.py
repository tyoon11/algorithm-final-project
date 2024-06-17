import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit  # 카드의 슈트 (Hearts, Diamonds, Clubs, Spades)
        self.rank = rank  # 카드의 랭크 (2, 3, ..., 10, jack, queen, king, ace)

    def __repr__(self):
        return f"{self.rank} of {self.suit}"  # 카드의 문자열 표현

    def value(self):
        card_values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        return card_values.index(self.rank) + 2  # 카드의 랭크 값을 정수로 반환

class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']
                      for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']]
        random.shuffle(self.cards)  # 덱을 초기화하고 카드를 섞음

    def deal(self):
        return self.cards.pop()  # 덱에서 카드를 한 장 뽑아 반환
