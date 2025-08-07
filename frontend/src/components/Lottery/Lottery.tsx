import React, { useState, useRef, useEffect, useCallback } from "react";
import "./Lottery.css";
import { fetchLottery, fetchTopWinners, Winner } from "./Utils";
import NavBar from "../NavBar";
import { toast } from "react-toastify";
import NumberInput from "../NumberInput";
import axios from "axios";

const Lottery: React.FC = () => {
    const [segments, setSegments] = useState<string[]>([]);
    const [currentDeg, setCurrentDeg] = useState(0);
    const [isSpinning, setIsSpinning] = useState(false);
    const pointerRef = useRef<HTMLDivElement>(null);
    const lightsRef = useRef<HTMLDivElement[]>([]);
    const [currentLottery, setCurrentLottery] = useState<number | null>(null);
    const [endTime, setEndTime] = useState<Date | null>(null);
    const [remainStringTime, setRemainStringTime] = useState<string>("");
    const [showInputLottery, setShowInputLottery] = useState<boolean>(false);
    const [inputLottery, setInputLottery] = useState<boolean>(false);
    const [showTopWinners, setShowTopWinners] = useState<boolean>(false);
    const [topWinnersClass, setTopWinnersClass] = useState<boolean>(false);
    const [topWinners, setTopWinners] = useState<Winner[]>([]);
    const [inputDeg, setInputDeg] = useState(0);
    const lightssRef = useRef<HTMLDivElement[]>([]);
    const [bet, setBet] = useState<number>(0);
    const [inputSegments, setInputSegments] = useState<string[]>([]);
    const [inputSpinning, setInputSpinning] = useState(false);

    useEffect(() => {
        setSegments(
            [
                // 10 crypto rewards
                "10 TON",
                "50 TON",
                "100 TON",
                "200 TON",
                "500 TON",
                "1000 TON",
                "5000 TON",
                "10000 TON",
                "20000 TON",
                "50000 TON",
            ].sort(() => 0.5 - Math.random())
        );
        setInputSegments(
            [
                "x2",
                "x3",
                "x1.5",
                "x0",
                "x2",
                "x0",
                "x0",
                "x0",
                "x1",
                "x1.5",
            ].sort(() => 0.5 - Math.random())
        );
        fetchLottery().then((data) => {
            if (data.currentValue !== -1 && data.endTime !== "") {
                setCurrentLottery(data.currentValue);
                setEndTime(new Date(data.endTime));
            } else {
                toast.error(
                    "Не удалось получить данные. Перезагрузите страницу"
                );
            }
        });
        fetchTopWinners().then((data) => {
            setTopWinners(data.winners);
        });
        const mockTopWinners: Winner[] = [
            { username: "user1", bet: 100, multiplier: 2 },
            { username: "user2", bet: 50, multiplier: 1.5 },
            { username: "user3", bet: 200, multiplier: 3 },
            { username: "user4", bet: 150, multiplier: 2.5 },
            { username: "user5", bet: 250, multiplier: 4 },
            { username: "user6", bet: 300, multiplier: 5 },
            { username: "user7", bet: 350, multiplier: 6 },
            { username: "user8", bet: 400, multiplier: 7 },
            { username: "user9", bet: 450, multiplier: 8 },
            { username: "user10", bet: 500, multiplier: 9 },
            { username: "user1", bet: 100, multiplier: 2 },
            { username: "user2", bet: 50, multiplier: 1.5 },
            { username: "user3", bet: 200, multiplier: 3 },
            { username: "user4", bet: 150, multiplier: 2.5 },
            { username: "user5", bet: 250, multiplier: 4 },
            { username: "user6", bet: 300, multiplier: 5 },
            { username: "user7", bet: 350, multiplier: 6 },
            { username: "user8", bet: 400, multiplier: 7 },
            { username: "user9", bet: 450, multiplier: 8 },
            { username: "user10", bet: 500, multiplier: 9 },
            { username: "user1", bet: 100, multiplier: 2 },
            { username: "user2", bet: 50, multiplier: 1.5 },
            { username: "user3", bet: 200, multiplier: 3 },
            { username: "user4", bet: 150, multiplier: 2.5 },
            { username: "user5", bet: 250, multiplier: 4 },
            { username: "user6", bet: 300, multiplier: 5 },
            { username: "user7", bet: 350, multiplier: 6 },
            { username: "user8", bet: 400, multiplier: 7 },
            { username: "user9", bet: 450, multiplier: 8 },
            { username: "user10", bet: 500, multiplier: 9 },
            { username: "user1", bet: 100, multiplier: 2 },
            { username: "user2", bet: 50, multiplier: 1.5 },
            { username: "user3", bet: 200, multiplier: 3 },
            { username: "user4", bet: 150, multiplier: 2.5 },
            { username: "user5", bet: 250, multiplier: 4 },
            { username: "user6", bet: 300, multiplier: 5 },
            { username: "user7", bet: 350, multiplier: 6 },
            { username: "user8", bet: 400, multiplier: 7 },
            { username: "user9", bet: 450, multiplier: 8 },
            { username: "user10", bet: 500, multiplier: 9 },
        ];
        setTopWinners(mockTopWinners);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const updateTime = useCallback(() => {
        const now = new Date().getTime();
        // @ts-expect-error I already checked that endTime is not null
        const distance = endTime?.getTime() - now;
        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor(
            (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)
        );
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);
        let out: string = "";
        if (days) {
            out += days + "д ";
        }
        if (hours) {
            out += hours + "ч ";
        }
        if (minutes) {
            out += minutes + "м ";
        }
        if (seconds) {
            out += seconds + "с";
        }
        setRemainStringTime(out);
    }, [endTime]);

    useEffect(() => {
        let x: number;
        if (endTime && endTime > new Date()) {
            x = setInterval(updateTime, 1000);
        }
        return () => {
            clearInterval(x);
        };
    }, [endTime, updateTime]);
    const makeDeposit = (): void => {
        const inputStartSpin = (): void => {
            setInputLottery(true);
            setTimeout(() => {
                setShowInputLottery(true);
            }, 100);

            //TODO
        };
        inputStartSpin();
    };

    const showTopDeposits = () => {
        setShowTopWinners(true);
        setTimeout(() => {
            setTopWinnersClass(true);
        }, 50);
    };

    const deposit = async () => {
        if (bet <= 0) return;
        const { data } = await axios.post("/api/money/check", {
            bet: bet,
        });
        if (!data.ok) {
            toast.error("Недостаточно монет");
            return;
        }
        const inputStartSpin = (): void => {
            if (inputSpinning) return;

            setInputSpinning(true);
            if (lightssRef.current) {
                lightssRef.current.forEach((light) =>
                    light.classList.add("light-twinkling")
                );
            }

            const rotateDeg = Math.random() * 360 + 1080; // Rotate 3 to 4 full turns
            const newDeg = currentDeg + rotateDeg;
            setInputDeg(newDeg);
            const index = Math.floor(((newDeg % 360) + 15) / 36);
            const prize = Number(inputSegments[index].replace("x", ""));
            axios.post("/api/lottery/deposit", {
                reward: prize,
                bet: bet,
            });
            if (prize > 1) {
                toast.success(`Вы выиграли ${prize * bet - bet}!`);
            } else if (prize < 1) {
                toast.warn(`Вы проиграли ${bet}`);
            } else {
                toast.success("Вы ничего не проиграли!");
            }

            setTimeout(() => {
                lightssRef.current.forEach((light) =>
                    light.classList.remove("light-twinkling")
                );
            }, 3000);
            setTimeout(() => {
                setShowInputLottery(false);
                setTimeout(() => {
                    setInputLottery(false);
                    setInputSpinning(false);
                }, 1000);
            }, 4000);
        };
        inputStartSpin();
    };

    const spin = () => {
        if (isSpinning) return;
        setIsSpinning(true);
        lightsRef.current.forEach((light) =>
            light.classList.add("light-twinkling")
        );

        const rotateDeg = Math.random() * 360 + 1080; // Rotate 3 to 4 full turns
        const newDeg = currentDeg + rotateDeg;
        setCurrentDeg(newDeg);

        setTimeout(() => {
            lightsRef.current.forEach((light) =>
                light.classList.remove("light-twinkling")
            );
            setIsSpinning(false);
        }, 3000); // Spin duration
        // spin again
    };
    setInterval(spin, 7000);
    const handleBetChange = (e: string) => {
        setBet(Number(e));
    };

    return (
        <>
            <div className="page-title">
                <div className="page-title-cell inter">
                    <b className="page-title-cell-title inter">Лотерея</b>
                </div>
                <div className="page-title-cell inter">
                    {currentLottery ? (
                        <>
                            <b className="page-title-cell-title">
                                Общий оборот:
                            </b>{" "}
                            {currentLottery}{" "}
                            {currentLottery % 10 === 1 &&
                            currentLottery % 100 !== 11
                                ? "монета"
                                : 2 <= currentLottery % 10 &&
                                    currentLottery % 10 <= 4 &&
                                    !(
                                        12 <= currentLottery % 100 &&
                                        currentLottery % 100 <= 14
                                    )
                                  ? "монеты"
                                  : "монет"}
                        </>
                    ) : remainStringTime ? (
                        <>
                            <b className="page-title-cell-title">
                                Общий оборот:{" "}
                            </b>
                            0
                        </>
                    ) : (
                        <></>
                    )}
                </div>
                {remainStringTime ? (
                    <div className="page-title-cell inter">
                        <b className="page-title-cell-title">Осталось:</b>{" "}
                        {remainStringTime}
                    </div>
                ) : (
                    <div className="page-title-cell inter">
                        <b>Лотерея не началась</b>
                    </div>
                )}
            </div>
            <div className="page-other">
                <button
                    className="cell btn-money inter"
                    disabled={remainStringTime === ""}
                    onClick={makeDeposit}
                >
                    💰Сделать депозит💰
                </button>
                <button
                    className="cell inter btn-def"
                    disabled={remainStringTime === ""}
                    onClick={showTopDeposits}
                >
                    Топ депозитов
                </button>
                <div className="wrapper inter">
                    {Array.from({ length: 10 }, (_, i) => (
                        <div
                            key={i}
                            className="light"
                            ref={(el) => {
                                if (el) lightsRef.current[i] = el;
                            }}
                        ></div>
                    ))}
                    <div className="panel">
                        {segments.map((segment, index) => (
                            <div
                                key={index}
                                className="sector"
                                style={{
                                    transform: `rotate(${index * 36 - 18}deg)`,
                                }}
                            >
                                <div className="sector-inner">
                                    <span>{segment}</span>
                                </div>
                            </div>
                        ))}
                        <div
                            className="pointer"
                            ref={pointerRef}
                            style={{ transform: `rotate(${currentDeg}deg)` }}
                        ></div>
                    </div>
                </div>
            </div>
            <NavBar stricted={false} />
            {inputLottery && (
                <div className={`popup ${showInputLottery ? "show" : ""}`}>
                    <button
                        className="inter"
                        style={{
                            position: "absolute",
                            right: "10px",
                            top: "10px",
                            color: "red",
                            backgroundColor: "white",
                        }}
                        onClick={() => {
                            setShowInputLottery(false);
                            setTimeout(() => {
                                setInputLottery(false);
                            }, 1000);
                        }}
                    >
                        ✕
                    </button>
                    <div className="wrapper">
                        {Array.from({ length: 10 }, (_, i) => (
                            <div
                                key={i}
                                className="light"
                                ref={(el) => {
                                    if (el) lightssRef.current[i] = el;
                                }}
                            ></div>
                        ))}
                        <div className="panel">
                            {inputSegments.map((segment, index) => (
                                <div
                                    key={index}
                                    className="sector"
                                    style={{
                                        transform: `rotate(${index * 36 - 18}deg)`,
                                    }}
                                >
                                    <div className="sector-inner">
                                        <span>{segment}</span>
                                    </div>
                                </div>
                            ))}
                            <div
                                className="pointer"
                                ref={pointerRef}
                                style={{ transform: `rotate(${inputDeg}deg)` }}
                            ></div>
                        </div>
                    </div>
                    <div
                        style={{
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center",
                            alignItems: "center",
                        }}
                    >
                        <label
                            className="inter"
                            style={{
                                alignSelf: "center",
                                padding: "10px",
                                fontSize: "2rem",
                            }}
                        >
                            Ставка
                        </label>
                        <NumberInput
                            className="cell inter"
                            onChange={handleBetChange}
                        />
                        <button
                            className="cell btn-money inter"
                            onClick={() => deposit()}
                        >
                            Депозит
                        </button>
                    </div>
                </div>
            )}
            {showTopWinners && (
                <>
                    <div
                        className={`top-winners ${topWinnersClass ? "show" : ""}`}
                    >
                        <div className="top-winners-inner">
                            <button
                                className="inter"
                                style={{
                                    position: "absolute",
                                    right: "10px",
                                    top: "10px",
                                    color: "red",
                                    backgroundColor: "white",
                                }}
                                onClick={() => {
                                    setShowTopWinners(false);
                                    setTopWinnersClass(false);
                                }}
                            >
                                ✕
                            </button>
                            <h2 className="inter">Топ депозитов</h2>
                            <ul
                                style={{
                                    maxHeight: "80vh",
                                    overflowY: "scroll",
                                    overflowX: "hidden",
                                }}
                            >
                                {topWinners.map((winner, index) => (
                                    <li
                                        key={index}
                                        className="inter"
                                        style={{
                                            display: "flex",
                                            justifyContent: "space-evenly",
                                            alignItems: "center",
                                            marginTop: "4px",
                                        }}
                                    >
                                        <span>{index + 1}. </span>
                                        <span>{winner.username} </span>
                                        <span>
                                            {winner.bet}TON *{" "}
                                            {winner.multiplier}x
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </>
            )}
        </>
    );
};

export default Lottery;
