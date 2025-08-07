import { useEffect, useState } from "react";
import {
    TonConnectError,
    useTonAddress,
    useTonConnectUI,
    useTonWallet,
} from "@tonconnect/ui-react";
import { fetchData, fetchHistory, fetchTonBalance } from "./Utils";
import { toast } from "react-toastify";
import NavBar from "../NavBar";
import getLaunchParams from "../RetrieveLaunchParams";
import NumberInput from "../NumberInput";
import axios from "axios";

interface Transaction {
    id: string;
    transaction_type: string;
    amount: number;
    created_at: string;
    transaction_hash: string;
    confirmed: boolean;
}

function toNano(nano: string): string {
    return String(Number(nano) / 1000000000);
}

function formatLargeNumber(num: number) {
    const suffixes = ["", "K", "M", "B", "T", "Q", "Qi", "Sx", "Sp", "Oc"];
    let i = 0;
    while (num >= 1000 && i < suffixes.length - 1) {
        num /= 1000;
        i++;
    }

    return num.toFixed(2) + suffixes[i];
}

/**
 * A functional component that displays the user's balance and provides options to withdraw, deposit, and view transaction history.
 *
 * @return {JSX.Element} The JSX element representing the balance page.
 */
const Balance: React.FC = (): JSX.Element => {
    const { initDataRaw, initData } = getLaunchParams();
    const [depositPopup, setDepositPopup] = useState<boolean>(false);
    const [historyPopup, setHistoryPopup] = useState<boolean>(false);
    const [moneyBalance, setMoneyBalance] = useState<number>(0);
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [tonBalance, setTonBalance] = useState<number>(0);
    const tonWallet = useTonWallet();
    const [tonConnectUI] = useTonConnectUI();
    const [walletSet, setWalletSet] = useState<boolean>(false);
    const tonAddress = useTonAddress(false);
    const [depositNumber, setDeposit] = useState(0);

    useEffect(() => {
        async function main() {
            try {
                const [balance, transactions] = await Promise.all([
                    fetchData(initDataRaw, initData?.user?.id),
                    fetchHistory(initDataRaw, initData?.user?.id),
                ]);

                if (balance === -1) {
                    toast.error(
                        "Не удалось получить данные. Перезагрузите страницу"
                    );
                } else {
                    setMoneyBalance(balance);
                }

                setTransactions(transactions);
            } catch (error) {
                console.error(error);
            }
        }

        main();

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    useEffect(() => {
        if (tonWallet) {
            fetchTonBalance(initDataRaw, initData?.user?.id).then((balance) => {
                if (balance == -1) {
                    toast.error("Перепривяжите TON кошелёк");
                } else setTonBalance(balance);
            });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [tonWallet]);

    tonConnectUI.onStatusChange((wallet) => {
        if (wallet) {
            setWalletSet(true);
        }
    });

    useEffect(() => {
        const updateWallet = async () => {
            const { data } = await axios.post("/api/wallet/connect", {
                initData: initDataRaw,
                player_id: initData?.user?.id,
                wallet_address: tonAddress,
            });
            if (!data.ok) {
                toast.error(data.msg);
            }
        };
        if (walletSet) updateWallet();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [walletSet]);

    const moneyEnding: string =
        moneyBalance % 10 === 1 && moneyBalance % 100 !== 11
            ? "монета"
            : 2 <= moneyBalance % 10 &&
                moneyBalance % 10 <= 4 &&
                !(12 <= moneyBalance % 100 && moneyBalance % 100 <= 14)
              ? "монеты"
              : "монет";

    const showDepositPopup = (): JSX.Element => {
        const closeDeposit = (): void => {
            const popup = document.getElementById("depositPopup");
            popup?.classList.remove("show");
            setTimeout(() => {
                setDepositPopup(false);
            }, 100);
        };

        const deposit = async (): Promise<void> => {
            if (depositNumber < 0) {
                toast.error("Неверная сумма депозита");
                return;
            }
            const { data } = await axios.post("/api/wallet/deposit", {
                amount: depositNumber,
                initData: initDataRaw,
            });
            if (!data.ok) {
                toast.error("Выполнить депозит в данный момент невозможно");
                return;
            }
            if (depositNumber)
                tonConnectUI
                    .sendTransaction({
                        validUntil: Math.floor(Date.now() / 1000) + 360,
                        messages: [
                            {
                                address: data.wallet_address,
                                amount: toNano(
                                    depositNumber.toString()
                                ).toString(),
                            },
                        ],
                    })
                    .then(async () => {
                        await axios.post("/api/balance/deposit", {
                            amount: depositNumber,
                            initData: initDataRaw,
                            player_id: initData?.user?.id,
                        });
                    })
                    .catch((e: TonConnectError) => {
                        if ("USER_REJECTS_ERROR" in e) {
                            toast.error("Вы отклонили транзакцию");
                        } else if ("UNKNOWN_ERROR" in e) {
                            toast.error("Произошла неизвестная ошибка");
                        } else if ("BAD_REQUEST_ERROR" in e) {
                            toast.error("Вы ввели некорректные данные");
                        } else if ("UNKNOWN_APP_ERROR" in e) {
                            toast.error("Проблема с приложением");
                        } else if ("METHOD_NOT_SUPPORTED" in e) {
                            toast.error("Метод не поддерживается");
                        }
                    });
            else {
                toast.error("Не получилось совершить депозит");
            }

            closeDeposit();
        };

        const handleChangeDeposit = (newValue: string) => {
            setDeposit(Number(newValue));
        };

        return (
            <div className="popup" id="depositPopup">
                <div className="popup-content inter">
                    <h2>Депозит</h2>
                    <label>Сумма депозита(TON):</label>
                    <NumberInput
                        className="inter"
                        placeholder="TON"
                        onChange={handleChangeDeposit}
                    />
                    <div className="popup-buttons">
                        <button className="btn-create inter" onClick={deposit}>
                            Депозит
                        </button>
                        <button
                            className="btn-cancel inter"
                            onClick={closeDeposit}
                        >
                            Отмена
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    const showHistoryPopup = (): JSX.Element => {
        const closeHistory = (): void => {
            const popup = document.getElementById("historyPopup");
            popup?.classList.remove("show");
            setTimeout(() => {
                setHistoryPopup(false);
            }, 100);
        };

        return (
            <div className="popup" id="historyPopup">
                <div className="popup-content inter">
                    <h2>История транзакций</h2>
                    <div className="history-content">
                        <div className="cell">
                            <p>Депозит: 50 TON</p>
                            <p>2023-07-22</p>
                        </div>
                        <div className="cell">
                            <p>Депозит: 540 TON</p>
                            <p>2023-07-22</p>
                        </div>
                        <div className="cell">
                            <p>Депозит: 20 TON</p>
                            <p>2023-07-22</p>
                        </div>
                        {transactions?.map((transaction) => (
                            <div className="cell">
                                <p>
                                    {transaction.transaction_type}:{" "}
                                    {transaction.amount} TON
                                </p>
                                <p>
                                    {new Date(transaction.created_at)
                                        .toISOString()
                                        .replace(/T/, " ")
                                        .replace(/\..+/, "")}
                                </p>
                            </div>
                        ))}
                    </div>
                    <div className="popup-buttons">
                        <button
                            className="btn-cancel inter"
                            onClick={closeHistory}
                        >
                            Закрыть
                        </button>
                    </div>
                </div>
            </div>
        );
    };

    const setShowDepositPopup = (): void => {
        setDepositPopup(true);
        setTimeout(() => {
            const popup = document.getElementById("depositPopup");
            if (popup) popup.classList.add("show");
        }, 10);
    };

    const setShowHistoryPopup = (): void => {
        setHistoryPopup(true);
        setTimeout(() => {
            const popup = document.getElementById("historyPopup");
            if (popup) popup.classList.add("show");
        }, 10);
    };

    return (
        <>
            <div className="page-title">
                <div className="page-title-cell inter">
                    <b className="page-title-cell-title"> Монет:</b>{" "}
                    {formatLargeNumber(moneyBalance)} {moneyEnding}
                </div>
                {tonWallet ? (
                    <div className="page-title-cell inter">
                        <b className="page-title-cell-title"> TON Кошёлёк:</b>{" "}
                        {formatLargeNumber(tonBalance)} TON{" "}
                    </div>
                ) : (
                    <></>
                )}
            </div>
            <div className="page-other">
                <button
                    className="cell btn-def inter"
                    onClick={() => {
                        setShowDepositPopup();
                    }}
                >
                    Депозит средств
                </button>
                <button
                    className="cell btn-def inter"
                    onClick={() => {
                        setShowHistoryPopup();
                    }}
                >
                    История выводов и депозитов
                </button>
                {tonWallet ? (
                    <button
                        className="cell btn-money inter"
                        onClick={async () => {
                            const { data } = await axios.post(
                                "/api/wallet/disconnect",
                                {
                                    player_id: initData?.user?.id,
                                    initData: initDataRaw,
                                }
                            );

                            if (data.ok) {
                                await tonConnectUI.disconnect();
                                toast.success("Кошелёк успешно отвязан");
                            } else {
                                toast.error("Не получилось отвязать кошелёк");
                            }
                        }}
                    >
                        Отвязать TON Кошёлёк
                    </button>
                ) : (
                    <button
                        className="cell btn-def inter"
                        onClick={() => tonConnectUI.openModal()}
                    >
                        Привязать TON Кошёлёк
                    </button>
                )}
            </div>
            {depositPopup && showDepositPopup()}
            {historyPopup && showHistoryPopup()}
            <NavBar stricted={false} />
        </>
    );
};

export default Balance;
