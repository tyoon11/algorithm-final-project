class Player:
    def __init__(self, name):
        self.name = name  # 플레이어의 이름
        self.hand = []  # 플레이어의 손에 있는 카드 목록

    def receive_card(self, card):
        self.hand.append(card)  # 카드를 플레이어의 손에 추가

    def show_hand(self):
        return ', '.join(map(str, self.hand))  # 플레이어의 손에 있는 카드를 문자열로 반환
