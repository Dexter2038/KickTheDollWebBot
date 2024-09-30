import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import getLaunchParams from "../../RetrieveLaunchParams";
import NavBar from "../../NavBar";
import NumberInput from "../../NumberInput";

interface DiceRoom {
  name: string;
  reward: number;
  room_id: string;
}


const DicePage = (): JSX.Element => {
  const [rooms, setRooms] = useState<Array<DiceRoom>>([]);
  const [createPopup, setCreatePopup] = useState<boolean>(false);
  const { initDataRaw, initData } = getLaunchParams();
  const [name, setName] = useState<string>("");
  const [reward, setReward] = useState<number>(0);
  const navigate = useNavigate();
  useEffect(() => {
    const fetchRooms = async () => {
      const response = await fetch("/api/dice/rooms", {
        method: "GET",
      });
      const data = await response.json();
      if (response.ok) {
        setRooms(data.rooms);
      }
    };
    fetchRooms();
    return () => {
    }
  }, [initDataRaw, initData?.user?.id]);

  const createDice = (): void => {
    if (!name || !reward) {
      toast.error("Необходимо заполнить все поля");
      return;
    }
    const fetchCreate = async () => {
      const response = await fetch("/api/dice/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          initData: initDataRaw,
          player_id: initData?.user?.id,
          name,
          reward,
        }),
      });
      if (!response.ok) {
        const data = await response.json();
        toast.error(data.msg);
        return;
      }

      const data: {
        msg: string;
        ok: boolean;
        status: number;
        room_id: string;
        name: string;
        reward: number;
      } = await response.json();

      navigate(`/dice_game?room_id=${data.room_id}&reward=${data.reward}`);
    };
    fetchCreate();
  };

  const botStartDice = (): void => {
    navigate("/dice_bot");
  };

  const setShowCreatePopup = (): void => {
    setCreatePopup(true);
    setTimeout(() => {
      const popup = document.getElementById("createPopup");
      if (popup) popup.classList.add("show");
    }, 10);
  };

  const closeCreatePopup = (): void => {
    setCreatePopup(false);
    setTimeout(() => {
      const popup = document.getElementById("createPopup");
      if (popup) popup.classList.remove("show");
    }, 100);
  };

  const createGame = (): void => {
    closeCreatePopup();
    createDice();
  };

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>): void => {
    setName(e.target.value);
  }

  const handleRewardChange = (num: string): void => {
    setReward(Number(num));
  }

  const showCreatePopup = (): JSX.Element => {
    return (
      <div id="createPopup" className="popup">
        <div className="popup-content">
          <h2>Создать игру</h2>
          <label>Название</label>
          <input type="text" style={{ textAlign: "center" }} onChange={handleNameChange} maxLength={20} />
          <label>Награда</label>
          <NumberInput onChange={handleRewardChange} />
          <div className="popup-buttons">
            <button type="submit" className="btn-create" onClick={createGame}>
              Создать
            </button>
            <button
              type="button"
              className="btn-cancel"
              onClick={closeCreatePopup}
            >
              Отменить
            </button>
          </div>
        </div>
      </div>
    );
  };



  const joinDice = async (room_id: string) => {
    const response = await fetch("/api/dice/join", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ initData: initDataRaw, room_id: room_id, player_id: initData?.user?.id }),
    });
    if (!response.ok) {
      const data = await response.json();
      toast.error(data.msg);
      //return;
    }

    const data: {
      msg: string;
      ok: boolean;
      status: number;
      room_id: string;
      name: string;
      reward: number;
    } = await response.json();

    //redirect to blackjack?room_id=room_id&reward=reward
    navigate(`/dice_game?room_id=${data.room_id}&reward=${data.reward}`);
  };

  return (
    <>
      <div className="page-title"></div>
      <div className="page-other-dice">
        <div className="dice-create">
          <button onClick={setShowCreatePopup} className="btn-dice-create">
            Создать игру
          </button>
        </div>
        <div className="dice-start-bot">
          <button onClick={() => botStartDice()} className="btn-dice-create">
            Играть с ботом
          </button>
        </div>
        <div className="dice-table">
          {rooms.map((room, index: number) => (
            <button
              className="dice-join"
              key={index}
              onClick={() => joinDice(room.room_id)}
            >
              <div className="dice-join-title">{room.name}</div>
              <div className="dice-join-reward">{room.reward} {
                room.reward % 10 === 1 && room.reward % 100 !== 11
                  ? "монета"
                  : 2 <= room.reward % 10 &&
                    room.reward % 10 <= 4 &&
                    !(12 <= room.reward % 100 && room.reward % 100 <= 14)
                    ? "монеты"
                    : "монет"}</div>
            </button>
          ))}
        </div>
      </div>
      {createPopup && showCreatePopup()}
      <NavBar stricted={false} />
    </>
  );
}

export default DicePage;