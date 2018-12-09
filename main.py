from random import shuffle
from itertools import zip_longest

#Important notes on the game.
#Blackjacks are paid out 3 to 2, or 1.5x the bet.
#Everyone's first card is face-up, second is face-down.
#A blackjack is a starting hand of an Ace and any 10-value card, and considere an automatic win (unless both blackjack).
#If the dealer's first card is an Ace, the player can make an insurance bet.
#Insurance bets may only be made up to half your original bet.
#If the dealer has a Blackjack and an insurance bet is made, the insurance bet pays out 2 to 1, or 2x the insurance bet.
#If the dealer doesn't have Blackjack, he takes all insurance bets.
#The dealer must take a hit when at or below 16, and stand when at 17 or higher.
#If the dealer busts (over 21), all bets are paid out 1 to 1.
#Winning a hand by a higher total than the dealer is paid out 1 to 1.
#Doubling down is one hit then a stand, with your bet being doubled.
#You may only surrender after your initial 2 cards.
#You may only split if you have two equal value cards.
#If you split Aces, you may only take one hit on each hand.
#When splitting, you split your two cards and place an equal second bet on the second hand.
#You may split up to having 4 hands in play.


class Card:

    suit_symbols = "\u2663\u2666\u2665\u2660"
    rank_symbols = [
        "A", "2", "3", "4", "5",
        "6", "7", "8", "9", "10",
        "J", "Q", "K"]

    # suit: 0..3 (clubs, diamonds, hearts, spades)
    # rank: 0..12
    # base_value for Aces is ALWAYS 11. Reduction is done in
    #  the hand.

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

        value = rank + 1
        if value > 10:
            self.base_value = 10
        elif value == 1:
            self.base_value = 11
        else:
            self.base_value = value

    def __str__(self):
        suit = Card.suit_symbols[self.suit]
        rank = Card.rank_symbols[self.rank]
        return rank + suit

class Hand:
    def __init__(self, name, *cards, times_split=0):
        self.name = name
        self.cards = []
        self.total = 0
        self.soft = False
        self.times_split = times_split
        
        for c in cards:
            self.add_card(c)
    
    def can_be_split(self):
        return (
            self.times_split == 0
            and len(self.cards) == 2
            and self.cards[0].rank == self.cards[1].rank)
    
    def split(self):
        splits = self.times_split + 1
        return (
            Hand(self.name + " Left",
                self.cards[0], times_split=splits),
            Hand(self.name + " Right",
                self.cards[1], times_split=splits))
    
    def add_card(self, card):
        self.cards.append(card)
        self.total += card.base_value
        
        if card.rank == 0:
            if self.soft:
                # If we already have an ace,
                # reduce it, since we'll only
                # ever have one non-reduced ace.
                self.total -= 10
            self.soft = True
        
        if self.total > 21 and self.soft:
            self.total -= 10
            self.soft = False
    
    def card_values(self):
        unreduced_ace = self.soft
        for card in self.cards:
            if card.rank == 0: # Ace
                if unreduced_ace:
                    unreduced_ace = False
                else:
                    yield card, 1
                    continue
            yield card, card.base_value
    
    def __getitem__(self, key):
        return self.cards[key]
    
    def __repr__(self):
        return f"Hand('{self.name}', [{','.join(map(str, self.cards))}])"

class PlayerAI:
    def __init__(self):
        self.my_hands = ()
        self.dealer_hand = None
        self.wins = 0
        self.losses = 0
        self.draws = 0
    
    def start_round(self, my_hand, dealer_hand):
        assert not self.my_hands and not self.dealer_hand
        self.my_hands = {my_hand}
        self.dealer_hand = dealer_hand
    
    def split_hand(self, old_hand, new_hand1, new_hand2):
        self.my_hands.remove(old_hand)
        self.my_hands.add(new_hand1)
        self.my_hands.add(new_hand2)
    
    def end_hand(self, my_hand):
        self.my_hands.remove(my_hand)
    
    def end_round(self, result):
        assert not self.my_hands
        self.dealer_hand = None
        if result > 0:
            self.wins += 1
        elif result < 0:
            self.losses += 1
        else:
            self.draws += 1
    
    CH_HIT = 0
    CH_STAND = 1
    CH_DOUBLE_DOWN = 2
    CH_SPLIT = 3
    
    choice_names = ["Hit", "Stand", "Double Down", "Split"]
    
    def choose_insurance(self):
        return False
    
    def choose_surrender(self):
        return False
    
    def choice(self, my_hand):
        raise NotImplementedError()

class PlayerAIStand(PlayerAI):
    def choice(self, my_hand):
        return PlayerAI.CH_STAND

class PlayerAIRules(PlayerAI):
    def choice(self, my_hand):
        dealer_card = self.dealer_hand[0].base_value
        
        if my_hand.total >= 17:
            return PlayerAI.CH_STAND
        if my_hand.total >= 13:
            if 2 <= dealer_card <= 6:
                return PlayerAI.CH_STAND
            else:
                return PlayerAI.CH_HIT
        if my_hand.total == 12:
            if 4 <= dealer_card <= 6:
                return PlayerAI.CH_STAND
            else:
                return PlayerAI.CH_HIT
        if my_hand.total == 11:
            if dealer_card == 11:
                return PlayerAI.CH_HIT
            else:
                return PlayerAI.CH_DOUBLE_DOWN
        if my_hand.total == 10:
            if 10 <= dealer_card <= 11:
                return PlayerAI.CH_HIT
            else:
                return PlayerAI.CH_DOUBLE_DOWN
        if my_hand.total == 9:
            if dealer_card == 2 or dealer_card >= 7:
                return PlayerAI.CH_HIT
            else:
                return PlayerAI.CH_DOUBLE_DOWN
        return PlayerAI.CH_HIT

class PlayerAIManual(PlayerAI):
    
    def choose_insurance(self):
        return input_yes_no("Make an insurance bet? (y/n)")
    
    def choose_surrender(self):
        return input_yes_no("Surrender? (y/n)")
    
    def choice(self, my_hand):
        print("Input player action: 0: Hit, 1: Stand, 2: Double Down, 3: Split")
        while True:
            player_decision = input()
            try:
                player_decision = int(player_decision)
            except ValueError:
                pass
            else:
                if 0 <= player_decision <= 3:
                    return player_decision
            print(f"'{player_decision}' is not a valid choice.")


def print_hands(*hands):
    # Semi-ugly code to print the hands next to each other.
    
    print()
    
    widths = [max(10, len(h.name)) for h in hands]
    sep = "    "

    print(end=" ")
    print(sep=sep, *(f"{h.name:{w}}" for w, h in zip(widths, hands)))

    print(end=" ")
    print(sep=sep, *("-" * w for w in widths))

    card_columns = (h.card_values() for h in hands)
    for card_row in zip_longest(*card_columns):
        print(end=" ")
        print(sep=sep, *(
            f"{str(card_value[0]):>{w - 5}} ({card_value[1]:>2})"
            if card_value else " " * w
            for w, card_value in zip(widths, card_row)))

    print(end=" ")
    print(sep=sep, *("-" * w for w in widths))

    print(end=" ")
    print(sep=sep, *(f"Total:{hand.total:>{w - 7}} "
        for w, hand in zip(widths, hands)))
    
    print()


def play_hand(player_ai, player, dealer, deck):
    #Player makes decision: 0: Hit, 1: Stand, 2: Double Down, 3: Split
    #Temporarily using manual player until AI logic is created.
    
    print_hands(player, dealer)
    player_decision = player_ai.choice(player)
    print("Player choice:", PlayerAI.choice_names[player_decision])

    #Player splits their hand.
    if player_decision == PlayerAI.CH_SPLIT:
        hand1, hand2 = player.split()
        player_ai.split_hand(player, hand1, hand2)
        
        hand1.add_card(deck.pop(0))
        hand2.add_card(deck.pop(0))
        
        return [
            *play_hand(player_ai, hand1, dealer, deck),
            *play_hand(player_ai, hand2, dealer, deck)]

    #Any other action is taken by the player.
    while player_decision != PlayerAI.CH_STAND:
        if player_decision == PlayerAI.CH_HIT:
            player.add_card(deck.pop(0))
        elif player_decision == PlayerAI.CH_DOUBLE_DOWN:
            #Double the player's bet.

            #Take one hit then stand.
            player.add_card(deck.pop(0))
            break
        #Check if the player busted before continuing.
        if player.total > 21:
            print("Hand busted")
            break
        
        print_hands(player, dealer)
        player_decision = player_ai.choice(player)
        print("Player choice:", PlayerAI.choice_names[player_decision])
    
    player_ai.end_hand(player)
    return [player]


def build_deck():
    deck = [Card(s, r) for r in range(13) for s in range(4)]
    shuffle(deck)
    return deck

def input_yes_no(prompt):
    if prompt:
        print(prompt)
    return input().strip().lower() in ("y", "yes")


def main(number_of_runs, ai_type):
    
    #Build the deck. Deck will be shuffled at the end of a round where half the deck or more has been used.
    deck = build_deck()
    shuffle_deck_at = 26
    
    player_ai = ai_type()

    #Run the simulation
    for run_number in range(number_of_runs):
        
        print("----------------------------------")
        
        #These represent the hands of the player and dealer, respectively.
        player = Hand("Player")
        dealer = Hand("Dealer")
        
        player_ai.start_round(player, dealer)

        #Player places their bet.
        funds = 100.0
        bet = 10.0

        #Deal cards out.
        #Deal 2 cards to the player and dealer, alternating
        if len(deck) <= shuffle_deck_at:
            deck = build_deck()
        player.add_card(deck.pop(0))
        dealer.add_card(deck.pop(0))
        player.add_card(deck.pop(0))
        dealer.add_card(deck.pop(0))

        #Player can choose to make an insurance bet.
        print_hands(player, dealer)
        if player_ai.choose_insurance():
            print("Player chooses to make an insurance bet.")
            insurance = 5.0
        else:
            print("Player does not choose to make an insurance bet.")
            insurance = 0.0

        #Check for Blackjack
        player_blackjack = player.total == 21
        dealer_blackjack = dealer.total == 21

        if player_blackjack and dealer_blackjack:
            print("Player and Dealer Blackjack, Round Draw")
            print_hands(player, dealer)
            funds += (2.0 * insurance)
            print("Ending Funds: " + str(funds))
            player_ai.end_hand(player)
            player_ai.end_round(0)
            continue
        elif player_blackjack:
            print("Player Blackjack, Player Wins")
            print_hands(player, dealer)
            funds -= insurance
            funds += (bet * 1.5)
            print("Ending Funds: " + str(funds))
            player_ai.end_hand(player)
            player_ai.end_round(+1)
            continue
        elif dealer_blackjack:
            print("Dealer Blackjack, Dealer Wins")
            print_hands(player, dealer)
            funds -= bet
            funds += (2.0 * insurance)
            print("Ending Funds: " + str(funds))
            player_ai.end_hand(player)
            player_ai.end_round(-1)
            continue
        elif insurance != 0:
            print("Dealer does not have Blackjack, Insurance forfeited")
            print_hands(player, dealer)
            funds -= insurance

        #Player plays out their hand.
        print_hands(player, dealer)
        if player_ai.choose_surrender():
            print("Player surrender, Dealer Wins")
            print_hands(player, dealer)
            funds -= (0.5 * bet)
            print("Ending Funds: " + str(funds))
            player_ai.end_hand(player)
            player_ai.end_round(-1)
            continue
        else:
            print("Player does not surrender.")
        
        results = play_hand(player_ai, player, dealer, deck)

        #Check what the outcome was.
        non_busted_hands = []
        for i, hand in enumerate(results):
            if hand.total > 21:
                print(f"Hand {i}: Player busts, Dealer Wins")
                print_hands(hand, dealer)
                funds -= bet
            else:
                non_busted_hands.append(results[i])

        #If there are no more live hands, continue
        if len(non_busted_hands) == 0:
            print("Ending Funds:", funds)
            player_ai.end_round(-1)
            continue

        #Dealer makes decision: hit when below 17 and stand when above 16.
        while dealer.total < 17:
            dealer.add_card(deck.pop(0))

        #Check if the dealer busted.
        if dealer.total > 21:
            print("Dealer Busts, Player Wins")
            for hand in non_busted_hands:
                print_hands(hand, dealer)
            funds += (bet * len(non_busted_hands))
            print("Ending Funds:", funds)
            player_ai.end_round(+1)
            continue

        #Compare the player's and dealer's hand.
        for hand in non_busted_hands:
            if hand.total > dealer.total:
                print("Player Total Higher, Player Wins")
                print_hands(hand, dealer)
                funds += bet
                player_ai.end_round(+1)
            elif hand.total < dealer.total:
                print("Dealer Total Higher, Dealer Wins")
                print_hands(hand, dealer)
                funds -= bet
                player_ai.end_round(-1)
            else:
                print("Player and Dealer Totals Equal, Draw")
                print_hands(hand, dealer)
                player_ai.end_round(0)
        print("Ending Funds:", funds)
    
    print("Player Wins:  ", player_ai.wins)
    print("Player Losses:", player_ai.losses)
    print("Player Draws: ", player_ai.draws)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    
    ai_type_group = parser.add_mutually_exclusive_group()
    ai_type_group.add_argument("-m", "--manual",
        help="replace the AI with manual player input",
        dest="ai_type", action="store_const", const=PlayerAIManual)
    ai_type_group.add_argument("-s", "--stand",
        help="use an AI that always stands",
        dest="ai_type", action="store_const", const=PlayerAIStand)
    ai_type_group.add_argument("-r", "--rules",
        help="use an AI that follows a set of rules",
        dest="ai_type", action="store_const", const=PlayerAIRules)
    parser.set_defaults(ai_type=PlayerAIRules)
    
    parser.add_argument("-n", "--num-rounds",
        dest="num_rounds", metavar="NUM",
        help="set the number of rounds to play (default 10)",
        type=int, default=10)
    args = parser.parse_args()
    
    main(args.num_rounds, args.ai_type)
































#This allows me to scroll, k
