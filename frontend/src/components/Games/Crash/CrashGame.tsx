import React, { useState, useEffect } from "react";
import "./CrashGame.css";
import { toast } from "react-toastify";
import NavBar from "../../NavBar";
import NumberInput from "../../NumberInput";
import axios from "axios";

function formatLargeNumber(num: number) {
    const suffixes = ["", "K", "M", "B", "T", "Q", "Qi", "Sx", "Sp", "Oc"];
    let i = 0;
    while (num >= 1000 && i < suffixes.length - 1) {
        num /= 1000;
        i++;
    }

    return num.toFixed(2) + suffixes[i];
}

const CrashGame: React.FC = () => {
    const [multiplier, setMultiplier] = useState<number>(1);
    const [isGameActive, setIsGameActive] = useState<boolean>(false);
    const [hasBetPlaced, setHasBetPlaced] = useState<boolean>(false);
    const [reward, setReward] = useState<number>(100);
    const [graphPoints, setGraphPoints] = useState<
        Array<{ x: number; y: number }>
    >([]);
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const [crashMultiplier, setCrashMultiplier] = useState<number | null>(null);

    useEffect(() => {
        let interval: number;

        if (isGameActive) {
            // Генерация случайного значения для краша
            const randomCrashMultiplier = 1 + Math.random() * 4; // Значение между 1 и 5
            setCrashMultiplier(randomCrashMultiplier);

            interval = setInterval(() => {
                setMultiplier((prevMultiplier) => {
                    const newMultiplier = prevMultiplier + 0.1;
                    const timeElapsed = graphPoints.length + 1; // 1 секунда интервалов
                    setGraphPoints((prevPoints) => [
                        ...prevPoints,
                        { x: timeElapsed, y: newMultiplier },
                    ]);

                    if (newMultiplier >= randomCrashMultiplier) {
                        crashGame();
                        return newMultiplier;
                    }
                    return newMultiplier;
                });
            }, 1000);
        }

        return () => {
            if (interval) clearInterval(interval);
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isGameActive, graphPoints]);

    const crashGame = () => {
        setIsGameActive(false);
        setHasBetPlaced(false);
        setMultiplier(1.0);
        toast.warn(
            `Вы проиграли ${reward} ${
                reward % 10 === 1 && reward % 100 !== 11
                    ? "монета"
                    : 2 <= reward % 10 &&
                        reward % 10 <= 4 &&
                        !(12 <= reward % 100 && reward % 100 <= 14)
                      ? "монеты"
                      : "монет"
            }`
        );
        axios.post("/api/game/finish", {
            game_type: 4,
            second_user_id: null,
            amount: -reward,
        });
    };

    const placeBet = async () => {
        if (hasBetPlaced) {
            toast.info("Ставка уже сделана!");
            return;
        }
        try {
            const { data } = await axios.post("/api/money/check", {
                bet: reward,
            });
            if (!data.ok) {
                toast.error("Недостаточно монет");
                return;
            }
        } catch (error) {
            console.error(error);
        }
        setHasBetPlaced(true);
        setIsGameActive(true);
        setMultiplier(1);
        setGraphPoints([]);
        setCrashMultiplier(null); // Сбросить случайный множитель
    };

    const cashOut = () => {
        if (!isGameActive) {
            toast.error("Сначала сделайте ставку!");
            return;
        }
        setIsGameActive(false);
        setHasBetPlaced(false);
        toast.success(`Вы вывели с множителем ${multiplier.toPrecision(3)}x!`);
        axios.post("/api/game/finish", {
            game_type: 4,
            second_user_id: null,
            amount: reward * multiplier - reward,
        });

        setMultiplier(1);
    };

    const handleRewardChange = (num: string) => {
        setReward(Number(num));
    };

    return (
        <>
            <div className="page-title">
                <div className="page-title-cell">
                    <b className="page-title-cell-title">💰Награда💰:</b>{" "}
                    {reward ? formatLargeNumber(reward * multiplier) : 0}{" "}
                    {(reward * multiplier) % 10 === 1 &&
                    (reward * multiplier) % 100 !== 11
                        ? "монета"
                        : 2 <= (reward * multiplier) % 10 &&
                            (reward * multiplier) % 10 <= 4 &&
                            !(
                                12 <= (reward * multiplier) % 100 &&
                                (reward * multiplier) % 100 <= 14
                            )
                          ? "монеты"
                          : "монет"}
                </div>
                <div className="page-title-cell">
                    <b className="page-title-cell-title">Множитель:</b>{" "}
                    {multiplier.toPrecision(3)}x
                </div>
                <div className="page-title-cell">
                    <span>
                        {isGameActive ? "Игра активна" : "Игра неактивна"}
                    </span>
                </div>
            </div>
            <div className="page-other">
                <button
                    type="button"
                    className="cell btn-def"
                    onClick={cashOut}
                    disabled={!isGameActive}
                >
                    Вывести
                </button>
                <button
                    type="button"
                    className="cell def"
                    onClick={() => placeBet()}
                    disabled={isGameActive}
                >
                    Поставить
                </button>
                <div className="cell">
                    <NumberInput
                        style={{ fontSize: "1.3rem" }}
                        value="reward"
                        onChange={handleRewardChange}
                        disabled={isGameActive}
                        placeholder="Сумма"
                    />
                </div>
                <div className="graph-container">
                    <svg width="100%" height="100%" viewBox="0 0 100 50">
                        <polyline
                            fill="none"
                            stroke="blue"
                            strokeWidth="2"
                            points={graphPoints
                                .map((p) => `${p.x * 2},${50 - p.y * 10}`)
                                .join(" ")}
                        />
                    </svg>
                </div>
            </div>
            <NavBar stricted={true} />
        </>
    );
};

export default CrashGame;
