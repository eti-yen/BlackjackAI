import sys
from random import shuffle
import itertools

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

def map_value(x, l1, h1, l2, h2, *, clamp=True):
    i = (x - l1) / (h1 - l1)
    if clamp:
        i = max(0, min(1, i))
    return i * (h2 - l2) + l2

class Card:

    suit_symbols = "♣♦♥♠"
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
        
        if self.base_value <= 6:
            self.cc_value = +1
        elif self.base_value >= 10:
            self.cc_value = -1
        else:
            self.cc_value = 0

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
        self.bet = None
        
        for c in cards:
            self.add_card(c)
    
    def can_be_split(self):
        return (
            self.times_split == 0
            and len(self.cards) == 2
            and self.cards[0].base_value == self.cards[1].base_value)
    
    def split(self):
        splits = self.times_split + 1
        
        left = Hand(self.name + " Left",
            self.cards[0], times_split=splits)
        right = Hand(self.name + " Right",
            self.cards[1], times_split=splits)
        left.bet = right.bet = self.bet
        
        return left, right
    
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
    
    def __len__(self):
        return len(self.cards)
    
    def __repr__(self):
        return f"Hand('{self.name}', [{','.join(map(str, self.cards))}])"

class PlayerAI:
    def __init__(self, funds=0):
        self.my_hands = ()
        self.dealer_hand = None
        
        self.wins = 0
        self.losses = 0
        self.draws = 0
        
        self.funds = funds
    
    def deck_shuffled(self, num_decks):
        pass
    
    def view_card(self, card):
        pass
    
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
    
    def make_bet(self):
        raise NotImplementedError()
    
    def choose_insurance(self):
        return False
    
    def choose_surrender(self):
        return False
    
    def choice(self, my_hand):
        raise NotImplementedError()

class PlayerAIStand(PlayerAI):
    def choice(self, my_hand):
        return PlayerAI.CH_STAND
    
    def make_bet(self):
        return 10

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
    
    def make_bet(self):
        return 10

class PlayerAICardCounting(PlayerAI):
    def deck_shuffled(self, num_decks):
        self.num_decks = num_decks
        self.running_count = 0
        self.cards_played = 0
    
    def view_card(self, card):
        self.running_count += card.cc_value
        self.cards_played += 1
    
    @property
    def true_count(self):
        return self.running_count // (self.num_decks - (cards_played // 52))
    
    def make_bet(self):
        return map_value(self.true_count,
            0, 10,
            10, 10000)
    
    def choose_surrender(self):
        assert len(self.my_hands) == 1
        hand = next(iter(self.my_hands))
        
        if hand.total == 16:
            return self.dealer_hand[0].base_value >= 9
        if hand.total == 15:
            return self.dealer_hand[0].base_value >= 10
        return False
    
    def choice(self, my_hand):
        assert my_hand.total != 21
        
        dealer_value = self.dealer_hand[0].base_value
        
        # Splits?
        if my_hand.can_be_split():
            pair_type = my_hand[0].base_value
            
            if pair_type == 11:
                return PlayerAI.CH_SPLIT
            elif pair_type == 10:
                pass # Never split
            elif pair_type == 9:
                if dealer_value <= 9 and dealer_value != 7:
                    return PlayerAI.CH_SPLIT
                else:
                    return PlayerAI.CH_STAND
            elif pair_type == 8:
                return PlayerAI.CH_SPLIT
            # For 7, see the else block
            elif pair_type == 6:
                if dealer_value <= 6:
                    return PlayerAI.CH_SPLIT
                else:
                    return PlayerAI.CH_HIT
            elif pair_type == 5:
                if dealer_value <= 9:
                    return PlayerAI.CH_DOUBLE_DOWN
                else:
                    return PlayerAI.CH_HIT
            elif pair_type == 4:
                if 5 <= dealer_value <= 6:
                    return PlayerAI.CH_SPLIT
                else:
                    return PlayerAI.CH_HIT
            else: # 7, 3, 2
                if dealer_value <= 7:
                    return PlayerAI.CH_SPLIT
                else:
                    return PlayerAI.CH_HIT
        
        if my_hand.soft:
            if my_hand.total == 20:
                return PlayerAI.CH_STAND
            if my_hand.total == 19:
                if dealer_value == 6:
                    return PlayerAI.CH_DOUBLE_DOWN
                else:
                    return PlayerAI.CH_STAND
            if my_hand.total == 18:
                if dealer_value <= 6:
                    return PlayerAI.CH_DOUBLE_DOWN
                elif dealer_value >= 9:
                    return PlayerAI.CH_HIT
                else:
                    return PlayerAI.CH_STAND
            else:
                low = (24 - my_hand.total) // 2
                if low <= dealer_value <= 6:
                    return PlayerAI.CH_DOUBLE_DOWN
                else:
                    return PlayerAI.CH_HIT
        
        if my_hand.total >= 17:
            return PlayerAI.CH_STAND
        elif my_hand.total >= 13:
            if dealer_value <= 6:
                return PlayerAI.CH_STAND
            else:
                return PlayerAI.CH_HIT
        elif my_hand.total >= 12:
            if 4 <= dealer_value <= 6:
                return PlayerAI.CH_STAND
            else:
                return PlayerAI.CH_HIT
        elif my_hand.total == 11:
            return PlayerAI.CH_DOUBLE_DOWN
        elif my_hand.total == 10:
            if dealer_value <= 9:
                return PlayerAI.CH_STAND
            else:
                return PlayerAI.CH_HIT
        elif my_hand.total == 9:
            if 3 <= dealer_value <= 6:
                return PlayerAI.CH_STAND
            else:
                return PlayerAI.CH_HIT
        else:
            return PlayerAI.CH_HIT

class PlayerAIManual(PlayerAI):
    
    def choose_insurance(self):
        return input_yes_no("Make an insurance bet? (y/n)")
    
    def choose_surrender(self):
        return input_yes_no("Surrender? (y/n)")
    
    def make_bet(self):
        while True:
            bet = input("Enter your bet amount: ")
            try:
                bet = int(bet)
            except ValueError:
                print(f"'{bet}' is not a valid amount.")
            else:
                return bet
    
    def choice(self, my_hand):
        print("Input player action: 0: Hit, 1: Stand, 2: Double Down",
            ", 3: Split" if my_hand.can_be_split() else "", sep="")
        while True:
            player_decision = input()
            try:
                player_decision = int(player_decision)
            except ValueError:
                pass
            else:
                if my_hand.can_be_split() and player_decision == 3:
                    return player_decision
                if 0 <= player_decision <= 2:
                    return player_decision
            print(f"'{player_decision}' is not a valid choice.")

def input_yes_no(prompt):
    if prompt:
        print(prompt)
    return input().strip().lower() in ("y", "yes")

class BlackjackSimulator:
    def __init__(self, player_ai, num_decks=1, shuffle_deck_at=0.5,
            quiet=False, log_file=None):
        self.player_ai = player_ai
        
        self.num_decks = num_decks
        self.shuffle_deck_at = shuffle_deck_at
        self.build_deck()
        
        self.quiet = quiet
        self.log_file = log_file
    
    def print(self, *args, loud=False, **kwargs):
        if loud or not self.quiet:
            print(*args, **kwargs)
        if self.log_file:
            print(*args, **kwargs, file=self.log_file)
    
    def print_hands(self, *hands, hide=("Dealer",)):
        # Semi-ugly code to print the hands next to each other.
        
        self.print()
        
        widths = [max(10, len(h.name)) for h in hands]
        sep = "    "
        
        self.print(end=" ")
        self.print(sep=sep, *(f"{h.name:{w}}" for w, h in zip(widths, hands)))

        self.print(end=" ")
        self.print(sep=sep, *("-" * w for w in widths))

        card_columns = []
        for h in hands:
            if h.name in hide:
                cards = itertools.chain(
                    ((h[0], h[0].base_value),),
                    itertools.repeat(("--", "--"), len(h) - 1))
            else:
                cards = h.card_values()
            card_columns.append(cards)
        
        for card_row in itertools.zip_longest(*card_columns):
            self.print(end=" ")
            self.print(sep=sep, *(
                f"{str(card_value[0]):>{w - 5}} ({card_value[1]:>2})"
                if card_value else " " * w
                for w, card_value in zip(widths, card_row)))

        self.print(end=" ")
        self.print(sep=sep, *("-" * w for w in widths))

        self.print(end=" ")
        self.print(sep=sep, *(
            f"""Total:{
                "--" if hand.name in hide else hand.total
                :>{w - 7}} """
            for w, hand in zip(widths, hands)))
        
        self.print()

    def build_deck(self):
        self.deck = [Card(s, r)
            for r in range(13)
            for s in range(4)
            for _ in range(self.num_decks)]
        shuffle(self.deck)
        self.player_ai.deck_shuffled(self.num_decks)
    
    def deal(self, hand, player_sees):
        card = self.deck.pop(0)
        hand.add_card(card)
        if player_sees:
            self.player_ai.view_card(card)

    def play_hand(self, player, dealer):
        
        if player.total >= 21:
            if player.total > 21:
                self.print("Hand busted")
            self.player_ai.end_hand(player)
            return [player]
        
        #Player makes decision: 0: Hit, 1: Stand, 2: Double Down, 3: Split
        self.print_hands(player, dealer)
        player_decision = self.player_ai.choice(player)
        self.print("Player choice:", PlayerAI.choice_names[player_decision])

        #Player splits their hand.
        if player_decision == PlayerAI.CH_SPLIT:
            assert player.can_be_split()
            
            hand1, hand2 = player.split()
            self.player_ai.split_hand(player, hand1, hand2)
            
            self.deal(hand1, True)
            self.deal(hand2, True)
            
            return [
                *self.play_hand(hand1, dealer),
                *self.play_hand(hand2, dealer)]
        
        #Any other action is taken by the player.
        while player_decision != PlayerAI.CH_STAND:
            
            if player_decision == PlayerAI.CH_HIT:
                self.deal(player, True)
                
            elif player_decision == PlayerAI.CH_DOUBLE_DOWN:
                #Double the player's bet.
                player.bet *= 2
                
                #Take one hit then stand.
                self.deal(player, True)
                break
            #Check if the player busted before continuing.
            if player.total > 21:
                self.print("Hand busted")
                break
            if player.total == 21:
                break
            
            self.print_hands(player, dealer)
            player_decision = self.player_ai.choice(player)
            self.print("Player choice:", PlayerAI.choice_names[player_decision])
        
        self.player_ai.end_hand(player)
        return [player]

    def play_run(self):
        
        if len(self.deck) < 52 * self.num_decks * self.shuffle_deck_at:
            self.build_deck()
        
        #These represent the hands of the player and dealer, respectively.
        player = Hand("Player")
        dealer = Hand("Dealer")
        
        self.player_ai.start_round(player, dealer)

        #Player places their bet.
        player.bet = self.player_ai.make_bet()

        #Deal cards out.
        #Deal 2 cards to the player and dealer, alternating
        self.deal(player, True)
        self.deal(dealer, True)
        self.deal(player, True)
        self.deal(dealer, False)
        
        if dealer[0].base_value == 11:
            #Player can choose to make an insurance bet.
            self.print_hands(player, dealer)
            if self.player_ai.choose_insurance():
                self.print("Player chooses to make an insurance bet.")
                insurance = 5
            else:
                self.print("Player does not choose to make an insurance bet.")
                insurance = 0
        else:
            insurance = 0
        
        #Check for Blackjack
        player_blackjack = player.total == 21
        dealer_blackjack = dealer.total == 21
        
        if player_blackjack and dealer_blackjack:
            self.print("Player and Dealer Blackjack, Round Draw")
            self.player_ai.view_card(dealer[1])
            self.print_hands(player, dealer, hide=())
            self.player_ai.funds += (2 * insurance)
            self.player_ai.end_hand(player)
            self.player_ai.end_round(0)
            return
        elif player_blackjack:
            self.print("Player Blackjack, Player Wins")
            self.player_ai.view_card(dealer[1])
            self.print_hands(player, dealer, hide=())
            self.player_ai.funds += (player.bet * 3 // 2) - insurance
            self.player_ai.end_hand(player)
            self.player_ai.end_round(+1)
            return
        elif dealer_blackjack:
            self.print("Dealer Blackjack, Dealer Wins")
            self.player_ai.view_card(dealer[1])
            self.print_hands(player, dealer, hide=())
            self.player_ai.funds += (2 * insurance) - player.bet
            self.player_ai.end_hand(player)
            self.player_ai.end_round(-1)
            return
        elif insurance != 0:
            self.print("Dealer does not have Blackjack, Insurance forfeited")
            self.print_hands(player, dealer)
            self.player_ai.funds -= insurance

        #Player plays out their hand.
        self.print_hands(player, dealer)
        if self.player_ai.choose_surrender():
            self.print("Player surrender, Dealer Wins")
            self.print_hands(player, dealer)
            self.player_ai.funds -= (player.bet // 2)
            self.player_ai.end_hand(player)
            self.player_ai.end_round(-1)
            return
        else:
            self.print("Player does not surrender.")
        
        results = self.play_hand(player, dealer)
        
        #Check what the outcome was.
        non_busted_hands = []
        for i, hand in enumerate(results):
            if hand.total > 21:
                self.print(f"Hand {i}: Player busts, Dealer Wins")
                self.print_hands(hand, dealer)
                self.player_ai.funds -= player.bet
            else:
                non_busted_hands.append(results[i])

        #If there are no more live hands, continue
        if len(non_busted_hands) == 0:
            self.player_ai.end_round(-1)
            return

        #Dealer makes decision: hit when below 17 and stand when above 16.
        self.player_ai.view_card(dealer[1])
        while dealer.total < 17:
            self.deal(dealer, True)
        
        #Check if the dealer busted.
        if dealer.total > 21:
            self.print("Dealer Busts, Player Wins")
            for hand in non_busted_hands:
                self.player_ai.view_card(dealer[1])
                self.print_hands(player, dealer, hide=())
                self.player_ai.funds += hand.bet
            self.player_ai.end_round(+1)
            return

        #Compare the player's and dealer's hand.
        self.player_ai.view_card(dealer[1])
        for hand in non_busted_hands:
            if hand.total > dealer.total:
                self.print("Player Total Higher, Player Wins")
                self.print_hands(player, dealer, hide=())
                self.player_ai.funds += hand.bet
                self.player_ai.end_round(+1)
            elif hand.total < dealer.total:
                self.print("Dealer Total Higher, Dealer Wins")
                self.print_hands(player, dealer, hide=())
                self.player_ai.funds -= hand.bet
                self.player_ai.end_round(-1)
            else:
                self.print("Player and Dealer Totals Equal, Draw")
                self.print_hands(player, dealer, hide=())
                self.player_ai.end_round(0)


if __name__ == "__main__":
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
    ai_type_group.add_argument("-c", "--counting",
        help="use an AI that counts cards",
        dest="ai_type", action="store_const", const=PlayerAICardCounting)
    parser.set_defaults(ai_type=PlayerAICardCounting)
    
    parser.add_argument("-n", "--num-rounds",
        help="set the number of rounds to play (default 10)",
        dest="num_rounds", metavar="NUM",
        type=int, default=10)
    parser.add_argument("-d", "--num-decks",
        help="set the number of decks to play with (default 1)",
        dest="num_decks", metavar="NUM",
        type=int, default=1)
    parser.add_argument("-s", "--shuffle-at",
        help="sets the percentage of the decks that is played before shuffling (default 0.5)",
        dest="shuffle_at", metavar="DEC",
        type=float, default=0.5)
    parser.add_argument("-q", "--quiet",
        help="remove most screen logging",
        action="store_true")
    parser.add_argument("-l", "--log",
        help="save logs to a file",
        nargs="?", const="log.txt")
    args = parser.parse_args()
    
    
    if args.log is None:
        log_file = None
    else:
        log_file = open(args.log, "w", encoding="utf-8")
    
    player_ai = args.ai_type()
    sim = BlackjackSimulator(player_ai,
        num_decks=args.num_decks, shuffle_deck_at=args.shuffle_at,
        quiet=args.quiet, log_file=log_file)
    
    if args.quiet and args.num_rounds >= 100000:
        thousands_of_rounds = str(args.num_rounds // 1000)
        occ_update = f"Run {{:{len(thousands_of_rounds)}}}k/{thousands_of_rounds}k"
    else:
        occ_update = None
    
    #Run the simulation
    for run_number in range(args.num_rounds):
        
        if occ_update and run_number % 50000 == 49999:
            print(occ_update.format((run_number + 1) // 1000))
        
        sim.print("----------------------------------")
        sim.play_run()
        sim.print(f"Total Profit: {player_ai.funds:+}")
    
    sim.print("----------------------------------")
    sim.print("Player Wins:  ", player_ai.wins,      loud=True)
    sim.print("Player Losses:", player_ai.losses,    loud=True)
    sim.print("Player Draws: ", player_ai.draws,     loud=True)
    sim.print(f"Profit:        {player_ai.funds:+}", loud=True)
    
    if log_file:
        log_file.close()
































#This allows me to scroll, k
