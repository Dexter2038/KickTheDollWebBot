import { retrieveLaunchParams } from "@telegram-apps/sdk";
import { useEffect, useRef, useState } from "react"
import { useSearchParams } from "react-router-dom";
import { toast } from "react-toastify";


const DiceGame: React.FC = () => {
    const [searchParams] = useSearchParams();
    const roomId = searchParams.get("room_id");
    const { initDataRaw, initData } = { initDataRaw: "2", initData: "2" }
    const playerId = initData?.user?.id;
    const [selfSteps, setSelfSteps] = useState<number>(0);
    const [otherSteps, setOtherSteps] = useState<number>(0);
    const [player1Result, setPlayer1Result] = useState<number>(0);
    const [player2Result, setPlayer2Result] = useState<number>(0);
    const [activePlayer, setActivePlayer] = useState<boolean>(false);
    const [reward, setReward] = useState<number>(0);
    const cube1Ref = useRef<HTMLDivElement>(null);
    const cube2Ref = useRef<HTMLDivElement>(null);


    useEffect(() => {
        const getReward = async () => {
            try {
                const response = await fetch(`/api/dice/reward?room_id=${roomId}`, {
                    method: "GET"
                });
                const data = await response.json();
                setReward(data.reward);
            } catch {
                toast.error("Произошла ошибка.");
            }
        };
        getReward();
        const interval = setInterval(getDiceUpdates, 1500);
        return () => clearInterval(interval);
    });

    const getDiceUpdates = async () => {
        try {
            const response = await fetch(`/api/dice/updates?player_id=${playerId}&room_id=${roomId}`, {
                method: "GET",
            });
            const data = await response.json();
            if (response.ok) {
                if (data.msg !== "Обновления успешно получены.") {
                    toast(data.msg);
                }
                if (selfSteps !== data.self.count) {
                    setSelfSteps(data.self.count);
                    rollDiceSelf(data.self.hands);
                }
                if (otherSteps !== data.opponent.count) {
                    setOtherSteps(data.opponent.count);
                    rollDiceOpponent(data.opponent.hands);
                }
                setActivePlayer(data.data.active_player);
                setPlayer1Result(data.self.results);
                setPlayer2Result(data.opponent.results);
            }
        } catch (error) {
            toast.error("Произошла ошибка.");
        }
    };

    const roll = async () => {
        try {
            const response = await fetch("/api/dice/roll", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ player_id: playerId, room_id: roomId, initData: initDataRaw }),
            });
            const data = await response.json();
            if (response.ok) {
                if (data.msg !== "Вы бросили кубики.") {
                    toast(data.msg);
                }
                rollDiceSelf(data.self.hands);

            }
        } catch (error) {
            toast.error("Произошла ошибка.");
        }
    }

    const getRandomInt = (min: number, max: number): number => {
        min = Math.ceil(min);
        max = Math.floor(max);
        return Math.floor(Math.random() * (max - min) + min); // The maximum is exclusive and the minimum is inclusive
    }
    interface Coords {
        x: number, y: number, z: number
    }
    const rollDiceSelf = (result: number): void => {
        const rotations: Coords[] = [];
        for (let i = 0; i < 20; i++) { // 20 rotations for a more realistic roll
            rotations.push({
                x: getRandomInt(-90, 90),
                y: getRandomInt(-180, 180),
                z: getRandomInt(-180, 180)
            });
        }
        const finalRotation = {
            x: 0,
            y: 0,
            z: 0
        };
        if (result === 1) { finalRotation.y = 0; }
        if (result === 2) { finalRotation.y = 180; }
        if (result === 3) { finalRotation.y = -90; }
        if (result === 4) { finalRotation.y = 90; }
        if (result === 5) { finalRotation.x = -90; }
        if (result === 6) { finalRotation.x = 90; }

        let rotationIndex = 0;
        const animate = function () {
            if (rotationIndex < rotations.length) {
                if (cube1Ref.current) {
                    cube1Ref.current.style.transform = 'translateZ(-100px) rotateX(' + rotations[rotationIndex].x + 'deg) rotateY(' + rotations[rotationIndex].y + 'deg) rotateZ(' + rotations[rotationIndex].z + 'deg)';
                } rotationIndex++;
                requestAnimationFrame(animate);
            } else {
                // Final rotation
                if (cube1Ref.current) {
                    cube1Ref.current.style.transform = 'translateZ(-100px) rotateX(' + finalRotation.x + 'deg) rotateY(' + finalRotation.y + 'deg) rotateZ(' + finalRotation.z + 'deg)';
                }
            }
        };
        animate();
    }

    const rollDiceOpponent = (result: number): void => {
        const rotations: Coords[] = [];
        for (let i = 0; i < 20; i++) { // 20 rotations for a more realistic roll
            rotations.push({
                x: getRandomInt(-90, 90),
                y: getRandomInt(-180, 180),
                z: getRandomInt(-180, 180)
            });
        }
        const finalRotation = {
            x: 0,
            y: 0,
            z: 0
        };
        if (result === 1) { finalRotation.y = 0; }
        if (result === 2) { finalRotation.y = 180; }
        if (result === 3) { finalRotation.y = -90; }
        if (result === 4) { finalRotation.y = 90; }
        if (result === 5) { finalRotation.x = -90; }
        if (result === 6) { finalRotation.x = 90; }

        let rotationIndex = 0;
        const animate = function () {
            if (rotationIndex < rotations.length) {
                if (cube2Ref.current) {
                    cube2Ref.current.style.transform = 'translateZ(-100px) rotateX(' + rotations[rotationIndex].x + 'deg) rotateY(' + rotations[rotationIndex].y + 'deg) rotateZ(' + rotations[rotationIndex].z + 'deg)';
                } rotationIndex++;
                requestAnimationFrame(animate);
            } else {
                // Final rotation
                if (cube2Ref.current) {
                    cube2Ref.current.style.transform = 'translateZ(-100px) rotateX(' + finalRotation.x + 'deg) rotateY(' + finalRotation.y + 'deg) rotateZ(' + finalRotation.z + 'deg)';
                }
            }
        };
        animate();
    }



    return <>
        <div className="page-title">
            <div className="page-title-cell">
                <b className="page-title-cell-title">Противник:</b> {player2Result}
            </div>
            <div className="page-title-cell">
                <b className="page-title-cell-title">Вы:</b> {player1Result}
            </div>
            <div className="page-title-cell">
                <b className="page-title-cell-title">Награда💰:</b> {reward}$
            </div>
            <div className="page-title-cell">
                <span>{activePlayer ? "Ваш ход" : "Ход противника"}</span>
            </div>
        </div>
        <div className="page-other">
            <button type="button" className="cell btn-money" id="rollButton" onClick={roll} disabled={!activePlayer}>Бросить кубик</button>
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
}

export default DiceGame;