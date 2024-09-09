import { useEffect, useRef, useState } from "react";

import "./GuessGame.css";
import NavBar from "../../NavBar";
import { toast } from "react-toastify";

interface Coin {
    name: string;
    symbol: string;
    price: string;
}

const GuessPage: React.FC = () => {

    const [coins, setCoins] = useState<Coin[]>([])
    const [showClass, setShowClass] = useState<boolean>(false);
    const [showPopup, setShowPopup] = useState<boolean>(false);
    const betRef = useRef<HTMLInputElement>(null);
    const [curCoin, setCurCoin] = useState<number>(-1);

    const [time, setTime] = useState<string>("")
    const [way, setWay] = useState<boolean | null>(null)

    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const handleChange = (e: any) => {
        setTime(e.target.value)
    }
    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const handleWayChange = (e: any) => {
        setWay(e.target.checked)
    }

    useEffect(() => {
        const updateCoins = async () => {
            try {
                const response = await fetch('/api/guess/currencies',
                    {
                        method: 'GET',
                    });
                const data = await response.json();
                if (data.ok) {
                    setCoins(data.coins);
                } else {
                    toast.error("Ошибка в получении данных. Перезагрузите страницу");
                }
            } catch {
                toast.error("Ошибка в получении данных. Перезагрузите страницу");
                const newCoins = [
                    { name: 'Bitcoin', symbol: 'BTC', price: '$58,574.70' },
                    { name: 'Ethereum', symbol: 'ETH', price: '$2,519.24' },
                    { name: 'Tether', symbol: 'USDT', price: '$0.9999' },
                    { name: 'BNB', symbol: 'BNB', price: '$522.22' },
                    { name: 'Solana', symbol: 'SOL', price: '$133.07' },
                    { name: 'USDC', symbol: 'USDC', price: '$1.00' },
                    { name: 'XRP', symbol: 'XRP', price: '$0.5578' },
                    { name: 'Dogecoin', symbol: 'DOGE', price: '$0.09768' },
                    { name: 'TRON', symbol: 'TRX', price: '$0.1564' },
                    { name: 'Toncoin', symbol: 'TON', price: '$5.15' },
                    { name: 'Cardano', symbol: 'ADA', price: '$0.33' },
                    { name: 'Avalanche', symbol: 'AVAX', price: '$22.16' },
                    { name: 'Shiba Inu', symbol: 'SHIB', price: '$0.00001347' },
                    { name: 'Chainlink', symbol: 'LINK', price: '$10.69' },
                    { name: 'Bitcoin Cash', symbol: 'BCH', price: '$321.48' },
                    { name: 'Polkadot', symbol: 'DOT', price: '$4.17' },
                    { name: 'UNUS SED LEO', symbol: 'LEO', price: '$5.83' },
                    { name: 'Dai', symbol: 'DAI', price: '$1.00' },
                    { name: 'Litecoin', symbol: 'LTC', price: '$64.57' },
                    { name: 'NEAR Protocol', symbol: 'NEAR', price: '$3.97' },
                ];
                setCoins(newCoins);
            }
        }
        updateCoins();
    }, [])

    const bet = (coin_id: number) => {
        setCurCoin(coin_id);
        openBetPopup();
    }

    const createBet = () => {
        const bet = betRef.current?.value
        if (!bet || !time || way === null) {
            toast.error("Необходимо заполнить все поля")
            return
        }
        //TODO:
        closeBetPopup();
    }

    const openBetPopup = (): void => {
        setShowClass(true);
        setTimeout(() => {
            setShowPopup(true);
        }, 50)
        setWay(false);
    }

    const closeBetPopup = (): void => {
        setShowClass(false);
        setTimeout(() => {
            setShowPopup(false);
        }, 1000)
        setTime("");
        setWay(null);
    }


    const showBetPopup = (): JSX.Element => {
        return (
            <div id="createPopup" className={`popup ${showClass ? "show" : ""}`}>
                <div className="popup-content">
                    <h2>Угадать</h2>
                    <h2>{coins[curCoin].name}</h2>
                    <label>Ставка</label>
                    <input type="number" ref={betRef} name="game-name" />
                    <form>
                        <ul id="filter1" className="filter-switch inline-flex items-center relative h-10 p-1 space-x-1 bg-gray-200 rounded-md font-semibold text-blue-600 my-4">
                            <li className="filter-switch-item flex relative h-8 bg-gray-300x">
                                <input type="radio" onClick={handleChange} value="6h" name="filter1" id="filter1-0" className="sr-only" />
                                <label htmlFor="filter1-0" className="h-8 py-1 px-2 text-sm leading-6 text-gray-600 hover:text-gray-800 bg-white rounded shadow">
                                    6ч
                                </label>
                                <div aria-hidden="true" className="filter-active"></div>
                            </li>
                            <li className="filter-switch-item flex relative h-8 bg-gray-300x">
                                <input type="radio" onClick={handleChange} value="12h" name="filter1" id="filter1-1" className="sr-only" />
                                <label htmlFor="filter1-1" className="h-8 py-1 px-2 text-sm leading-6 text-gray-600 hover:text-gray-800 bg-white rounded shadow">
                                    12ч
                                </label>
                            </li>
                            <li className="filter-switch-item flex relative h-8 bg-gray-300x">
                                <input type="radio" onClick={handleChange} value="24h" name="filter1" id="filter1-2" className="sr-only" />
                                <label htmlFor="filter1-2" className="h-8 py-1 px-2 text-sm leading-6 text-gray-600 hover:text-gray-800 bg-white rounded shadow">
                                    1д
                                </label>
                            </li>
                            <li className="filter-switch-item flex relative h-8 bg-gray-300x">
                                <input type="radio" onClick={handleChange} value="48h" name="filter1" id="filter1-3" className="sr-only" />
                                <label htmlFor="filter1-3" className="h-8 py-1 px-2 text-sm leading-6 text-gray-600 hover:text-gray-800 bg-white rounded shadow">
                                    2д
                                </label>
                            </li>
                        </ul>
                    </form>
                    <form>
                        <label className="toggle">
                            <input type="checkbox" onClick={handleWayChange} />
                            <span className="labels" data-on="📈" data-off="📉"></span>
                        </label>
                    </form>
                    <div className="popup-buttons">
                        <button type="submit" className="btn-create" onClick={createBet}>
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
                                <td style={{ fontWeight: "bold", textAlign: "center" }}>{index + 1}</td>
                                <td style={{ textAlign: "center" }}><img src={`${coin.name.toLowerCase()}-${coin.symbol.toLowerCase()}-logo.svg`} width={"40px"} height={"40px"} /></td>
                                <td className="coin-name">{coin.name} <p className="coin-symbol">{coin.symbol}</p></td>
                                <td className="coin-price" style={{ textAlign: "center" }}>{coin.price}</td>
                                <td><button className="coin-btn" onClick={() => bet(index)}>Поставить</button></td>
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
}

export default GuessPage;