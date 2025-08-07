import { useEffect, useState } from "react";
import NavBar from "../NavBar";
import { fetchReward, fetchLink, fetchReferral } from "./Utils";
import { toast } from "react-toastify";
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

/**
 * A React component that displays the number of referrals and rewards earned by a user.
 * It also provides functionality to copy the referral link and claim the reward.
 *
 * @return {JSX.Element} The JSX element representing the component.
 */
const Referral = (): JSX.Element => {
    const [reward, setReward] = useState<number>(0);
    const [referral, setReferral] = useState<number>(0);
    const [link, setLink] = useState<string>("");
    useEffect(() => {
        const fetchAll = async () => {
            try {
                const [reward, referral, link] = await Promise.all([
                    fetchReward(),
                    fetchReferral(),
                    fetchLink(),
                ]);

                if (reward === -1) {
                    toast.error(
                        "Не удалось получить данные. Перезагрузите страницу"
                    );
                } else {
                    setReward(reward);
                }

                if (referral === -1) {
                    toast.error(
                        "Не удалось получить данные. Перезагрузите страницу"
                    );
                } else {
                    setReferral(referral);
                }

                if (link === "") {
                    toast.error(
                        "Не удалось получить данные. Перезагрузите страницу"
                    );
                } else {
                    setLink(link);
                }
            } catch (error) {
                console.error(error);
            }
        };
        fetchAll();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);
    const referalEnding: string =
        referral % 10 === 1 && referral % 100 !== 11
            ? "пользователь"
            : 2 <= referral % 10 &&
                referral % 10 <= 4 &&
                !(12 <= referral % 100 && referral % 100 <= 14)
              ? "пользователя"
              : "пользователей";
    const rewardEnding: string =
        reward % 10 === 1 && reward % 100 !== 11
            ? "монета"
            : 2 <= reward % 10 &&
                reward % 10 <= 4 &&
                !(12 <= reward % 100 && reward % 100 <= 14)
              ? "монеты"
              : "монет";
    /**
     * Copies the referral link to the clipboard and displays a notification popup.
     *
     * @return {void} No return value.
     */
    const takeLink = (): void => {
        if (link) {
            toast.success("Ссылка скопирована");
            navigator.clipboard.writeText(link);
        } else {
            toast.error(
                "Не удалось скопировать ссылку. Перезагрузите страницу"
            );
        }
    };

    /**
     * Asynchronously takes a reward by making a POST request to the "/api/take-reward" endpoint.
     * If the response is successful, decrements the reward value by 1 every 10 milliseconds until it reaches 0.
     *
     * @return {Promise<void>} A Promise that resolves when the reward is taken.
     */
    const takeReward = async (): Promise<void> => {
        const fetchTakeReward = async () => {
            const { data } = await axios.post("/api/take-reward");
            if (data.ok) {
                const intervalId = setInterval(() => {
                    setReward((reward) =>
                        reward > 0 ? reward - 1 : (clearInterval(intervalId), 0)
                    );
                }, 10);
            }
        };
        fetchTakeReward();
    };

    return (
        <>
            <div className="page-title">
                <div className="page-title-cell inter">
                    <b className="page-title-cell-title"> Приглашено:</b>{" "}
                    {referral} {referalEnding}
                </div>
                <div className="page-title-cell inter">
                    <b className="page-title-cell-title"> Награда:</b>{" "}
                    {formatLargeNumber(reward)} {rewardEnding}
                </div>
            </div>
            <div className="page-other">
                <button className="cell btn-def inter" onClick={takeLink}>
                    Скопировать ссылку
                </button>
                <button className="cell btn-money inter" onClick={takeReward}>
                    💰Забрать награду💰
                </button>
            </div>
            <NavBar stricted={false} />
        </>
    );
};

export default Referral;
