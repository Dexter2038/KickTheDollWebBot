import getLaunchParams from "../RetrieveLaunchParams";

const PlatformSurenessProvider = ({
    children,
}: {
    children: React.ReactNode;
}) => {
    try {
        const { platform } = getLaunchParams();
        if (
            platform === "android" ||
            platform === "ios" ||
            platform === "android x"
        ) {
            return <>{children}</>;
        } else {
            return (
                <div
                    style={{
                        backgroundColor: "black",
                        width: "100vw",
                        height: "100vh",
                    }}
                >
                    <div
                        style={{
                            display: "flex",
                            justifyContent: "center",
                            alignItems: "center",
                            height: "100%",
                            flexDirection: "column",
                        }}
                    >
                        <img
                            src="/phone.svg"
                            style={{
                                backgroundColor: "white",
                                width: "20%",
                                padding: 0,
                                margin: 0,
                                borderRadius: "20%",
                                marginBottom: "10%",
                            }}
                        />
                        <h1 style={{ color: "white" }} className="inter">
                            Играйте на телефоне
                        </h1>
                    </div>
                </div>
            );
        }
    } catch (e) {
        return <>{children}</>;
        //TODO: Убрать
        return (
            <div
                style={{
                    backgroundColor: "black",
                    width: "100vw",
                    height: "100vh",
                }}
            >
                <div
                    style={{
                        display: "flex",
                        justifyContent: "center",
                        alignItems: "center",
                        height: "100%",
                        flexDirection: "column",
                    }}
                >
                    <img
                        src="/phone.svg"
                        style={{
                            backgroundColor: "white",
                            width: "20%",
                            padding: 0,
                            margin: 0,
                            borderRadius: "20%",
                            marginBottom: "10%",
                        }}
                    />
                    <h1 style={{ color: "white" }} className="inter">
                        Играйте на телефоне
                    </h1>
                </div>
            </div>
        );
    }
};

export default PlatformSurenessProvider;
