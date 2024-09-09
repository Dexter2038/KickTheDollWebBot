import { useNavigate } from "react-router-dom"

import DiceSVG from "../../assets/dice.svg";
import BlackjackSVG from "../../assets/blackjack.svg";
import CrashSVG from "../../assets/crash.svg";
import MinesSVG from "../../assets/minesweeper.svg";
import GuessSVG from "../../assets/guess.svg";
import RouletteSVG from "../../assets/roulette.svg";
import NavBar from "../NavBar";

import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';


const GamesPage = () => {
    const navigate = useNavigate();

    const ooooo = () => {
        toast("УРА");
    }


    return <>
        <div className="page-title">
            <div className="page-title-cell">
                <b className="page-title-cell-title">Меню игр</b>
            </div>
        </div>
        <div className="page-other">
            <div className="page-other-games-cell">
                <div className="page-other-games-game-cell">
                    <img src={DiceSVG} className="img-game-enter" />
                    <button type="button" onClick={() => { ooooo() }} className="btn-game-enter">
                        Dice
                    </button>
                </div>
                <div className="page-other-games-game-cell">
                    <img src={BlackjackSVG} className="img-game-enter" />
                    <button type="button" onClick={() => navigate("/blackjack")} className="btn-game-enter">
                        Blackjack
                    </button>
                </div>
                <div className="page-other-games-game-cell">
                    <img src={MinesSVG} className="img-game-enter" />
                    <button type="button" onClick={() => navigate("/mines")} className="btn-game-enter">
                        Mines
                    </button>
                </div>
                <div className="page-other-games-game-cell">
                    <img src={CrashSVG} className="img-game-enter" />
                    <button type="button" onClick={() => navigate("/crash")} className="btn-game-enter">
                        Crash
                    </button>
                </div>
                <div className="page-other-games-game-cell">
                    <img src={GuessSVG} className="img-game-enter" />
                    <button type="button" onClick={() => navigate("/guess")} className="btn-game-enter">
                        Guess
                    </button>
                </div>
                <div className="page-other-games-game-cell">
                    <img src={RouletteSVG} className="img-game-enter" />
                    <button type="button" onClick={() => navigate("/roulette")} className="btn-game-enter">
                        Roulette
                    </button>
                </div>
            </div>
        </div>
        <NavBar stricted={true} />
    </>
}

export default GamesPage;