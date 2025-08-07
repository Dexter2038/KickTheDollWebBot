import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter as Router } from "react-router-dom";
import App from "./App";
import { TonConnectUIProvider } from "@tonconnect/ui-react";
import PlatformSurenessProvider from "./components/PlatformSurenessProvider";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <Router>
        <PlatformSurenessProvider>
            <TonConnectUIProvider manifestUrl="https://ton-connect.github.io/demo-dapp-with-react-ui/tonconnect-manifest.json">
                <App />
            </TonConnectUIProvider>
        </PlatformSurenessProvider>
    </Router>
);
