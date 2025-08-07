import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { toast } from "react-toastify";
import getLaunchParams from "../../RetrieveLaunchParams";
import axios from "axios";

const BlackjackGame: React.FC = () => {
    const [searchParams] = useSearchParams();
    const roomId = searchParams.get("room_id");
    const { initDataRaw, initData } = getLaunchParams();
    const playerId = initData?.user?.id;
    const [steps, setSteps] = useState<number>(-1);
    const [player1Result, setPlayer1Result] = useState<number>(0);
    const [player2Result, setPlayer2Result] = useState<number>(0);
    const [activePlayer, setActivePlayer] = useState<boolean>(false);
    const [selfHand, setSelfHand] = useState<string[]>([]);
    const [opponentHand, setOpponentHand] = useState<string[]>([]);
    const [hiddenCards, setHiddenCards] = useState<boolean>(false);
    const [reward, setReward] = useState<number>(0);

    const rewardEnding: string =
        reward % 10 === 1 && reward % 100 !== 11
            ? "монета"
            : 2 <= reward % 10 &&
                reward % 10 <= 4 &&
                !(12 <= reward % 100 && reward % 100 <= 14)
              ? "монеты"
              : "монет";

    useEffect(() => {
        const getReward = async () => {
            axios
                .get(`/api/blackjack/reward?room_id=${roomId}`)
                .then((response) => {
                    setReward(response.data.reward);
                })
                .catch(() => {
                    toast.error("Произошла ошибка.");
                });
        };
        getReward();
        const interval = setInterval(getBlackjackUpdates, 1500);
        return () => clearInterval(interval);
    });

    const getBlackjackUpdates = async () => {
        const { data } = await axios.get(
            `/api/blackjack/updates?player_id=${playerId}&room_id=${roomId}`
        );
        if (data.ok) {
            if (data.msg !== "Обновления успешно получены.") {
                toast(data.msg);
            }
            setSelfHand(data.data.self.hands);
            setPlayer1Result(data.data.self.results);
            setPlayer2Result(data.data.opponent.results);
            setActivePlayer(data.data.active_player);
            if (
                data.self.count == data.opponent.count &&
                steps !== data.self.count
            ) {
                setSteps(data.self.count);
                checkWinner(data.self.hands, opponentHand, data.opponent.hands);
            } else {
                setOpponentHand(data.data.opponent.hands);
            }
        } else {
            toast.error("Произошла ошибка.");
        }
    };

    const takeCard = async () => {
        axios
            .post(
                "/api/blackjack/take",
                {
                    initData: initDataRaw,
                    player_id: playerId,
                    room_id: roomId,
                },
                {
                    headers: {
                        "Content-Type": "application/json",
                    },
                }
            )
            .then(({ data }) => {
                if (data.ok) {
                    setSelfHand(data.hand);
                    if (data.status === 202) {
                        toast.warning("Перебор!");
                        if (data.opponent) {
                            setHiddenCards(true);
                            setTimeout(() => setHiddenCards(false), 1000);
                        }
                    }
                } else {
                    toast(data.msg);
                }
            })
            .catch(() => {
                toast.error("Ошибка!");
            });
    };

    const passTurn = async () => {
        try {
            const { data } = await axios.post("/api/blackjack/pass", {
                initData: initDataRaw,
                player_id: playerId,
                room_id: roomId,
            });
            if (!data.ok) {
                toast(data.msg);
            }
        } catch (error) {
            toast.error("Ошибка!");
        }
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

    const checkWinner = (
        hand1: string[],
        hand2: string[],
        opponent_current_hands: string[]
    ) => {
        setHiddenCards(true);
        const score1 = parseHand(hand1);
        const score2 = parseHand(hand2);
        if (score1 > 21) {
            toast.warn("Перебор! Вы проиграли.");
        } else if (score2 > 21) {
            toast.success("Противник перебрал! Вы выиграли!");
        } else if (score1 > score2) {
            toast.success("Вы выиграли!");
        } else if (score2 > score1) {
            toast.warn("Вы проиграли.");
        } else {
            toast.info("Ничья");
        }
        setTimeout(() => {
            setHiddenCards(false);
            setOpponentHand(opponent_current_hands);
        }, 1400);
    };

    return (
        <div>
            <div className="page-title">
                <div className="page-title-cell">
                    <b className="page-title-cell-title">Противник:</b>{" "}
                    <span>{player2Result}</span>
                </div>
                <div className="page-title-cell">
                    <b className="page-title-cell-title">Вы:</b>{" "}
                    <span>{player1Result}</span>
                </div>
                <div className="page-title-cell">
                    <b className="page-title-cell-title">Награда💰:</b> {reward}{" "}
                    {rewardEnding}
                </div>
                <div className="page-title-cell">
                    <span>{activePlayer ? "Ваш ход" : "Ход противника"}</span>
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
                    {selfHand.map((card: string, index: number) => (
                        <img
                            key={index}
                            src={`/blackjack/${card}.svg`}
                            width="10%"
                            style={{
                                transform: `rotate(${calculateAngle(
                                    index,
                                    selfHand.length
                                )}deg) translateY(20px)`,
                            }}
                        />
                    ))}
                </div>
                <div className="card-hand-opponent">
                    {opponentHand.map((card, index) => (
                        <img
                            key={index}
                            src={
                                hiddenCards
                                    ? "/blackjack/back.svg"
                                    : `/blackjack/${card}.svg`
                            }
                            width="10%"
                            style={{
                                transform: `rotate(${calculateAngle(
                                    index,
                                    opponentHand.length,
                                    true
                                )}deg) translateY(20px)`,
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

export default BlackjackGame;
