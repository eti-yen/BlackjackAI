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


class Card():
    #1 is Ace
    number = 0

    def getValue(self):
        return self.number

    def reduceAce(self):
        if self.number == 11:
            self.number = 1


def printHands(player, dealer):
    print("Player Hand:")
    for i in player:
        print(i.getValue())
    print("Player Total: " + str(getHandValue(player)))
    print("\nDealer Hand:")
    for i in dealer:
        print(i.getValue())
    print("Dealer Total: " + str(getHandValue(dealer)) + "\n")


def getHandValue(hand):
    total = 0
    for i in hand:
        total += i.getValue()
    #If the hand would bust, check if there are any Aces that can be counted as 1 instead of 11.
    if total > 21:
        for i in hand:
            if i.getValue() == 11:
                i.reduceAce()
                return getHandValue(hand)
    return total


def playHand(player, dealer, deck, current_card, results):
    #Player makes decision: 0: Hit, 1: Stand, 2: Double Down, 3: Split
    #Temporarily using manual player until AI logic is created.
    printHands(player, dealer)
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
        playHand(hand1, dealer, deck, current_card, results)
        playHand(hand2, dealer, deck, current_card, results)
        return

    #Get the value of the player's hand.
    player_total = getHandValue(player)

    #Any other action is taken by the player.
    while player_decision != "1":
        if player_decision == "0":
            player.append(deck[current_card])
            player_total = getHandValue(player)
            current_card += 1
        elif player_decision == "2":
            #Double the player's bet.

            #Take one hit then stand.
            player.append(deck[current_card])
            player_total = getHandValue(player)
            current_card += 1
            break
        #Check if the player busted before continuing.
        if player_total > 21:
            print("Hand busted")
            break
        #Temporarily using manual player until AI logic is created.
        printHands(player, dealer)
        print("Input player action: 0: Hit, 1: Stand, 2: Double Down, 3: Split")
        player_decision = input()
        print("\n\n")
    results.append(player)
    return


def buildDeck(deck):
    #Create the deck of cards using card objects.
    for i in range(4):
        for j in range(1, 14):
            new_card = Card()
            if j > 10:
                new_card.number = 10
            elif j == 1:
                new_card.number = 11
            else:
                new_card.number = j
            deck.append(new_card)

    #Shuffle the deck.
    shuffle(deck)

    return deck

def main():
    #The number of times the simulation should be run.
    number_of_runs = 1

    #Run the simulation
    for run_number in range(number_of_runs):
        #Build the deck.
        deck = buildDeck([])

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
        printHands(player, dealer)
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
        if player[0].getValue() == 11 and player[1].getValue() == 10:
            player_blackjack = 1
        elif player[0].getValue() == 10 and player[1].getValue() == 11:
            player_blackjack = 1
        if dealer[0].getValue() == 11 and dealer[1].getValue() == 10:
            dealer_blackjack = 1
        elif dealer[0].getValue() == 10 and dealer[1].getValue() == 11:
            dealer_blackjack = 1


        if player_blackjack == 1 and dealer_blackjack == 1:
            print("Player and Dealer Blackjack, Round Draw")
            printHands(player, dealer)
            funds += (2.0 * insurance)
            print("Ending Funds: " + str(funds))
            continue
        elif player_blackjack == 1:
            print("Player Blackjack, Player Wins")
            printHands(player, dealer)
            funds -= insurance
            funds += (bet * 1.5)
            print("Ending Funds: " + str(funds))
            continue
        elif dealer_blackjack == 1:
            print("Dealer Blackjack, Dealer Wins")
            printHands(player, dealer)
            funds -= bet
            funds += (2.0 * insurance)
            print("Ending Funds: " + str(funds))
            continue
        elif insurance != 0:
            print("Dealer does not have Blackjack, Insurance forfeited")
            printHands(player, dealer)
            funds -= insurance

        #Player plays out their hand.
        printHands(player, dealer)
        print("Surrender? (y/n)")
        surrender = input()
        if surrender == "y":
            print("Player surrender, Dealer Wins")
            printHands(player, dealer)
            funds -= (0.5 * bet)
            print("Ending Funds: " + str(funds))
            continue
        print("\n\n")
        results = []
        results_hands = []
        playHand(player, dealer, deck, current_card, results)

        #Check what the outcome was.
        non_busted_hands = []
        for i in range(0, len(results)):
            if getHandValue(results[i]) > 21:
                print("Hand " + str(i) + ": Player busts, Dealer Wins")
                printHands(results[i], dealer)
                funds -= bet
            else:
                non_busted_hands.append(results[i])

        #If they are no more live hands, continue
        if len(non_busted_hands) == 0:
            print("Ending Funds: " + str(funds))
            continue

        #Dealer makes decision: hit when below 17 and stand when above 16.
        dealer_total = getHandValue(dealer)
        while dealer_total < 17:
            dealer.append(deck[current_card])
            dealer_total = getHandValue(dealer)
            current_card += 1

        #Check if the dealer busted.
        if dealer_total > 21:
            print("Dealer Busts, Player Wins")
            for i in non_busted_hands:
                printHands(i, dealer)
            funds += (bet * len(non_busted_hands))
            print("Ending Funds: " + str(funds))
            continue

        #Compare the player's and dealer's hand.
        for i in non_busted_hands:
            hand_total = getHandValue(i)
            if hand_total > dealer_total:
                print("Player Total Higher, Player Wins")
                printHands(i, dealer)
                funds += bet
            elif hand_total < dealer_total:
                print("Dealer Total Higher, Dealer Wins")
                printHands(i, dealer)
                funds -= bet
            else:
                print("Player and Dealer Totals Equal, Draw")
                printHands(i, dealer)
        print("Ending Funds: " + str(funds))

#Beginning of execution.
main()
































#This allows me to scroll, k
