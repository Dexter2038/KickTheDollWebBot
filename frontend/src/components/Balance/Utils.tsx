import axios from "axios";
/**
 * Fetches player data from the API and updates the dollar and money balances.
 *
 * @return {Promise<number>}
 */
const fetchData = async (): Promise<number> => {
    const { data } = await axios.post("/api/player/get");
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
const fetchHistory = async (): Promise<Transaction[]> => {
    const { data } = await axios.post("/api/transactions/get");
    if (data.ok) {
        return data.data;
    } else {
        return [];
    }
};

const fetchTonBalance = async (): Promise<number> => {
    const { data } = await axios.post("/api/wallet/get_balance");
    if (data.ok) {
        return data.balance;
    } else {
        return -1;
    }
};

export { fetchData, fetchHistory, fetchTonBalance };
