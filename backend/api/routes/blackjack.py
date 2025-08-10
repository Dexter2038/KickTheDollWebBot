from random import choice, randint

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from backend.core.blackjack import calculate_hand_value, generate_room_id
from backend.domain.games import CreateRoomRequest, RoomRequest

blackjack_rooms = dict()

cards_52: list[str] = [
    "2_h",
    "2_d",
    "2_c",
    "2_s",
    "3_h",
    "3_d",
    "3_c",
    "3_s",
    "4_h",
    "4_d",
    "4_c",
    "4_s",
    "5_h",
    "5_d",
    "5_c",
    "5_s",
    "6_h",
    "6_d",
    "6_c",
    "6_s",
    "7_h",
    "7_d",
    "7_c",
    "7_s",
    "8_h",
    "8_d",
    "8_c",
    "8_s",
    "9_h",
    "9_d",
    "9_c",
    "9_s",
    "j_h",
    "j_d",
    "j_c",
    "j_s",
    "q_h",
    "q_d",
    "q_c",
    "q_s",
    "k_h",
    "k_d",
    "k_c",
    "k_s",
]


router = APIRouter(prefix="/blackjack")


@router.post("/create", response_class=JSONResponse)
async def create_blackjack_room(
    request: Request, data: CreateRoomRequest
) -> JSONResponse:
    name = data.name
    reward = data.reward
    new_room_id = generate_room_id()
    blackjack_rooms[new_room_id] = {
        "name": name,
        "reward": reward,
        "going": False,
        "active_player": randint(0, 1),
        "players": [request.state.user_id],
        "hands": {
            0: [choice(cards_52), choice(cards_52)],
        },
        "count": {0: 0},
        "results": {0: 0},
    }
    logger.info(
        f"Пользователь {request.state.user_id} создал комнату блэкджека с наградой {reward}$"
    )
    return JSONResponse(
        {
            "msg": "Комната успешно создана!",
            "room_id": new_room_id,
        },
        status.HTTP_201_CREATED,
    )


@router.post("/join", response_class=JSONResponse)
async def join_blackjack_room(request: Request, data: RoomRequest) -> JSONResponse:
    current_room = blackjack_rooms[data.room_id]
    if len(current_room["players"]) > 1:
        logger.info(
            f"Пользователь {request.state.user_id} попытался присоединиться к заполненной комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Комната заполнена.")
    current_room["going"] = True
    current_room["players"].append(request.state.user_id)
    current_room["hands"][1] = [choice(cards_52), choice(cards_52)]
    current_room["count"][1] = 0
    current_room["results"][1] = 0
    logger.info(
        f"Пользователь {request.state.user_id} присоединился к комнате {data.room_id}"
    )
    return JSONResponse(
        {
            "msg": "Вы успешно присоединились к комнате!",
            "room_id": data.room_id,
            "name": current_room["name"],
            "reward": current_room["reward"],
        }
    )


@router.post("/pass", response_class=JSONResponse)
async def pass_card(request: Request, data: RoomRequest) -> JSONResponse:
    if data.room_id not in blackjack_rooms:
        logger.info(
            f"Пользователь {request.state.user_id} попытался оставить карту в несуществующей комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Комната не найдена.")
    current_room = blackjack_rooms[data.room_id]
    player_idx = current_room["players"].index(request.state.user_id)
    if current_room["active_player"] != player_idx:
        logger.info(
            f"Пользователь {request.state.user_id} пытался оставить карту, но не его ход в комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Не ваш ход.")
    current_room["active_player"] = int(not player_idx)  # Reverse active player
    current_room["count"][player_idx] += 1
    logger.info(
        f"Пользователь {request.state.user_id} оставил карту в комнате {data.room_id}"
    )
    return JSONResponse({"msg": "Вы оставили карты"})


@router.post("/take", response_class=JSONResponse)
async def take_card(request: Request, data: RoomRequest) -> JSONResponse:
    if data.room_id not in blackjack_rooms:
        logger.info(
            f"Пользователь {request.state.user_id} попытался взять карту в несуществующей комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Комната не найдена.")
    current_room = blackjack_rooms[data.room_id]
    player_idx = current_room["players"].index(request.state.user_id)
    if current_room["active_player"] != player_idx:
        logger.info(
            f"Пользователь {request.state.user_id} пытался взять карту, но не его ход в комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Не ваш ход.")
    current_room["hands"][player_idx].append(choice(cards_52))
    player_hand = current_room["hands"][player_idx]
    if calculate_hand_value(player_hand) > 21:
        opponent_idx = int(not player_idx)
        current_room[player_idx] += 1
        if current_room["count"][player_idx] > current_room["count"][opponent_idx]:
            current_room["count"][opponent_idx] += 1
            opponent = True
        else:
            opponent = False
        logger.info(
            f"У пользователя {request.state.user_id} перебор в комнате {data.room_id}"
        )
        return JSONResponse(
            {
                "msg": "У вас перебор.",
                "hand": player_hand,
                "opponent": opponent,
            },
            status.HTTP_202_ACCEPTED,
        )
    logger.info(
        f"Пользователь {request.state.user_id} взял карту в комнате {data.room_id}"
    )
    return JSONResponse({"msg": "Вы взяли карту.", "hand": player_hand})


@router.get("/updates", response_class=JSONResponse)
async def get_blackjack_updates(request: Request, data: RoomRequest) -> JSONResponse:
    if data.room_id not in blackjack_rooms:
        logger.info(
            f"Пользователь {request.state.user_id} запросил обновления в несуществующей комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Комната не найдена.")
    current_room = blackjack_rooms[data.room_id]
    if any(item == 3 for item in current_room["results"].values()):
        self_idx = current_room["players"].index(request.state.user_id)
        self = current_room["results"][self_idx]
        opponent = current_room["results"][int(not self_idx)]
        if self > opponent:
            logger.info(
                f"Пользователь {request.state.user_id} выиграл в комнате {data.room_id}"
            )
            return JSONResponse({"msg": "Вы выиграли!"})
        elif self < opponent:
            logger.info(
                f"Пользователь {request.state.user_id} проиграл в комнате {data.room_id}"
            )
            return JSONResponse({"msg": "Вы проиграли!"})
        else:
            logger.info(f"Ничья в комнате {data.room_id}")
            return JSONResponse({"msg": "Ничья!"})
    if len(current_room["players"]) < 2:
        logger.info(
            f"Противник пользователя {request.state.user_id} вышел из комнаты {data.room_id}"
        )
        return JSONResponse(
            {
                "msg": "Противник вышел из игры! Вы выиграли!",
            }
        )
    self_idx = current_room["players"].index(request.state.user_id)
    opponent_idx = int(not self_idx)
    logger.info(
        f"Пользователь {request.state.user_id} успешно получил обновления в комнате {data.room_id}"
    )
    return JSONResponse(
        {
            "msg": "Обновления успешно получены.",
            "active_player": current_room["active_player"] == self_idx,
            "self": {
                "hands": current_room["hands"][self_idx],
                "count": current_room["count"][self_idx],
                "results": current_room["results"][self_idx],
            },
            "opponent": {
                "hands": current_room["hands"][opponent_idx],
                "count": current_room["count"][opponent_idx],
                "results": current_room["results"][opponent_idx],
            },
        }
    )


@router.get("/rooms", response_class=JSONResponse)
async def get_blackjack_rooms() -> JSONResponse:
    available_rooms = [
        {"room_id": room_id, "name": details["name"], "reward": details["reward"]}
        for room_id, details in blackjack_rooms.items()
        if not details["going"]
    ]
    return JSONResponse({"rooms": available_rooms})


@router.post("/leave", response_class=JSONResponse)
async def leave_blackjack_room(request: Request, data: RoomRequest) -> JSONResponse:
    if data.room_id not in blackjack_rooms:
        logger.info(
            f"Пользователь {request.state.user_id} пытался выйти из несуществующей комнаты {data.room_id}"
        )
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Комната не найдена.")
    current_room = blackjack_rooms[data.room_id]
    if request.state.user_id not in current_room["players"]:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Вы не в игре.")
    current_room["players"].remove(request.state.user_id)
    logger.info(f"Пользователь {request.state.user_id} вышел из комнаты {data.room_id}")
    return JSONResponse({"msg": "Вы вышли из игры!"})


@router.get("/reward", response_class=JSONResponse)
async def get_blackjack_reward(room_id: str) -> JSONResponse:
    if room_id not in blackjack_rooms:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Комната не найдена.")
    current_room = blackjack_rooms[room_id]
    return JSONResponse(
        {
            "msg": "Награда забрана.",
            "reward": current_room["reward"],
        }
    )
