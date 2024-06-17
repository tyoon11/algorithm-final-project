import random
from collections import deque, Counter
from itertools import combinations
from card import Deck

class HoldemGame:
    def __init__(self, players):
        self.players = players  # 플레이어 목록
        self.reset_game()

    def reset_game(self):
        self.deck = Deck()  # 새로운 덱을 생성
        self.pot = 0  # 현재 판에 걸린 총 금액
        self.table_cards = []  # 테이블에 공개된 카드 목록
        self.current_bet = 0  # 현재 베팅 금액
        self.scores = {}  # 각 플레이어의 점수
        self.history = deque()  # 게임의 히스토리
        self.state = "start"  # 현재 게임 상태

        for player in self.players:
            player.hand = []  # 각 플레이어의 손에 있는 카드를 초기화
            player.current_bet = 0  # 각 플레이어의 현재 베팅 금액을 초기화
            player.folded = False  # 각 플레이어의 폴드 상태를 초기화

    def start_game(self):
        self.history.append((self.players.copy(), self.table_cards.copy()))  # 현재 상태를 히스토리에 저장
        for _ in range(2):
            for player in self.players:
                player.receive_card(self.deck.deal())  # 각 플레이어에게 2장의 카드를 나눠줌
        self.state = "start"

    def reveal_flop(self):
        if self.state != "start":
            raise Exception("플랍을 먼저 공개해야 합니다.")  # 현재 상태가 'start'가 아니면 예외를 발생시킴
        self.history.append((self.players.copy(), self.table_cards.copy()))  # 현재 상태를 히스토리에 저장
        self.table_cards.extend([self.deck.deal() for _ in range(3)])  # 테이블에 3장의 카드를 공개
        self.state = "flop"

    def reveal_turn(self):
        if self.state != "flop":
            raise Exception("턴을 공개하려면 플랍을 먼저 공개해야 합니다.")  # 현재 상태가 'flop'이 아니면 예외를 발생시킴
        self.history.append((self.players.copy(), self.table_cards.copy()))  # 현재 상태를 히스토리에 저장
        self.table_cards.append(self.deck.deal())  # 테이블에 1장의 카드를 추가로 공개
        self.state = "turn"

    def reveal_river(self):
        if self.state != "turn":
            raise Exception("리버를 공개하려면 턴을 먼저 공개해야 합니다.")  # 현재 상태가 'turn'이 아니면 예외를 발생시킴
        self.history.append((self.players.copy(), self.table_cards.copy()))  # 현재 상태를 히스토리에 저장
        self.table_cards.append(self.deck.deal())  # 테이블에 1장의 카드를 추가로 공개
        self.state = "river"

    def show_table(self):
        return ', '.join(map(str, self.table_cards))  # 테이블에 공개된 카드 목록을 문자열로 반환

    def calculate_scores(self):
        self.history.append((self.players.copy(), self.table_cards.copy()))  # 현재 상태를 히스토리에 저장
        for player in self.players:
            best_hand = self.get_best_hand(player.hand + self.table_cards)  # 플레이어의 최상의 핸드를 계산
            self.scores[player.name] = self.hand_rank(best_hand)  # 플레이어의 점수를 저장

    def hand_rank(self, hand):
        ranks = sorted([card.value() for card in hand], reverse=True)  # 카드의 랭크 값을 정렬
        suits = [card.suit for card in hand]  # 카드의 슈트 목록

        is_flush = len(set(suits)) == 1  # 플러시 여부 확인
        is_straight = ranks == list(range(ranks[0], ranks[0] - 5, -1))  # 스트레이트 여부 확인

        rank_counts = Counter(ranks)  # 카드 랭크의 빈도수 계산
        counts = sorted(rank_counts.values(), reverse=True)  # 빈도수를 내림차순으로 정렬
        unique_ranks = sorted(rank_counts.keys(), reverse=True)  # 유니크한 랭크 값을 내림차순으로 정렬

        if is_flush and is_straight:
            return (8, unique_ranks)  # 스트레이트 플러시
        elif counts == [4, 1]:
            return (7, unique_ranks)  # 포카드
        elif counts == [3, 2]:
            return (6, unique_ranks)  # 풀하우스
        elif is_flush:
            return (5, unique_ranks)  # 플러시
        elif is_straight:
            return (4, unique_ranks)  # 스트레이트
        elif counts == [3, 1, 1]:
            return (3, unique_ranks)  # 트리플
        elif counts == [2, 2, 1]:
            return (2, unique_ranks)  # 투페어
        elif counts == [2, 1, 1, 1]:
            return (1, unique_ranks)  # 원페어
        else:
            return (0, unique_ranks)  # 하이카드

    def get_best_hand(self, cards):
        if len(cards) < 5:
            return cards  # 카드가 5장 미만일 경우 그대로 반환
        return max(combinations(cards, 5), key=self.hand_rank)  # 최상의 5장 조합을 반환

    def determine_winner(self):
        self.calculate_scores()  # 점수를 계산
        winner = max(self.scores, key=lambda name: self.scores[name])  # 가장 높은 점수를 가진 플레이어를 승자로 설정
        return winner, self.scores[winner]  # 승자와 점수를 반환

    def calculate_win_probability(self):
        remaining_deck = self.deck.cards.copy()  # 남은 덱을 복사
        total_simulations = 1000  # 시뮬레이션 횟수
        win_counts = {player.name: 0 for player in self.players}  # 각 플레이어의 승리 횟수 초기화

        for _ in range(total_simulations):
            random.shuffle(remaining_deck)  # 남은 덱을 섞음
            for player in self.players:
                simulated_hand = player.hand + self.table_cards + remaining_deck[:5-len(self.table_cards)]  # 시뮬레이션 핸드 생성
                best_hand = self.get_best_hand(simulated_hand)  # 최상의 핸드 계산
                win_counts[player.name] += self.hand_rank(best_hand)[0]  # 승리 횟수 증가

        total_score = sum(win_counts.values())  # 총 승리 횟수 계산
        for player in self.players:
            win_counts[player.name] = (win_counts[player.name] / total_score) * 100  # 승리 확률 계산

        return win_counts

    def hand_description(self, hand):
        ranks = sorted([card.value() for card in hand], reverse=True)  # 카드의 랭크 값을 정렬
        suits = [card.suit for card in hand]  # 카드의 슈트 목록

        is_flush = len(set(suits)) == 1  # 플러시 여부 확인
        is_straight = ranks == list(range(ranks[0], ranks[0] - 5, -1))  # 스트레이트 여부 확인

        rank_counts = Counter(ranks)  # 카드 랭크의 빈도수 계산
        counts = sorted(rank_counts.values(), reverse=True)  # 빈도수를 내림차순으로 정렬
        unique_ranks = sorted(rank_counts.keys(), reverse=True)  # 유니크한 랭크 값을 내림차순으로 정렬

        rank_to_str = {14: 'A', 13: 'K', 12: 'Q', 11: 'J'}

        best_rank_str = rank_to_str.get(unique_ranks[0], str(unique_ranks[0]))  # 가장 높은 랭크를 문자열로 변환

        if is_flush and is_straight:
            return f"Straight flush, {best_rank_str} high"
        elif counts == [4, 1]:
            return f"Four of a kind, {rank_to_str.get(unique_ranks[0], str(unique_ranks[0]))}s"
        elif counts == [3, 2]:
            return f"Full house, {rank_to_str.get(unique_ranks[0], str(unique_ranks[0]))}s over {rank_to_str.get(unique_ranks[1], str(unique_ranks[1]))}s"
        elif is_flush:
            return f"Flush, {best_rank_str} high"
        elif is_straight:
            return f"Straight, {best_rank_str} high"
        elif counts == [3, 1, 1]:
            return f"Three of a kind, {rank_to_str.get(unique_ranks[0], str(unique_ranks[0]))}s"
        elif counts == [2, 2, 1]:
            return f"Two pair, {rank_to_str.get(unique_ranks[0], str(unique_ranks[0]))}s and {rank_to_str.get(unique_ranks[1], str(unique_ranks[1]))}s"
        elif counts == [2, 1, 1, 1]:
            return f"One pair, {rank_to_str.get(unique_ranks[0], str(unique_ranks[0]))}s"
        else:
            return f"{rank_to_str.get(unique_ranks[0], str(unique_ranks[0]))} high"

    def undo(self):
        if self.history:
            previous_state = self.history.pop()  # 이전 상태를 히스토리에서 꺼냄
            self.players, self.table_cards = previous_state  # 이전 상태로 복원
