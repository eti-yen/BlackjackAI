from random import shuffle

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
    
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        if rank > 9:
            self.value = 10
        elif rank == 0:
            self.value = 11
        else:
            self.value = rank + 1
    
    def reduce_ace(self):
        if self.value == 11:
            self.value = 1
    
    def __str__(self):
        suit = Card.suit_symbols[self.suit]
        rank = Card.rank_symbols[self.rank]
        return f"{suit}{rank} ({self.value})"


def print_hands(player, dealer):
    print("Player Hand:")
    for i in player:
        print(i.value)
    print("Player Total: " + str(get_hand_value(player)))
    print("\nDealer Hand:")
    for i in dealer:
        print(i.value)
    print("Dealer Total: " + str(get_hand_value(dealer)) + "\n")


def get_hand_value(hand):
    total = sum(card.value for card in hand)
    # If the hand would bust, check if there are any
    # Aces that can be counted as 1 instead of 11.
    if total > 21:
        for card in hand:
            if card.value == 11:
                card.reduce_ace()
                total -= 10
                if total <= 21:
                    break
    return total


def play_hand(player, dealer, deck, current_card, results):
    #Player makes decision: 0: Hit, 1: Stand, 2: Double Down, 3: Split
    #Temporarily using manual player until AI logic is created.
    print_hands(player, dealer)
    print("Input player action: 0: Hit, 1: Stand, 2: Double Down, 3: Split")
    player_decision = input()
    print("\n\n")

    #Player splits their hand.
    if player_decision == "3":
        hand1 = [player[0]]
        hand1.append(deck[current_card])
        current_card += 1
        hand2 = [player[1]]
        hand2.append(deck[current_card])
        current_card += 1
        play_hand(hand1, dealer, deck, current_card, results)
        play_hand(hand2, dealer, deck, current_card, results)
        return

    #Get the value of the player's hand.
    player_total = get_hand_value(player)

    #Any other action is taken by the player.
    while player_decision != "1":
        if player_decision == "0":
            player.append(deck[current_card])
            player_total = get_hand_value(player)
            current_card += 1
        elif player_decision == "2":
            #Double the player's bet.

            #Take one hit then stand.
            player.append(deck[current_card])
            player_total = get_hand_value(player)
            current_card += 1
            break
        #Check if the player busted before continuing.
        if player_total > 21:
            print("Hand busted")
            break
        #Temporarily using manual player until AI logic is created.
        print_hands(player, dealer)
        print("Input player action: 0: Hit, 1: Stand, 2: Double Down, 3: Split")
        player_decision = input()
        print("\n\n")
    results.append(player)
    return


def build_deck():
    deck = [Card(s, r) for r in range(13) for s in range(4)]
    shuffle(deck)
    return deck

def main():
    #The number of times the simulation should be run.
    number_of_runs = 1

    #Run the simulation
    for run_number in range(number_of_runs):
        #Build the deck.
        deck = build_deck()

        #These represent the hands of the player and dealer, respectively.
        player = []
        dealer = []

        #Which card is next in the queue from the deckself.
        current_card = 0

        #Player places their bet.
        funds = 100.0
        bet = 10.0

        #Deal cards out.
        #Deal 2 cards to the player and dealer, alternating
        player.append(deck[current_card])
        current_card += 1
        dealer.append(deck[current_card])
        current_card += 1
        player.append(deck[current_card])
        current_card += 1
        dealer.append(deck[current_card])
        current_card += 1

        #Player can choose to make an insurance bet.
        print_hands(player, dealer)
        print("Make an insurance bet? (y/n)")
        x = input()
        print("\n\n")
        if x == "y":
            insurance = 5.0
        else:
            insurance = 0.0

        #Check for Blackjack
        player_blackjack = 0
        dealer_blackjack = 0
        if player[0].value == 11 and player[1].value == 10:
            player_blackjack = 1
        elif player[0].value == 10 and player[1].value == 11:
            player_blackjack = 1
        if dealer[0].value == 11 and dealer[1].value == 10:
            dealer_blackjack = 1
        elif dealer[0].value == 10 and dealer[1].value == 11:
            dealer_blackjack = 1


        if player_blackjack == 1 and dealer_blackjack == 1:
            print("Player and Dealer Blackjack, Round Draw")
            print_hands(player, dealer)
            funds += (2.0 * insurance)
            print("Ending Funds: " + str(funds))
            continue
        elif player_blackjack == 1:
            print("Player Blackjack, Player Wins")
            print_hands(player, dealer)
            funds -= insurance
            funds += (bet * 1.5)
            print("Ending Funds: " + str(funds))
            continue
        elif dealer_blackjack == 1:
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
        print("Surrender? (y/n)")
        surrender = input()
        if surrender == "y":
            print("Player surrender, Dealer Wins")
            print_hands(player, dealer)
            funds -= (0.5 * bet)
            print("Ending Funds: " + str(funds))
            continue
        print("\n\n")
        results = []
        results_hands = []
        play_hand(player, dealer, deck, current_card, results)

        #Check what the outcome was.
        non_busted_hands = []
        for i in range(0, len(results)):
            if get_hand_value(results[i]) > 21:
                print("Hand " + str(i) + ": Player busts, Dealer Wins")
                print_hands(results[i], dealer)
                funds -= bet
            else:
                non_busted_hands.append(results[i])

        #If they are no more live hands, continue
        if len(non_busted_hands) == 0:
            print("Ending Funds: " + str(funds))
            continue

        #Dealer makes decision: hit when below 17 and stand when above 16.
        dealer_total = get_hand_value(dealer)
        while dealer_total < 17:
            dealer.append(deck[current_card])
            dealer_total = get_hand_value(dealer)
            current_card += 1

        #Check if the dealer busted.
        if dealer_total > 21:
            print("Dealer Busts, Player Wins")
            for i in non_busted_hands:
                print_hands(i, dealer)
            funds += (bet * len(non_busted_hands))
            print("Ending Funds: " + str(funds))
            continue

        #Compare the player's and dealer's hand.
        for i in non_busted_hands:
            hand_total = get_hand_value(i)
            if hand_total > dealer_total:
                print("Player Total Higher, Player Wins")
                print_hands(i, dealer)
                funds += bet
            elif hand_total < dealer_total:
                print("Dealer Total Higher, Dealer Wins")
                print_hands(i, dealer)
                funds -= bet
            else:
                print("Player and Dealer Totals Equal, Draw")
                print_hands(i, dealer)
        print("Ending Funds: " + str(funds))

if __name__ == '__main__':
    main()
































#This allows me to scroll, k
