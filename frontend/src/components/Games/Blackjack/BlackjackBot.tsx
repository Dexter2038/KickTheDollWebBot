import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";

const BlackjackBot: React.FC = () => {
    const [steps, setSteps] = useState<number>(-1);
    const [playerResult, setPlayerResult] = useState<number>(0);
    const [botResult, setBotResult] = useState<number>(0);
    const [activePlayer, setActivePlayer] = useState<boolean>(true);
    const [playerHand, setPlayerHand] = useState<string[]>([]);
    const [botHand, setBotHand] = useState<string[]>([]);
    const [hiddenCards, setHiddenCards] = useState<boolean>(false);

    const startGame = () => {
        // Initialize the hands and results
        const initialPlayerHand = getRandomHand();
        const initialBotHand = getRandomHand();

        setPlayerHand(initialPlayerHand);
        setBotHand(initialBotHand);

        setPlayerResult(parseHand(initialPlayerHand));
        setBotResult(parseHand(initialBotHand));

        setSteps(0);
    };

    useEffect(() => {
        if (steps === -1) {
            startGame();
        }
    }, [steps]);

    const getRandomHand = (): string[] => {
        return [drawCard(), drawCard()];
    };

    const drawCard = (): string => {
        const ranks = [
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "j",
            "q",
            "k",
            "a",
        ];
        const suits = ["_hearts", "_diamonds", "_clubs", "_spades"];
        const randomRank = ranks[Math.floor(Math.random() * ranks.length)];
        const randomSuit = suits[Math.floor(Math.random() * suits.length)];
        return `${randomRank}${randomSuit}`;
    };

    const parseCard = (card: string) => {
        const rank = card.slice(0, 2).replace("_", "");
        return rank === "a"
            ? 11
            : parseInt(
                  rank.replace("q", "10").replace("k", "10").replace("j", "10")
              );
    };

    const parseHand = (hand: string[]) => {
        let total = 0;
        let aces = 0;

        for (const card of hand) {
            total += parseCard(card);
            if (card.slice(0, 2) === "a_") {
                aces++;
            }
        }

        while (total > 21 && aces > 0) {
            total -= 10;
            aces--;
        }

        return total;
    };

    const takeCard = () => {
        const newCard = drawCard();
        const newPlayerHand = [...playerHand, newCard];
        setPlayerHand(newPlayerHand);
        const newPlayerResult = parseHand(newPlayerHand);

        if (newPlayerResult > 21) {
            toast.warning("Перебор! Вы проиграли.");
            botTurn();
        } else {
            setPlayerResult(newPlayerResult);
        }
    };

    const passTurn = () => {
        botTurn();
    };

    const botTurn = () => {
        setActivePlayer(false);
        const botHandCopy = [...botHand];
        let botScore = parseHand(botHandCopy);

        // Bot draws cards until it reaches at least 17
        while (botScore < 17) {
            botHandCopy.push(drawCard());
            botScore = parseHand(botHandCopy);
        }

        setBotHand(botHandCopy);
        setBotResult(botScore);
        determineWinner(botScore);
    };

    const determineWinner = (botScore: number) => {
        setHiddenCards(true);
        const playerScore = playerResult;

        if (playerScore > 21) {
            toast.warn("Перебор! Вы проиграли.");
        } else if (botScore > 21) {
            toast.success("Бот перебрал! Вы выиграли!");
        } else if (playerScore > botScore) {
            toast.success("Вы выиграли!");
        } else if (botScore > playerScore) {
            toast.warn("Вы проиграли.");
        } else {
            toast.info("Ничья");
        }

        setTimeout(() => {
            setHiddenCards(false);
            setSteps(-1); // Reset game state
        }, 1400);
    };

    return (
        <div>
            <div className="page-title">
                <div className="page-title-cell">
                    <b className="page-title-cell-title">Бот:</b>{" "}
                    <span>{botResult}</span>
                </div>
                <div className="page-title-cell">
                    <b className="page-title-cell-title">Вы:</b>{" "}
                    <span>{playerResult}</span>
                </div>
                <div className="page-title-cell">
                    <span>{activePlayer ? "Ваш ход" : "Ход бота"}</span>
                </div>
            </div>
            <div className="page-other">
                <div className="cell cell-dividable">
                    <button
                        type="button"
                        className="btn-money take-button"
                        onClick={takeCard}
                        disabled={!activePlayer}
                    >
                        Ещё
                    </button>
                    <button
                        type="button"
                        className="btn-money pass-button"
                        onClick={passTurn}
                        disabled={!activePlayer}
                    >
                        Хватит
                    </button>
                </div>
                <div className="card-hand-self">
                    {playerHand.map((card: string, index: number) => (
                        <img
                            key={index}
                            src={`/blackjack/${card}.svg`}
                            width="10%"
                            style={{
                                transform: `rotate(${calculateAngle(index, playerHand.length)}deg) translateY(20px)`,
                            }}
                        />
                    ))}
                </div>
                <div className="card-hand-opponent">
                    {botHand.map((card, index) => (
                        <img
                            key={index}
                            src={
                                hiddenCards
                                    ? "/blackjack/back.svg"
                                    : `/blackjack/${card}.svg`
                            }
                            width="10%"
                            style={{
                                transform: `rotate(${calculateAngle(index, botHand.length, true)}deg) translateY(20px)`,
                            }}
                        />
                    ))}
                </div>
            </div>
        </div>
    );

    function calculateAngle(
        index: number,
        totalCards: number,
        isOpponent = false
    ): number {
        const arcAngle = 90;
        const angleStep = arcAngle / (totalCards - 1);
        return (isOpponent ? 180 : 0) - arcAngle / 2 + angleStep * index;
    }
};

export default BlackjackBot;
