import itertools
import random
from util import check_scores
class Player:
    def __init__(self, name):
        self.name = name
        self.roll = False
        self.rolls_left = 3
        self.dice_selected = [False, False, False, False, False]
        self.selected_choice = [False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.possible = [True, True, True, True, True, True, False, False, False, False, False, False, True]
        self.done = [False, False, False, False, False, False, False, False, False, False, False, False, False]
        self.score = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.totals = [0, 0, 0, 0, 0, 0, 0]
        self.clicked = -1
        self.current_score = 0
        self.something_selected = False
        self.bonus_time = False
        self.numbers = [0, 0, 0, 0, 0]

    def score_combination(self, dice):
        counts = {i: dice.count(i) for i in range(1, 7)}
        sorted_dice = sorted(set(dice))

        small_straight = any(
            sorted_dice[i:i + 4] == list(range(sorted_dice[i], sorted_dice[i] + 4))
            for i in range(len(sorted_dice) - 3)
        )
        large_straight = any(
            sorted_dice[i:i + 5] == list(range(sorted_dice[i], sorted_dice[i] + 5))
            for i in range(len(sorted_dice) - 4)
        )
        scores = {
            "ones": counts[1] * 1,
            "twos": counts[2] * 2,
            "threes": counts[3] * 3,
            "fours": counts[4] * 4,
            "fives": counts[5] * 5,
            "sixes": counts[6] * 6,
            "three_of_a_kind": sum(dice) if max(counts.values()) >= 3 else 0,
            "four_of_a_kind": sum(dice) if max(counts.values()) >= 4 else 0,
            "small_straight": 30 if small_straight else 0,
            "large_straight": 40 if large_straight else 0,
            "yahtzee": 50 if max(counts.values()) == 5 else 0,
            "chance": sum(dice),
        }
        return max(scores.values())

    def is_sequence(self, dice, length):
        sorted_dice = sorted(set(dice))
        for i in range(len(sorted_dice) - length + 1):
            if sorted_dice[i:i + length] == list(range(sorted_dice[i], sorted_dice[i] + length)):
                return sorted_dice[i:i + length]
        return []

    def generate_combinations(self, dice):
        return [list(comb) for r in range(len(dice)) for comb in itertools.combinations(dice, r)]

    def computer_choice(self, dice):
        counts = {value: dice.count(value) for value in set(dice)}
        of_one_kind_pos = [self.possible[6], self.possible[7], self.possible[8], self.possible[11]]
        if any(of_one_kind_pos) or self.done[11]:
            for count_value in [4, 3, 2]:
                matches = [value for value, count in counts.items() if count == count_value]
                if matches:
                    return [value for value in dice if value in matches]

        if self.possible[9] or self.possible[10]:
            for length in [4, 3, 2]:
                sequence = self.is_sequence(dice, length)
                if sequence:
                    return sequence

        combinations = self.generate_combinations(dice)
        scored_combinations = [(comb, self.score_combination(comb)) for comb in combinations]

        max_score = max(score for _, score in scored_combinations)
        weights = [score / max_score for _, score in scored_combinations]
        weights = [w + random.uniform(0, 0.2) for w in weights]

        chosen_comb = random.choices(scored_combinations, weights=weights, k=1)[0][0]
        return chosen_comb

    def ai_make_choice(self):
        choice = self.computer_choice(self.numbers)

        self.dice_selected = [False] * 5
        temp_numbers = self.numbers.copy()

        for value in choice:
            if value in temp_numbers:
                index = temp_numbers.index(value)
                self.dice_selected[index] = True
                temp_numbers[index] = None

    def minimax(self, depth, maximizing_player, current_numbers, possible_categories, scores):
        if depth == 0 or not possible_categories:
            return sum(scores)

        if maximizing_player:
            max_eval = float('-inf')
            for category in possible_categories:
                temp_scores = scores[:]
                temp_scores[category] = check_scores(
                    [j == category for j in range(len(scores))],
                    current_numbers, [True] * len(scores), 0
                )
                eval = self.minimax(depth - 1, False, current_numbers,
                                    [c for c in possible_categories if c != category], temp_scores)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for category in possible_categories:
                temp_scores = scores[:]
                temp_scores[category] = check_scores(
                    [j == category for j in range(len(scores))],
                    current_numbers, [True] * len(scores), 0
                )
                eval = self.minimax(depth - 1, True, current_numbers, [c for c in possible_categories if c != category],
                                    temp_scores)
                min_eval = min(min_eval, eval)
            return min_eval

    def choose_category(self):
        for i in range(len(self.selected_choice)):
             self.selected_choice[i] = False
        best_score = float('-inf')
        best_category = -1
        available_categories = [i for i in range(len(self.possible)) if self.possible[i] and not self.done[i]]

        for category in available_categories:
            temp_scores = self.score[:]
            temp_scores[category] = check_scores(
                [j == category for j in range(len(self.possible))],
                self.numbers, self.possible, 0
            )
            eval = self.minimax(1, False, self.numbers, [c for c in available_categories if c != category], temp_scores)
            if eval > best_score:
                best_score = eval
                best_category = category
        if best_category != -1:
            self.selected_choice[best_category] = True
        else:
            min_score = float('inf')
            fallback_category = -1

            for i in range(len(self.done)):
                if not self.done[i]:
                    temp_score = check_scores(
                        [j == i for j in range(len(self.possible))],
                        self.numbers, [True] * len(self.possible), 0
                    )
                    if temp_score < min_score:
                        min_score = temp_score
                        fallback_category = i

            if fallback_category != -1:
                self.selected_choice[fallback_category] = True




