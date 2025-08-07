import { useCallback, useEffect, useState } from "react";
import NavBar from "../NavBar";
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

const Game: React.FC = () => {
    const [balance, setBalance] = useState<number>(0);
    const [bonus, setBonus] = useState<boolean>(false);
    const [money, setMoney] = useState<number>(0);
    const [newVisit, setNewVisit] = useState<Date | null>(null);

    useEffect(() => {
        const fetchGameParams = () => {
            axios.post("/api/game/params/get").then((response) => {
                const data = response.data;
                if (data.ok) {
                    setBalance(data.params.money);
                    setBonus(data.params.bonus);
                    setNewVisit(data.params.last_visit);
                }
            });
        };
        fetchGameParams();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    //TODO: Game fetching at the end

    // <iframe
    // src={"/KickTheDoll.html"}
    // title="Game"
    // width={"100%"}
    // style={{ height: "90vh" }}
    // />
    const updateMoney = useCallback((msg: MessageEvent) => {
        if (msg.data === "1") {
            setMoney((data) => data + 1);
        }
    }, []);
    const fetchMoney = useCallback(() => {
        axios.post("/api/game/money", {
            bet: money,
        });
    }, []);

    useEffect(() => {
        window.addEventListener("message", updateMoney);
        window.addEventListener("unload", fetchMoney);
        return () => {
            window.removeEventListener("message", updateMoney);
            window.removeEventListener("unload", fetchMoney);
            fetchMoney();
        };
    }, [updateMoney, fetchMoney]);
    return (
        <div style={{ backgroundColor: "rgb(36, 32, 32)" }}>
            <div className="page-title">
                {!bonus ? (
                    <div className="page-title-cell inter">
                        {/* <b className="page-title-cell-title">До следующего бонуса: </b>{remainStringTime} */}
                    </div>
                ) : null}
                <div className="page-title-cell inter">
                    <b className="page-title-cell-title">Баланс: </b>
                    {formatLargeNumber(balance + money)}{" "}
                    {(balance + money) % 10 === 1 &&
                    (balance + money) % 100 !== 11
                        ? "монета"
                        : 2 <= (balance + money) % 10 &&
                            (balance + money) % 10 <= 4 &&
                            !(
                                12 <= (balance + money) % 100 &&
                                (balance + money) % 100 <= 14
                            )
                          ? "монеты"
                          : "монет"}
                </div>
                {bonus ? (
                    <div className="page-title-cell inter">
                        <b className="page-title-cell-title">Бонус активен</b>
                    </div>
                ) : null}
            </div>
            <iframe
                src="/assets/KickTheDoll.html"
                title="Game"
                width={"100%"}
                style={{
                    height: "81vh",
                    marginTop: "9vh",
                    marginBottom: "10vh",
                }}
            />
            <NavBar stricted={false} fromGame={true} />
        </div>
    );
};

export default Game;
