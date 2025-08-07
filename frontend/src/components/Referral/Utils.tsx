import axios from "axios";
/**
 * Fetches the reward data from the "/api/reward" endpoint using a GET request.
 * The request body includes the "initData" and "player_id" parameters.
 * If the response is successful, the reward value is updated using the "setReward" function.
 *
 * @return {Promise<void>} A promise that resolves when the reward data is fetched and updated.
 */
const fetchReward = async (
    initDataRaw: string | undefined,
    userId: number | undefined
): Promise<number> => {
    const { data } = await axios.post("/api/reward/get", {
        initData: initDataRaw,
        player_id: userId,
    });
    if (data.ok) {
        return data.reward;
    } else {
        return -1;
    }
};

/**
 * Fetches the referal data from the "/api/referal" endpoint using a GET request.
 * The request body includes the "initData" and "player_id" parameters.
 * If the response is successful, the referal value is updated using the "setReferal" function.
 *
 * @return {Promise<void>} A promise that resolves when the referal data is fetched and updated.
 */
const fetchReferral = async (
    initDataRaw: string | undefined,
    userId: number | undefined
): Promise<number> => {
    const { data } = await axios.post("/api/referral/get", {
        initData: initDataRaw,
        player_id: userId,
    });
    if (data.ok) {
        return data.referral_count;
    } else {
        return -1;
    }
};

/**
 * Fetches the link data from the "/api/link" endpoint using a GET request.
 * The request body includes the "initData" and "player_id" parameters.
 * If the response is successful, the link value is updated using the "setLink" function.
 *
 * @return {Promise<void>} A promise that resolves when the link data is fetched and updated.
 */
const fetchLink = async (
    initDataRaw: string | undefined,
    userId: number | undefined
): Promise<string> => {
    const { data } = await axios.post("/api/invite/link", {
        initData: initDataRaw,
        player_id: userId,
    });
    if (data.ok) {
        return data.invite_link;
    } else {
        return "";
    }
};

export { fetchReward, fetchReferral, fetchLink };
