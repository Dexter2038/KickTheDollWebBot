import { useTonAddress, useTonConnectUI } from "@tonconnect/ui-react";
import { toast } from "react-toastify";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { retrieveLaunchParams } from "@telegram-apps/sdk";

const RegisterPage: React.FC = (): JSX.Element => {
    const [registered, setRegistered] = useState<boolean>(false);
    const tonAddress = useTonAddress(false);
    const [tonConnectUI] = useTonConnectUI();
    const { initDataRaw } = retrieveLaunchParams();
    const navigate = useNavigate();

    tonConnectUI.onStatusChange((wallet) => {
        if (wallet) {
            setRegistered(true);
        }
    });

    useEffect(() => {
        const fetchRegister = () => {
            axios
                .post("/api/player/login", {
                    wallet_address: tonAddress,
                    init_data: initDataRaw,
                })
                .then(({ data }) => {
                    if (data.ok) {
                        toast.success("Вы успешно зарегистрированы");
                        navigate("/referal");
                    } else {
                        toast.error(data.msg);
                        setRegistered(false);
                        tonConnectUI.disconnect();
                    }
                });
        };
        if (registered) fetchRegister();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [registered]);

    if (tonAddress) {
        if (!registered) tonConnectUI.disconnect();
    }

    return (
        <>
            <div className="page-title">
                <div className="page-title-cell inter">
                    <b className="page-title-cell-title">Регистрация</b>
                </div>
                <div
                    className="page-title-cell inter"
                    style={{ textAlign: "center" }}
                >
                    <b className="page-title-cell-title">Условие: </b>на вашем
                    кошельке должно быть более 5$
                    <br />
                    <b className="page-title-cell-title">
                        или более 30 транзакций
                    </b>
                </div>
            </div>
            <div className="page-other">
                <button
                    className="cell btn-money inter"
                    onClick={() => tonConnectUI.openModal()}
                >
                    Привязать TON Кошёлёк
                </button>
            </div>
        </>
    );
};

export default RegisterPage;
