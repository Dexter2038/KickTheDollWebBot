import { useNavigate } from "react-router-dom";

const Waiting: React.FC = (): JSX.Element => {
    const navigate = useNavigate();
    navigate("/referal");
    return (
        <div
            style={{
                height: "100vh",
                width: "100vw",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                flexDirection: "column",
                backgroundColor: "rgba(0, 0, 0, 0.5)",
                borderRadius: "10px",
                padding: "20px",
                color: "white",
            }}
        >
            <img src="/loading.svg" width={"20%"}></img>
            <p className="inter"> Загрузка...</p>
        </div>
    );
};

export default Waiting;
