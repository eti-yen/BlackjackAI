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

def print_hands(*hands):
    # Semi-ugly code to print the hands next to each other.

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


def play_hand(player, dealer, deck):
    #Player makes decision: 0: Hit, 1: Stand, 2: Double Down, 3: Split
    #Temporarily using manual player until AI logic is created.
    print_hands(player, dealer)
    print("Input player action: 0: Hit, 1: Stand, 2: Double Down, 3: Split")
    player_decision = input()
    print("\n\n")

    #Player splits their hand.
    if player_decision == "3":
        hand1, hand2 = player.split()
        hand1.add_card(deck[0])
        deck.pop(0)
        hand2.add_card(deck[0])
        deck.pop(0)
        return [
            *play_hand(hand1, dealer, deck),
            *play_hand(hand2, dealer, deck)]

    #Any other action is taken by the player.
    while player_decision != "1":
        if player_decision == "0":
            player.add_card(deck[0])
            deck.pop(0)
        elif player_decision == "2":
            #Double the player's bet.

            #Take one hit then stand.
            player.add_card(deck[0])
            deck.pop(0)
            break
        #Check if the player busted before continuing.
        if player.total > 21:
            print("Hand busted")
            break
        #Temporarily using manual player until AI logic is created.
        print_hands(player, dealer)
        print("Input player action: 0: Hit, 1: Stand, 2: Double Down, 3: Split")
        player_decision = input()
        print("\n\n")
    return [player]


def build_deck():
    deck = [Card(s, r) for r in range(13) for s in range(4)]
    shuffle(deck)
    return deck

def input_yes_no(prompt):
    if prompt:
        print(prompt)
    return input().strip().lower() in ("y", "yes")


def main():
    #The number of times the simulation should be run.
    number_of_runs = 1

    #Build the deck. Deck will be shuffled at the end of a round where half the deck or more has been used.
    deck = build_deck()
    shuffle_deck_at = 26

    #Run the simulation
    for run_number in range(number_of_runs):
        #These represent the hands of the player and dealer, respectively.
        player = Hand("Player")
        dealer = Hand("Dealer")

        #Player places their bet.
        funds = 100.0
        bet = 10.0

        #Deal cards out.
        #Deal 2 cards to the player and dealer, alternating
        if len(deck) <= shuffle_deck_at:
            deck = build_deck()
        player.add_card(deck[0])
        deck.pop(0)
        dealer.add_card(deck[0])
        deck.pop(0)
        player.add_card(deck[0])
        deck.pop(0)
        dealer.add_card(deck[0])
        deck.pop(0)

        #Player can choose to make an insurance bet.
        print_hands(player, dealer)
        if input_yes_no("Make an insurance bet? (y/n)"):
            insurance = 5.0
        else:
            insurance = 0.0
        print("\n\n")

        #Check for Blackjack
        player_blackjack = player.total == 21
        dealer_blackjack = dealer.total == 21

        if player_blackjack and dealer_blackjack:
            print("Player and Dealer Blackjack, Round Draw")
            print_hands(player, dealer)
            funds += (2.0 * insurance)
            print("Ending Funds: " + str(funds))
            continue
        elif player_blackjack:
            print("Player Blackjack, Player Wins")
            print_hands(player, dealer)
            funds -= insurance
            funds += (bet * 1.5)
            print("Ending Funds: " + str(funds))
            continue
        elif dealer_blackjack:
            print("Dealer Blackjack, Dealer Wins")
            print_hands(player, dealer)
            funds -= bet
            funds += (2.0 * insurance)
            print("Ending Funds: " + str(funds))
            continue
        elif insurance != 0:
            print("Dealer does not have Blackjack, Insurance forfeited")
            print_hands(player, dealer)
            funds -= insurance

        #Player plays out their hand.
        print_hands(player, dealer)
        if input_yes_no("Surrender? (y/n)"):
            print("Player surrender, Dealer Wins")
            print_hands(player, dealer)
            funds -= (0.5 * bet)
            print("Ending Funds: " + str(funds))
            continue
        print("\n\n")
        results = play_hand(player, dealer, deck)

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
            continue

        #Dealer makes decision: hit when below 17 and stand when above 16.
        while dealer.total < 17:
            dealer.add_card(deck[0])
            deck.pop(0)

        #Check if the dealer busted.
        if dealer.total > 21:
            print("Dealer Busts, Player Wins")
            for hand in non_busted_hands:
                print_hands(hand, dealer)
            funds += (bet * len(non_busted_hands))
            print("Ending Funds:", funds)
            continue

        #Compare the player's and dealer's hand.
        for hand in non_busted_hands:
            if hand.total > dealer.total:
                print("Player Total Higher, Player Wins")
                print_hands(hand, dealer)
                funds += bet
            elif hand.total < dealer.total:
                print("Dealer Total Higher, Dealer Wins")
                print_hands(hand, dealer)
                funds -= bet
            else:
                print("Player and Dealer Totals Equal, Draw")
                print_hands(hand, dealer)
        print("Ending Funds:", funds)

if __name__ == '__main__':
    main()
































#This allows me to scroll, k
