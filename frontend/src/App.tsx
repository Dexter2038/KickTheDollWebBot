import { useEffect } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import Balance from "./components/Balance";
import Referal from "./components/Referral";
import Game from "./components/Game";
import Lottery from "./components/Lottery";
import Technical from "./components/Technical";
import {
    GamesPage,
    BlackjackPage,
    BlackjackBot,
    BlackjackGame,
    DicePage,
    DiceBot,
    DiceGame,
    GuessGame,
    MinesGame,
    RouletteGame,
    CrashGame,
} from "./components/Games";
import RegisterPage from "./components/Register";
import Waiting from "./components/Waiting";
import { useIsConnectionRestored } from "@tonconnect/ui-react";
import "./App.css";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

function App() {
    const conRestored = useIsConnectionRestored();

    if (!conRestored) {
        return (
            <>
                <Routes>
                    <Route path="/referal" element={<Referal />} />
                    <Route path="/balance" element={<Balance />} />
                    <Route path="/lottery" element={<Lottery />} />
                    <Route path="/game" element={<Game />} />
                    <Route path="/games" element={<GamesPage />} />
                    <Route path="/dice" element={<DicePage />} />
                    <Route path="/dice_game" element={<DiceGame />} />
                    <Route path="/dice_bot" element={<DiceBot />} />
                    <Route path="/blackjack" element={<BlackjackPage />} />
                    <Route path="/blackjack_game" element={<BlackjackGame />} />
                    <Route path="/blackjack_bot" element={<BlackjackBot />} />
                    <Route path="/mines" element={<MinesGame />} />
                    <Route path="/crash" element={<CrashGame />} />
                    <Route path="/roulette" element={<RouletteGame />} />
                    <Route path="/guess" element={<GuessGame />} />
                    <Route path="/reg" element={<RegisterPage />} />
                    <Route path="/technical" element={<Technical />} />
                    <Route path="*" element={<Waiting />} />
                </Routes>
                <ToastContainer />
            </>
        );
    }

    return (
        <>
            <Routes>
                <Route path="/referal" element={<Referal />} />
                <Route path="/balance" element={<Balance />} />
                <Route path="/lottery" element={<Lottery />} />
                <Route path="/game" element={<Game />} />
                <Route path="/games" element={<GamesPage />} />
                <Route path="/dice" element={<DicePage />} />
                <Route path="/dice_game" element={<DiceGame />} />
                <Route path="/dice_bot" element={<DiceBot />} />
                <Route path="/blackjack" element={<BlackjackPage />} />
                <Route path="/blackjack_game" element={<BlackjackGame />} />
                <Route path="/blackjack_bot" element={<BlackjackBot />} />
                <Route path="/mines" element={<MinesGame />} />
                <Route path="/crash" element={<CrashGame />} />
                <Route path="/roulette" element={<RouletteGame />} />
                <Route path="/guess" element={<GuessGame />} />
                <Route path="/reg" element={<RegisterPage />} />
                <Route path="/technical" element={<Technical />} />
                <Route path="*" element={<Waiting />} />
            </Routes>
            <ToastContainer />
        </>
    );
}

export default App;
