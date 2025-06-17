from random import randint

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

from app.core.blackjack import generate_room_id
from app.domain.games import CreateRoomRequest, RoomRequest

dice_rooms = dict()


router = APIRouter(prefix="/dice", tags=["dice"])


@router.get("/rooms", response_class=JSONResponse)
async def get_dice_rooms() -> JSONResponse:
    available_rooms = [
        {"room_id": room_id, "name": details["name"], "reward": details["reward"]}
        for room_id, details in dice_rooms.items()
        if not details["going"]
    ]
    return JSONResponse({"rooms": available_rooms})


@router.post("/create", response_class=JSONResponse)
async def create_dice_room(request: Request, data: CreateRoomRequest) -> JSONResponse:
    new_room_id = generate_room_id()
    name = data.name
    reward = data.reward
    dice_rooms[new_room_id] = {
        "name": name,
        "reward": reward,
        "going": False,
        "active_player": randint(0, 1),
        "players": [request.state.user_id],
        "hands": {
            0: 0,
        },
        "count": {0: 0},
        "results": {0: 0},
    }
    logger.info(
        f"Пользователь {request.state.user_id} создал комнату кубиков с наградой {reward}$"
    )
    return JSONResponse(
        {
            "msg": "Комната успешно создана",
            "room_id": new_room_id,
        }
    )


@router.post("/join", response_class=JSONResponse)
async def join_dice_room(request: Request, data: RoomRequest) -> JSONResponse:
    current_room = dice_rooms[data.room_id]
    if len(current_room["players"]) > 1:
        logger.info(
            f"Пользователь {request.state.user_id} попытался присоединиться к заполненной комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Комната заполнена.")
    current_room["going"] = True
    current_room["players"].append(request.state.user_id)
    current_room["hands"][1] = 0
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


@router.post("/roll", response_class=JSONResponse)
async def roll_dice(request: Request, data: RoomRequest) -> JSONResponse:
    current_room = dice_rooms[data.room_id]
    if current_room["active_player"] != 0:
        logger.info(
            f"Пользователь {request.state.user_id} попытался бросить кубики, но не его ход в комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Не ваш ход.")
    player_id = current_room["players"].index(request.state.user_id)
    current_room["count"][player_id] += 1
    dice_value = randint(1, 6)
    current_room["hands"][player_id] = dice_value
    current_room["active_player"] = int(not player_id)
    if current_room["count"][0] == current_room["count"][1]:
        first = current_room["hands"][0]
        second = current_room["hands"][1]
        if first > second:
            current_room["results"][0] += 1
        elif first < second:
            current_room["results"][1] += 1
    logger.info(
        f"Пользователь {request.state.user_id} бросил кубики в комнате {request.state.user_id}"
    )
    return JSONResponse({"msg": "Вы бросили кубики!", "dice": dice_value})


@router.get("/reward", response_class=JSONResponse)
async def get_dice_reward(data: RoomRequest) -> JSONResponse:
    if data.room_id not in dice_rooms:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Комната не найдена")
    current_room = dice_rooms[data.room_id]
    return JSONResponse(
        {
            "msg": "Награда забрана.",
            "reward": current_room["reward"],
        }
    )


@router.get("/updates", response_class=JSONResponse)
async def get_dice_updates(request: Request, data: RoomRequest) -> JSONResponse:
    if data.room_id not in dice_rooms:
        logger.info(
            f"Пользователь {request.state.user_id} запросил обновления в несуществующей комнате {data.room_id}"
        )
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Комната не найдена")
    current_room = dice_rooms[data.room_id]
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
