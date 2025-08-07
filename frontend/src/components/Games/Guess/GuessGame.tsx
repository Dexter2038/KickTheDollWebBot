import { useEffect, useState } from "react";

import "./GuessGame.css";
import NavBar from "../../NavBar";
import { toast } from "react-toastify";
import getLaunchParams from "../../RetrieveLaunchParams";
import NumberInput from "../../NumberInput";
import axios from "axios";

interface Coin {
    name: string;
    symbol: string;
    price: string;
}

const GuessPage: React.FC = () => {
    const { initDataRaw, initData } = getLaunchParams();
    const [coins, setCoins] = useState<Coin[]>([]);
    const [showClass, setShowClass] = useState<boolean>(false);
    const [showPopup, setShowPopup] = useState<boolean>(false);
    const [bet, setBet] = useState<number>(0);
    const [curCoin, setCurCoin] = useState<number>(-1);

    const [time, setTime] = useState<string>("");
    const [way, setWay] = useState<boolean | null>(null);

    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const handleChange = (e: any) => {
        setTime(e.target.value);
    };
    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const handleWayChange = (e: any) => {
        setWay(e.target.checked);
    };

    useEffect(() => {
        const updateCoins = async () => {
            try {
                const { data } = await axios.get("/api/guess/currencies");
                if (data.ok) {
                    setCoins(data.coins);
                } else {
                    toast.error(
                        "Ошибка в получении данных. Перезагрузите страницу"
                    );
                }
            } catch {
                toast.error(
                    "Ошибка в получении данных. Перезагрузите страницу"
                );
            }
        };
        updateCoins();
    }, []);

    const toBet = (coin_id: number) => {
        setCurCoin(coin_id);
        openBetPopup();
    };

    const createBet = async () => {
        if (!bet || !time || way === null) {
            toast.error("Необходимо заполнить все поля");
            return;
        }
        let { data } = await axios.post("/api/money/check", {
            initData: initDataRaw,
            player_id: initData?.user?.id,
            bet,
        });
        if (!data.ok) {
            toast.error("Недостаточно монет");
            return;
        }

        data = (
            await axios.post("/api/money/bet", {
                initData: initDataRaw,
                player_id: initData?.user?.id,
                bet,
                coin_name: coins[curCoin].name,
                time,
                way,
            })
        ).data;
        if (data.ok) {
            toast.success("Ставка сделана");
        } else {
            toast.error(data.msg);
            return;
        }
        closeBetPopup();
    };

    const openBetPopup = (): void => {
        setShowClass(true);
        setTimeout(() => {
            setShowPopup(true);
        }, 50);
        setWay(false);
    };

    const closeBetPopup = (): void => {
        setShowClass(false);
        setTimeout(() => {
            setShowPopup(false);
        }, 1000);
        setTime("");
        setWay(null);
    };

    const handleBetChange = (num: string) => {
        setBet(Number(num));
    };

    const showBetPopup = (): JSX.Element => {
        return (
            <div
                id="createPopup"
                className={`popup ${showClass ? "show" : ""}`}
            >
                <div className="popup-content">
                    <h2>Угадать</h2>
                    <h2>{coins[curCoin].name}</h2>
                    <label>Ставка</label>
                    <NumberInput
                        value={bet.toString()}
                        onChange={handleBetChange}
                    />
                    <form>
                        <ul
                            id="filter1"
                            className="filter-switch inline-flex items-center relative h-10 p-1 space-x-1 bg-gray-200 rounded-md font-semibold text-blue-600 my-4"
                        >
                            <li className="filter-switch-item flex relative h-8 bg-gray-300x">
                                <input
                                    type="radio"
                                    onClick={handleChange}
                                    value="6h"
                                    name="filter1"
                                    id="filter1-0"
                                    className="sr-only"
                                />
                                <label
                                    htmlFor="filter1-0"
                                    className="h-8 py-1 px-2 text-sm leading-6 text-gray-600 hover:text-gray-800 bg-white rounded shadow"
                                >
                                    6ч
                                </label>
                                <div
                                    aria-hidden="true"
                                    className="filter-active"
                                ></div>
                            </li>
                            <li className="filter-switch-item flex relative h-8 bg-gray-300x">
                                <input
                                    type="radio"
                                    onClick={handleChange}
                                    value="12h"
                                    name="filter1"
                                    id="filter1-1"
                                    className="sr-only"
                                />
                                <label
                                    htmlFor="filter1-1"
                                    className="h-8 py-1 px-2 text-sm leading-6 text-gray-600 hover:text-gray-800 bg-white rounded shadow"
                                >
                                    12ч
                                </label>
                            </li>
                            <li className="filter-switch-item flex relative h-8 bg-gray-300x">
                                <input
                                    type="radio"
                                    onClick={handleChange}
                                    value="24h"
                                    name="filter1"
                                    id="filter1-2"
                                    className="sr-only"
                                />
                                <label
                                    htmlFor="filter1-2"
                                    className="h-8 py-1 px-2 text-sm leading-6 text-gray-600 hover:text-gray-800 bg-white rounded shadow"
                                >
                                    1д
                                </label>
                            </li>
                            <li className="filter-switch-item flex relative h-8 bg-gray-300x">
                                <input
                                    type="radio"
                                    onClick={handleChange}
                                    value="48h"
                                    name="filter1"
                                    id="filter1-3"
                                    className="sr-only"
                                />
                                <label
                                    htmlFor="filter1-3"
                                    className="h-8 py-1 px-2 text-sm leading-6 text-gray-600 hover:text-gray-800 bg-white rounded shadow"
                                >
                                    2д
                                </label>
                            </li>
                        </ul>
                    </form>
                    <form>
                        <label className="toggle">
                            <input type="checkbox" onClick={handleWayChange} />
                            <span
                                className="labels"
                                data-on="📈"
                                data-off="📉"
                            ></span>
                        </label>
                    </form>
                    <div className="popup-buttons">
                        <button
                            type="submit"
                            className="btn-create"
                            onClick={createBet}
                        >
                            Создать
                        </button>
                        <button
                            type="button"
                            className="btn-cancel"
                            onClick={closeBetPopup}
                        >
                            Отменить
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <>
            <div className="table-container">
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                    <thead>
                        <tr>
                            <th>№</th>
                            <th></th>
                            <th style={{ textAlign: "left" }}>Название</th>
                            <th style={{ textAlign: "center" }}>Цена</th>
                        </tr>
                    </thead>
                    <tbody>
                        {coins.map((coin, index) => (
                            <tr key={index}>
                                <td
                                    style={{
                                        fontWeight: "bold",
                                        textAlign: "center",
                                    }}
                                >
                                    {index + 1}
                                </td>
                                <td style={{ textAlign: "center" }}>
                                    <img
                                        src={`${coin.name.toLowerCase()}-${coin.symbol.toLowerCase()}-logo.svg`}
                                        width={"40px"}
                                        height={"40px"}
                                    />
                                </td>
                                <td className="coin-name">
                                    {coin.name}{" "}
                                    <p className="coin-symbol">{coin.symbol}</p>
                                </td>
                                <td
                                    className="coin-price"
                                    style={{ textAlign: "center" }}
                                >
                                    {coin.price}
                                </td>
                                <td>
                                    <button
                                        className="coin-btn"
                                        onClick={() => toBet(index)}
                                    >
                                        Поставить
                                    </button>
                                </td>
                            </tr>
                        ))}
                        <tr style={{ visibility: "hidden" }}>
                            <td>1</td>
                        </tr>
                        <tr style={{ visibility: "hidden" }}>
                            <td>1</td>
                        </tr>
                        <tr style={{ visibility: "hidden" }}>
                            <td>1</td>
                        </tr>
                        <tr style={{ visibility: "hidden" }}>
                            <td>1</td>
                        </tr>
                        <tr style={{ visibility: "hidden" }}>
                            <td>1</td>
                        </tr>
                        <tr style={{ visibility: "hidden" }}>
                            <td>1</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <NavBar stricted={false} />
            {showPopup && showBetPopup()}
        </>
    );
};

export default GuessPage;
