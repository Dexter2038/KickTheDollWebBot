import {
    Account,
    ConnectAdditionalRequest,
    TonProofItemReplySuccess,
} from "@tonconnect/ui";
import { useTonConnectUI } from "@tonconnect/ui-react";

class BackendAuth {
    private readonly payloadTTLMS = 1000 * 60 * 20;

    private interval: ReturnType<typeof setInterval> | undefined;

    private localStorageAccessToken = "ton-connect-access-token-dapp";

    public onAccessTokenChange:
        | ((accessToken: string | null) => void)
        | undefined;

    private _accessToken: string | null = null;
    private set accessToken(token: string | null) {
        this._accessToken = token;
        this.onAccessTokenChange?.(token);
        if (token) {
            localStorage.setItem(this.localStorageAccessToken, token);
        } else {
            localStorage.removeItem(this.localStorageAccessToken);
        }
    }

    public get accessToken(): string | null {
        return this._accessToken;
    }

    tonConnectUI = useTonConnectUI()[0];

    constructor() {
        this.tonConnectUI.connectionRestored.then(() => this.init());
    }

    private async init() {
        this.accessToken = localStorage.getItem(this.localStorageAccessToken);
        if (this.accessToken && this.tonConnectUI.wallet) {
            await this.tonConnectUI.disconnect();
        }

        if (!this.tonConnectUI.wallet) {
            this.accessToken = null;
            await this.refreshTonProofPayload();
            setInterval(
                async () => await this.refreshTonProofPayload(),
                this.payloadTTLMS
            );
        }

        this.tonConnectUI.onStatusChange(async (wallet) => {
            clearInterval(this.interval);

            if (!wallet) {
                this.accessToken = null;
                await this.refreshTonProofPayload();
                setInterval(
                    async () => await this.refreshTonProofPayload(),
                    this.payloadTTLMS
                );
            } else {
                if (
                    wallet.connectItems?.tonProof &&
                    !("error" in wallet.connectItems.tonProof)
                ) {
                    this.checkProof(
                        wallet.connectItems.tonProof.proof,
                        wallet.account
                    ).then((token) => {});
                }
            }
        });
    }

    private async refreshTonProofPayload() {
        this.tonConnectUI.setConnectRequestParameters({ state: "loading" });

        const value = await this.generatePayload();

        if (!value) {
            this.tonConnectUI.setConnectRequestParameters(null);
        } else {
            this.tonConnectUI.setConnectRequestParameters({
                state: "ready",
                value,
            });
        }
    }

    async generatePayload(): Promise<ConnectAdditionalRequest | undefined> {
        try {
            const response = await (
                await fetch(`/ton-proof/generatePayload`, {
                    method: "POST",
                })
            ).json();
            return { tonProof: response.payload };
        } catch (e) {
            console.error(e);
            return;
        }
    }

    async checkProof(
        proof: TonProofItemReplySuccess["proof"],
        account: Account
    ): Promise<string | undefined> {
        try {
            const requestBody = {
                address: account.address,
                network: account.chain,
                proof: {
                    ...proof,
                    state_init: account.walletStateInit,
                },
            };

            const response = await (
                await fetch(`/ton-proof/checkProof`, {
                    method: "POST",
                    body: JSON.stringify(requestBody),
                })
            ).json();

            return response?.token;
        } catch (e) {
            console.log(e);
        }
    }

    async getAccountInfo(accessToken: string, account: Account) {
        return (
            await fetch(`/dapp/getAccountInfo?network=${account.chain}`, {
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                    "Content-Type": "application/json",
                },
            })
        ).json();
    }
}

export const backendAuth = new BackendAuth();
