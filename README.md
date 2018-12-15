# Blackjack AI

### Authors:
- Kevin Donovan
- Etienne Morakotkarn
- Sol Toder

## Basic Usage

The project is intended to be run on Python 3.7. You can run it using

    python main.py

To see the full usage information, run it with

    python main.py --help

## Strategy

This project's aim is to create an AI that can play Blackjack and make a profit. This involved building a
full Blackjack simulation, into which we could plug our AI. Since Blackjack has many variants and house
rules, we had to decide on which ones to use for our sim. Some of the results:

- The dealer hits at soft 17.
- The number of decks is one by default, although this can be modified with console arguments.
- Early surrender is not allowed.
- A hand may only be split once.
- Doubling down is allowed after a split.

Our AI's strategy is based on accepted Blackjack techniques such as card counting and "basic strategy".
This was based in large part on the guides found at https://www.blackjackapprenticeship.com/blackjack-strategy-charts/,
https://www.blackjackapprenticeship.com/how-to-count-cards/, and related pages on the site. The default
AI will count all the cards it can see (which does not include the dealer's hidden card until the end of
the hand), and will make bets accordingly. Most play decisions (hit vs. stand, and so on) are based on
the tables found both in the linked pages and on Wikipedia, detailing the most mathematically advantageous
moves in all possible situations.

We also have an "Advanced" card counting AI that deviates from Basic Strategy following certain card counts.
This was mostly based on the so-called "Illustrious 18" and "Fab 4" charts found at https://wizardofodds.com/games/blackjack/card-counting/high-low/
and https://www.casinonewsdaily.com/blackjack-guide/illustrious-18/. Of note is that this is the only AI that will sometimes take insurance.

## Notes

- To get a good read on the AI's skill, it is recommended to let it play a large number of hands. Something
like

        python main.py -q -n 100000

    will output the final results after 100,000 matches. You may also add other arguments to vary the simulation.

- Keep in mind that, while the win/loss/draw ratios are of value, the target variable is the total profit.
Losses are inevitable, but the AI can minimize their impact by betting correctly.

- The current and default AI is the one accessed by `-c/--counting`. The other AI options are provided only for
historical and trivia purposes, and are not intended for grading. They are shown on the help screen in the
order of their creation: `-m/--manual` (no AI, manual player input), `-s/--stand` (always chooses to stand), 
`-r/--rules` (a more basic rules-based AI, with no card-counting), and '-ac/--advanced_counting' (card counting with derivations from basic strategy).
