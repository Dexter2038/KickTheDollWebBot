import axios from "axios";
/**
 * Fetches player data from the API and updates the dollar and money balances.
 *
 * @return {Promise<number>}
 */
const fetchData = async (
    initDataRaw: string | undefined,
    userId: number | undefined
): Promise<number> => {
    const { data } = await axios.post("/api/player/get", {
        initData: initDataRaw,
        player_id: userId,
    });
    if (data.ok) {
        return data.player.money_balance;
    } else {
        return -1;
    }
};

interface Transaction {
    id: string;
    transaction_type: string;
    amount: number;
    created_at: string;
    transaction_hash: string;
    confirmed: boolean;
}

/**
 * Fetches the transaction history from the API and updates the transactions state.
 *
 * @return {Promise<Transaction[]>}
 */
const fetchHistory = async (
    initDataRaw: string | undefined,
    userId: number | undefined
): Promise<Transaction[]> => {
    const { data } = await axios.post("/api/transactions/get", {
        initData: initDataRaw,
        player_id: userId,
    });
    if (data.ok) {
        return data.data;
    } else {
        return [];
    }
};

const fetchTonBalance = async (
    initDataRaw: string | undefined,
    userId: number | undefined
): Promise<number> => {
    const { data } = await axios.post("/api/wallet/get_balance", {
        initData: initDataRaw,
        player_id: userId,
    });
    if (data.ok) {
        return data.balance;
    } else {
        return -1;
    }
};

export { fetchData, fetchHistory, fetchTonBalance };
