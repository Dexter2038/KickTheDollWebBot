import { useState } from "react";
import { useNavigate } from "react-router-dom";

interface NavBarProps {
    stricted: boolean;
    fromGame?: boolean;
}

const NavBar = ({ stricted, fromGame = false }: NavBarProps) => {
    const [navigateAwayUrl, setNavigateAwayUrl] = useState<string>("");
    const [showClass, setShowClass] = useState<boolean>(false);
    const navigate = useNavigate();

    const defaultNavigate = (path: string) => {
        navigate(path);
    };

    if (stricted) {
        const showLeavePopup = () => {
            setTimeout(() => {
                setShowClass(true);
            }, 50);
        };

        let sureLeave;

        if (fromGame) {
            sureLeave = () => {
                window.location.replace(navigateAwayUrl);
                closeLeavePopup();
            };
        } else {
            sureLeave = () => {
                navigate(navigateAwayUrl);
                closeLeavePopup();
            };
        }

        const closeLeavePopup = () => {
            setShowClass(false);
            setTimeout(() => setNavigateAwayUrl(""), 500);
        };

        const strictedNavigate = (path: string) => {
            setNavigateAwayUrl(path);
            showLeavePopup();
        };
        return (
            <>
                <div className="nav">
                    <button
                        type="button"
                        id="Ref"
                        onClick={() => strictedNavigate("/referal")}
                        className="btn btn-nav inter"
                    >
                        Реферал
                    </button>
                    <button
                        type="button"
                        id="Bal"
                        onClick={() => strictedNavigate("/balance")}
                        className="btn btn-nav inter"
                    >
                        Баланс
                    </button>
                    <button
                        type="button"
                        id="Game"
                        onClick={() => strictedNavigate("/game")}
                        className="btn btn-nav inter"
                    >
                        Игра
                    </button>
                    <button
                        type="button"
                        id="Games"
                        onClick={() => strictedNavigate("/games")}
                        className="btn btn-nav inter"
                    >
                        Мини-игры
                    </button>
                    <button
                        type="button"
                        id="Lottery"
                        onClick={() => strictedNavigate("/lottery")}
                        className="btn btn-nav inter"
                    >
                        Лотерея
                    </button>
                </div>
                {navigateAwayUrl && (
                    <div
                        id="leave-popup"
                        className={`popup ${showClass ? "show" : ""}`}
                    >
                        <div className="popup-content inter">
                            <h2>Подтвердите выход</h2>
                            <p>Вы уверены, что хотите уйти?</p>
                            <div className="popup-buttons">
                                <button
                                    className="btn-cancel inter"
                                    onClick={sureLeave}
                                >
                                    Да
                                </button>
                                <button
                                    className="btn-create inter"
                                    onClick={closeLeavePopup}
                                >
                                    Нет
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </>
        );
    } else {
        return (
            <div className="nav inter">
                <button
                    type="button"
                    id="Ref"
                    onClick={() => defaultNavigate("/referal")}
                    className="btn btn-nav inter"
                >
                    Реферал
                </button>
                <button
                    type="button"
                    id="Bal"
                    onClick={() => defaultNavigate("/balance")}
                    className="btn btn-nav inter"
                >
                    Баланс
                </button>
                <button
                    type="button"
                    id="Game"
                    onClick={() => defaultNavigate("/game")}
                    className="btn btn-nav inter"
                >
                    Игра
                </button>
                <button
                    type="button"
                    id="Games"
                    onClick={() => defaultNavigate("/games")}
                    className="btn btn-nav inter"
                >
                    Мини-игры
                </button>
                <button
                    type="button"
                    id="Lottery"
                    onClick={() => defaultNavigate("/lottery")}
                    className="btn btn-nav inter"
                >
                    Лотерея
                </button>
            </div>
        );
    }
};

export default NavBar;
