const Technical: React.FC = () => {
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
                    src="/unavailable.svg"
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
                    Технические работы
                </h1>
                <p style={{ color: "white" }} className="inter">
                    Извините, но на данный момент выполняются технические работы
                </p>
            </div>
        </div>
    );
};

export default Technical;
