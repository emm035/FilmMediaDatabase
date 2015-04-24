/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package Controller;

import TexasModel.AI;
import TexasModel.Card;
import TexasModel.Deck;
import TexasModel.GameModel;
import static TexasModel.GameUtil.findTheBest;
import static TexasModel.GameUtil.findTheBestfromsix;
import TexasModel.Hand;
import TexasModel.SixCardHandException;
import java.util.ArrayList;

/**
 * The controller of the AI class, which reads information from the GameModel to
 * update the state of the AI. Uses inheritance so that controllers of multiple
 * difficulties can be made, but will still all have the same type, which is
 * AIController.
 *
 * @author justi_000
 */
public class AIController2 extends AIController {

    public AIController2(GameModel model, AI ai) {
        super(model, ai);
    }

    /**
     * Chooses move in Blind stage.
     */
    @Override
    protected void performBlindAction() {
        if (ai.getMoney() < model.getCallAmount()) {
            ai.fold();
            mostRecentDecision = "fold";
        } else if (model.isAllCall()) {
            if (ai.getMoney() >= model.getCallAmount()) {
                ai.call();
                mostRecentDecision = "call";
            } else {
                ai.allin();
                mostRecentDecision = "allin";
            }
        } else {
            // AI has already called this amount or higher
            if (ai.isIsCall()) {
                ai.check();
                mostRecentDecision = "check";
            } else {
                // For calls and raises, have to check if they have enough.
                if (ai.getMoney() >= model.getCallAmount()) {
                    ai.call();
                    mostRecentDecision = "call";
                }
            }
        }
    }

    /**
     * Chooses move in Flop stage.
     *
     * @throws SixCardHandException
     */
    @Override
    protected void performFlopAction() throws SixCardHandException {
        /* Need a temporary hand so that we can have a five card hand even when
         AI only holds two at a time until the riverhand round. */
        Hand tempAIHand = new Hand();

        // Create testDeck to simulate drawing additional common cards from.
        Deck testDeck = new Deck();
        /* Remove cards that are already in AI's hand or the pool from the test
         deck. We already know that the AI won't be drawing these cards.
         No need to include them in our tests. The code below also adds these
         five cards to an ArrayList, so that when two more cards are simulated,
         we can call a method to check what the best possible hand is from all
         the cards, and score this hand.
         */

        // sevenCardList is for predicting the future (will end game w/ 7 cards)
        ArrayList<Card> sevenCardList = new ArrayList<>();
        for (Card card : ai.getHand().getHand()) {
            testDeck.removeCard(card);
            sevenCardList.add(card);
            tempAIHand.addCard(card);
        }
        for (Card card : model.getPoolcards()) {
            testDeck.removeCard(card);
            sevenCardList.add(card);
            tempAIHand.addCard(card);
        }
        // reset circumstantial rank
        circumstantialRank = tempAIHand.getHandRank();

        /* Now, we know that two more cards will be turned over. Test all possible
         cases for what these could be using the test deck, getting the best hand
         with each addition and scoring the total.
         */
        int offset = 0;
        for (int index1 = 0; index1 < testDeck.getDeck().size(); index1++) {
            sevenCardList.add(testDeck.getDeck().get(index1));
            offset += 1;
            for (int index2 = offset; index2 < testDeck.getDeck().size(); index2++) {
                sevenCardList.add(testDeck.getDeck().get(index2));
                Hand bestHand = findTheBest(sevenCardList);
                circumstantialRank += bestHand.getHandRank();
                sevenCardList.remove(testDeck.getDeck().get(index2));
            }
            sevenCardList.remove(testDeck.getDeck().get(index1));
        }
        // DECISION MAKING CONSTANTS:
        int GREAT_MINOR_HAND_THRESHHOLD = 18000;
        int DECENT_MINOR_HAND_THRESHHOLD = 16000;

        if (ai.getMoney() < model.getCallAmount()) {
            ai.allin();
            mostRecentDecision = "allin";
        } else if (tempAIHand.getHandRank() == 23) {
            ai.allin();
            mostRecentDecision = "allin";
        } else if (tempAIHand.getHandRank() >= 20) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 2);
            mostRecentDecision = "raise";
        } else if (tempAIHand.getHandRank() >= 18) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 3);
            mostRecentDecision = "raise";
        } else if (circumstantialRank > GREAT_MINOR_HAND_THRESHHOLD) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 8);
            mostRecentDecision = "raise";
        } else if (circumstantialRank > DECENT_MINOR_HAND_THRESHHOLD && model.isAllCall()) {
            ai.call();
            mostRecentDecision = "call";
        } else if (circumstantialRank > DECENT_MINOR_HAND_THRESHHOLD && ai.isIsCall()) {
            ai.check();
            mostRecentDecision = "check";
        } else {
            ai.fold();
            mostRecentDecision = "fold";
        }

    }

    /**
     * Chooses move in turn stage.
     *
     * @throws SixCardHandException
     */
    @Override
    protected void performTurnhandAction() throws SixCardHandException {
        /* Need a temporary hand so that we can have a five card hand even when
         AI only holds two at a time until the riverhand round. */
        Hand tempAIHand = new Hand();

        // Create testDeck to simulate drawing additional common cards from.
        Deck testDeck = new Deck();
        /* Remove cards that are already in AI's hand or the pool from the test
         deck. We already know that the AI won't be drawing these cards.
         No need to include them in our tests. The code below also adds these
         five cards to an ArrayList, so that when two more cards are simulated,
         we can call a method to check what the best possible hand is from all
         the cards, and score this hand.
         */

        ArrayList<Card> sevenCardList = new ArrayList<>();
        for (Card card : ai.getHand().getHand()) {
            testDeck.removeCard(card);
            sevenCardList.add(card);
        }
        for (Card card : model.getPoolcards()) {
            testDeck.removeCard(card);
            sevenCardList.add(card);
        }

        /* in turnhand, there will only be 6 cards in the seven card list
         at this point (one to predict). Find the best hand to be the temp
         hand.
         */
        tempAIHand = findTheBestfromsix(sevenCardList);

        // reset circumstantial rank
        circumstantialRank = tempAIHand.getHandRank();

        /* Now, we know that one more cards will be turned over. Test all possible
         cases for what this could be using the test deck, getting the best hand
         with each addition and scoring the total.
         */
        for (Card deckCard1 : testDeck.getDeck()) {
            sevenCardList.add(deckCard1);
            Hand bestHand = findTheBest(sevenCardList);
            circumstantialRank += bestHand.getHandRank();
            sevenCardList.remove(deckCard1);
        }

        // DECISION MAKING CONSTANTS:
        int GREAT_MINOR_HAND_THRESHHOLD = 800;

        int DECENT_MINOR_HAND_THRESHHOLD = 700;

        if (ai.getMoney() < model.getCallAmount()) {
            ai.allin();
            mostRecentDecision = "allin";
        } else if (tempAIHand.getHandRank() == 23) {
            ai.allin();
            mostRecentDecision = "allin";
        } else if (tempAIHand.getHandRank() >= 20) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 2);
            mostRecentDecision = "raise";
        } else if (tempAIHand.getHandRank() >= 18) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 3);
            mostRecentDecision = "raise";
        } else if (circumstantialRank > GREAT_MINOR_HAND_THRESHHOLD) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 8);
            mostRecentDecision = "raise";
        } else if (circumstantialRank > DECENT_MINOR_HAND_THRESHHOLD && model.isAllCall()) {
            ai.call();
            mostRecentDecision = "call";
        } else if (circumstantialRank > DECENT_MINOR_HAND_THRESHHOLD && ai.isIsCall()) {
            ai.check();
            mostRecentDecision = "check";
        } else {
            ai.fold();
            mostRecentDecision = "fold";
        }
    }

    /**
     * Chooses move in river stage.
     */
    @Override
    protected void performRiverhandAction() {
        /* Now we know what our best hand is. Choose a move based on strength of
         this hand. */
        if (ai.getMoney() < model.getCallAmount()) {
            ai.allin();
            mostRecentDecision = "allin";
        } else if (ai.getHand().getHandRank() == 23) {
            ai.allin();
            mostRecentDecision = "allin";
        } else if (ai.getHand().getHandRank() >= 20) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 2);
            mostRecentDecision = "raise";
        } else if (ai.getHand().getHandRank() >= 18) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 3);
            mostRecentDecision = "raise";
        } else if (circumstantialRank > 14) {
            ai.raise((ai.getMoney() - model.getCallAmount()) / 8);
            mostRecentDecision = "raise";
        } else if (circumstantialRank < 14 && circumstantialRank > 8 && model.isAllCall()) {
            ai.call();
            mostRecentDecision = "call";
        } else if (circumstantialRank < 14 && circumstantialRank > 8 && ai.isIsCall()) {
            ai.check();
            mostRecentDecision = "check";
        } else {
            ai.fold();
            mostRecentDecision = "fold";
        }
    }

}
