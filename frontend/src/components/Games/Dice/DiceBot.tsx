import { useEffect, useRef, useState } from "react";
import { toast } from "react-toastify";

const DiceBot: React.FC = () => {
    const [player1Result, setPlayer1Result] = useState<number>(0);
    const [botResult, setBotResult] = useState<number>(0);
    const [activePlayer, setActivePlayer] = useState<boolean>(true); // Player starts first
    const cube1Ref = useRef<HTMLDivElement>(null);
    const cube2Ref = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // If it's the bot's turn, trigger its roll automatically
        if (!activePlayer) {
            setTimeout(() => {
                botRoll();
            }, 1500);
        }
    }, [activePlayer]);

    const getRandomInt = (min: number, max: number): number => {
        return Math.floor(Math.random() * (max - min + 1)) + min;
    };

    const rollDice = (
        cubeRef: React.RefObject<HTMLDivElement>,
        result: number
    ) => {
        const rotations = Array.from({ length: 20 }, () => ({
            x: getRandomInt(-90, 90),
            y: getRandomInt(-180, 180),
            z: getRandomInt(-180, 180),
        }));

        const finalRotation = getFinalRotation(result);
        let rotationIndex = 0;

        const animate = () => {
            if (rotationIndex < rotations.length) {
                if (cubeRef.current) {
                    const { x, y, z } = rotations[rotationIndex];
                    cubeRef.current.style.transform = `translateZ(-100px) rotateX(${x}deg) rotateY(${y}deg) rotateZ(${z}deg)`;
                }
                rotationIndex++;
                requestAnimationFrame(animate);
            } else if (cubeRef.current) {
                cubeRef.current.style.transform = `translateZ(-100px) rotateX(${finalRotation.x}deg) rotateY(${finalRotation.y}deg) rotateZ(${finalRotation.z}deg)`;
            }
        };

        animate();
    };

    const getFinalRotation = (result: number) => {
        switch (result) {
            case 1:
                return { x: 0, y: 0, z: 0 };
            case 2:
                return { x: 0, y: 180, z: 0 };
            case 3:
                return { x: 0, y: -90, z: 0 };
            case 4:
                return { x: 0, y: 90, z: 0 };
            case 5:
                return { x: -90, y: 0, z: 0 };
            case 6:
                return { x: 90, y: 0, z: 0 };
            default:
                return { x: 0, y: 0, z: 0 };
        }
    };

    const playerRoll = () => {
        const result = getRandomInt(1, 6);
        setPlayer1Result(result);
        rollDice(cube1Ref, result);
        setActivePlayer(false); // Switch to bot's turn
    };

    const botRoll = () => {
        const result = getRandomInt(1, 6);
        setBotResult(result);
        rollDice(cube2Ref, result);
        determineWinner(result);
    };

    const determineWinner = (botScore: number) => {
        if (player1Result > botScore) {
            toast.success("Вы выиграли!");
        } else if (player1Result < botScore) {
            toast.warn("Бот выиграл.");
        } else {
            toast.info("Ничья");
        }
        setTimeout(() => setActivePlayer(true), 2000); // Reset for the next round
    };

    return (
        <>
            <div className="page-title">
                <div className="page-title-cell">
                    <b className="page-title-cell-title">Бот:</b> {botResult}
                </div>
                <div className="page-title-cell">
                    <b className="page-title-cell-title">Вы:</b> {player1Result}
                </div>
                <div className="page-title-cell">
                    <span>{activePlayer ? "Ваш ход" : "Ход бота"}</span>
                </div>
            </div>
            <div className="page-other">
                <button
                    type="button"
                    className="cell btn-money"
                    id="rollButton"
                    onClick={playerRoll}
                    disabled={!activePlayer}
                >
                    Бросить кубик
                </button>
                <div className="scene">
                    <div className="cube1" ref={cube1Ref}>
                        <div className="cube__face cube__face--1">1</div>
                        <div className="cube__face cube__face--2">2</div>
                        <div className="cube__face cube__face--3">3</div>
                        <div className="cube__face cube__face--4">4</div>
                        <div className="cube__face cube__face--5">5</div>
                        <div className="cube__face cube__face--6">6</div>
                    </div>
                </div>
                <div className="scene">
                    <div className="cube2" ref={cube2Ref}>
                        <div className="cube__face cube__face--1">1</div>
                        <div className="cube__face cube__face--2">2</div>
                        <div className="cube__face cube__face--3">3</div>
                        <div className="cube__face cube__face--4">4</div>
                        <div className="cube__face cube__face--5">5</div>
                        <div className="cube__face cube__face--6">6</div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default DiceBot;
