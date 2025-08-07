import axios from "axios";
interface LotteryData {
    currentValue: number;
    endTime: string;
}

export interface Winner {
    username: string;
    bet: number;
    multiplier: number;
}

interface WinnersData {
    winners: Winner[];
}

/**
 * Fetches the current lottery data and updates the state
 * with the current lottery object and its end time.
 *
 * @return {Promise<LotteryData>} A promise that resolves when the data is fetched and updated.
 */
const fetchLottery = async (
    initDataRaw: string | undefined
): Promise<LotteryData> => {
    const { data } = await axios.post("/api/lottery", {
        initData: initDataRaw,
    });
    if (data.ok) {
        return { currentValue: data.lottery, endTime: data.time };
    } else {
        return { currentValue: -1, endTime: "" };
    }
};

const fetchTopWinners = async (
    initDataRaw: string | undefined
): Promise<WinnersData> => {
    const { data } = await axios.post("/api/lottery/topwinners", {
        initData: initDataRaw,
    });
    if (data.ok) {
        return { winners: data.winners };
    } else {
        return { winners: [] };
    }
};

export { fetchLottery, fetchTopWinners };
