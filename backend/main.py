from dataclasses import dataclass
import aiohttp
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

from loguru import logger
import sys

try:
    logger.remove()
except:
    print("Logger not found")
logger.add(
    sys.stderr,
    format=
    "<green>{time:YYYY-MM-DD HH:mm:ss.ms}</green> | <cyan>{file.path}:{line}:{function}</cyan> | <level>{message}</level>"
)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

import uvicorn

from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

from random import randint, choice
from typing import Dict, List

from request_models import *
from utils import *
from database import db
import telegram_bot
import asyncio


bot, dp = telegram_bot.get_bot()

app: FastAPI = FastAPI(debug=True)
app.mount('/assets',
          StaticFiles(directory="assets", check_dir=False),
          name="assets")

dice_rooms: dict = dict()
blackjack_rooms: dict = dict()

cards_52: List[str] = [
    '2_h', '2_d', '2_c', '2_s', '3_h', '3_d', '3_c', '3_s', '4_h', '4_d',
    '4_c', '4_s', '5_h', '5_d', '5_c', '5_s', '6_h', '6_d', '6_c', '6_s',
    '7_h', '7_d', '7_c', '7_s', '8_h', '8_d', '8_c', '8_s', '9_h', '9_d',
    '9_c', '9_s', 'j_h', 'j_d', 'j_c', 'j_s', 'q_h', 'q_d', 'q_c', 'q_s',
    'k_h', 'k_d', 'k_c', 'k_s'
]

templates: Jinja2Templates = Jinja2Templates(directory='templates')



@app.post('/api/initdata/check', response_class=JSONResponse)
async def check_init_data(request: DefaultRequest):
    if is_telegram(request.initData):
        logger.info(f"Данные успешно проинициализированы: {request.initData}")
        return {"msg": "Данные инициализации корректны", "ok": True}
    else:
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Данные инициализации некорректны", "ok": False}


@app.post('/api/player/get', response_class=JSONResponse)
async def get_player_by_id(id: str, request: DefaultRequest):
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    player = await db.get_user(id)
    if player:
        logger.info(f"Пользователь {id} был взят из базы данных")
        return {
            "msg": "Игрок успешно найден",
            "ok": True,
            "status": 200,
            "player": {
                "wallet_address": player.wallet_address,
                "dollar_balance": player.dollar_balance,
                "money_balance": player.money_balance,
                "total_transactions": player.total_transactions
            }
        }
    else:
        logger.warning(f"Была попытка поиска пользователя под id: {id}")
        return {"ok": False, "status": 404, "msg": "Игрок не найден"}


@app.post('/api/player/post', response_class=JSONResponse)
async def create_player(request: CreateUserRequest):
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    wallet_address = request.wallet_address
    username = request.username
    telegram_id = request.telegram_id
    if (await db.create_user(telegram_id=telegram_id,
                             username=username,
                             wallet_address=wallet_address)):
        logger.info(
            f"Создан пользователь. ID: {request.telegram_id}. Никнейм: {request.username}. Адрес кошелька: {request.wallet_address}"
        )
        return {"msg": "Игрок успешно создан", "ok": True, "status": 201}
    else:
        logger.error(
            f"Не удалось создать игрока с данными: ID: {request.telegram_id}. Никнейм: {request.username}. Адрес кошелька: {request.wallet_address}"
        )
        return {"ok": False, "status": 400, "msg": "Ошибка создания игрока"}


@app.post('/api/reward/get', response_class=JSONResponse)
async def find_out_reward(request: PlayerRequest):
    """
        Get amount of reward for every of referal
    """
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    reward = await db.get_referral_reward(request.player_id)
    return {
        "msg": "Награда забрана",
        "ok": True,
        "status": 200,
        "reward": reward
    }

@app.post('/api/take-reward', response_class=JSONResponse)
async def take_reward(request: PlayerRequest):
    """
        Get amount of reward for every of referal
    """
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    reward = await db.take_referral_reward(request.player_id)
    return {
        "msg": "Награда забрана",
        "ok": True,
        "status": 200,
        "reward": reward
    }


@app.post('/api/reward/post', response_class=JSONResponse)
async def get_reward(request: PlayerRequest):
    """
        Get amount of reward for every of referal
    """
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    reward = await db.grab_referral_reward(request.player_id)
    logger.info(f"Пользователь {request.player_id} получил награду: {reward}")
    return {
        "msg": "Награда забрана",
        "ok": True,
        "status": 200,
        "reward": reward
    }


@app.post('/api/referral/get', response_class=JSONResponse)
async def get_referral_count(request: PlayerRequest):
    """
        Get count of referrals of certain user
    """
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    referral_count = await db.get_referral_count(request.player_id)
    return {
        "msg": "Количество рефералов получено",
        "ok": True,
        "status": 200,
        "referral_count": referral_count
    }


@app.post('/api/invite/link', response_class=JSONResponse)
async def get_invite_link(request: PlayerRequest):
    """
        Get invitation link for certain user
    """
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    invite_link = await get_invitation_link(request.player_id)
    return {
        "msg": "Инвайт ссылка получена",
        "ok": True,
        "status": 200,
        "invite_link": invite_link
    }


@app.post('/api/transaction', response_class=JSONResponse)
async def create_transaction(request: TransactionRequest):
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    amount = request.amount
    transaction_type = request.transaction_type

    if (await db.create_transaction(request.telegram_id, amount,
                                    transaction_type)):
        logger.info(
            f"Создана транзакция. ID: {request.telegram_id}. Сумма: {amount}. Тип транзакции: {"Вывод" if transaction_type else "Депозит"}"
        )
        return {"msg": "Транзакция успешно создана", "ok": True, "status": 201}
    else:
        logger.error(f"Не удалось создать транзакцию с данными: ID: {request.telegram_id}. Сумма: {amount}. Тип транзакции: {"Вывод" if transaction_type else "Депозит"}")
        return {
            "ok": False,
            "status": 400,
            "msg": "Ошибка создания транзакции"
        }

@app.post('/api/transactions/get')
async def get_transactions(request: PlayerRequest):
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    transactions = await db.get_transactions(request.player_id)
    return {
        "msg": "Транзакции получены",
        "ok": True,
        "status": 200,
        "data": transactions
    }


@app.post('/api/game/finish', response_class=JSONResponse)
async def create_finished_game(request: FinishedGameRequest):
    if not is_telegram(request.initData):
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    game_type = request.game_type
    amount = request.amount
    first_user_id = request.first_user_idw
    second_user_id = request.second_user_id
    if (await db.mark_finished_game(game_type, amount, first_user_id,
                                    second_user_id)):
        logger.info(
            f"Игра {game_type} {f"между {first_user_id} и {second_user_id}" if second_user_id else f"от {first_user_id}"} "
            f"завершена. Сумма: {amount}"
        )
        return {"msg": "Игра успешно завершена", "ok": True, "status": 201}
    else:
        logger.error(f"Не удалось завершить игру с данными: тип игры {game_type}, сумма {amount}, ID первого игрока {first_user_id}, ID второго игрока {second_user_id}")
        return {"ok": False, "status": 400, "msg": "Ошибка завершения игры"}


@app.get('/api/dice/rooms', response_class=JSONResponse)
async def get_dice_rooms(request: Request):
    available_rooms = [{
        "room_id": room_id,
        "name": details["name"],
        "reward": details["reward"]
    } for room_id, details in dice_rooms.items() if not details["going"]]
    return {"ok": True, "status": 200, "rooms": available_rooms}


@app.post('/api/dice/create', response_class=JSONResponse)
async def create_dice_room(request: CreateRoomRequest):
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    new_room_id = generate_room_id()
    name = request.name
    reward = request.reward
    dice_rooms[new_room_id] = {
        "name": name,
        "reward": int(reward),
        "going": False,
        "active_player": randint(0, 1),
        "players": [request.player_id],
        "hands": {0: 0,},
        "count": {0: 0},
        "results": {0: 0},
    }
    logger.info(f"Пользователь {request.player_id} создал комнату кубиков с наградой {reward}$")
    return {
        "ok": True,
        "status": 200,
        "msg": "Комната успешно создана",
        "room_id": new_room_id
    }


@app.post('/api/dice/join', response_class=JSONResponse)
async def join_dice_room(request: JoinRequest):
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    if request.room_id not in dice_rooms:
        logger.info(f"Пользователь {request.player_id} попытался присоединиться к несуществующей комнате {request.room_id}")
        return {"msg": "Комнаты не существует.", "ok": False, "status": 404}
    current_room: dict = dice_rooms[request.room_id]
    if len(current_room["players"]) > 1:
        logger.info(f"Пользователь {request.player_id} попытался присоединиться к заполненной комнате {request.room_id}")
        return {"msg": "Комната заполнена.", "ok": False, "status": 403}
    current_room["going"] = True
    current_room["players"].append(request.player_id)
    current_room["hands"][1] = 0
    current_room["count"][1] = 0
    current_room["results"][1] = 0
    logger.info(f"Пользователь {request.player_id} присоединился к комнате {request.room_id}")
    return {
        "msg": "Вы успешно присоединились к комнате!",
        "ok": True,
        "status": 200,
        "room_id": request.room_id,
        "name": current_room["name"],
        "reward": current_room["reward"]
    }


@app.post('/api/dice/roll', response_class=JSONResponse)
async def roll_dice(request: TurnRequest):
    if not is_telegram(request.initData):
        logger.warning(f"Кто-то попытался бросить кубики с некорректными данными: {request.initData}")
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    if request.room_id not in dice_rooms:
        logger.info(f"Пользователь {request.player_id} попытался бросить кубики в несуществующей комнате {request.room_id}")
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = dice_rooms[request.room_id]
    if current_room["active_player"] != 0:
        logger.info(f"Пользователь {request.player_id} попытался бросить кубики, но не его ход в комнате {request.room_id}")
        return {"msg": "Не ваш ход.", "ok": False, "status": 401}
    player_id = current_room["players"].index(request.player_id)
    current_room["count"][player_id] += 1
    dice_value: int = randint(1, 6)
    current_room["hands"][player_id] = dice_value
    current_room["active_player"] = int(not player_id)
    if current_room["count"][0] == current_room["count"][1]:
        first = current_room["hands"][0]
        second = current_room["hands"][1]
        if first > second:
            current_room["results"][0] += 1
        elif first < second:
            current_room["results"][1] += 1
    logger.info(f"Пользователь {request.player_id} бросил кубики в комнате {request.room_id}")
    return {
        "msg": "Вы бросили кубики!",
        "ok": True,
        "status": 200,
        "dice": dice_value
    }
    
    
@app.get('/api/dice/reward', response_class=JSONResponse)
async def get_dice_reward(room_id: str):
    if room_id not in dice_rooms:
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = dice_rooms[room_id]
    return {
        "msg": "Награда забрана.",
        "ok": True,
        "status": 200,
        "reward": current_room["reward"]
    }

@app.get('/api/dice/updates', response_class=JSONResponse)
async def get_dice_updates(player_id: int, room_id: str):
    if room_id not in blackjack_rooms:
        logger.info(f"Пользователь {player_id} запросил обновления в несуществующей комнате {room_id}")
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = dice_rooms[room_id]
    if any(item == 3 for item in current_room["results"].values()):
        self_idx: int = current_room["players"].index(player_id)
        self: int = current_room["results"][self_idx]
        opponent: int = current_room["results"][int(not self_idx)]
        if self > opponent:
            logger.info(f"Пользователь {player_id} выиграл в комнате {room_id}")
            return {"msg": "Вы выиграли!", "ok": True, "status": 200}
        elif self < opponent:
            logger.info(f"Пользователь {player_id} проиграл в комнате {room_id}")
            return {"msg": "Вы проиграли!", "ok": True, "status": 200}
        else:
            logger.info(f"Ничья в комнате {room_id}")
            return {"msg": "Ничья!", "ok": True, "status": 200}
    if len(current_room["players"]) < 2:
        logger.info(f"Противник пользователя {player_id} вышел из комнаты {room_id}")
        return {
            "msg": "Противник вышел из игры! Вы выиграли!",
            "ok": True,
            "status": 200
        }
    self_idx: int = current_room["players"].index(player_id)
    opponent_idx: int = int(not self_idx)
    data = {
        "active_player": current_room["active_player"] == self_idx,
        "self": {
            "hands": current_room["hands"][self_idx],
            "count": current_room["count"][self_idx],
            "results": current_room["results"][self_idx]
        },
        "opponent": {
            "hands": current_room["hands"][opponent_idx],
            "count": current_room["count"][opponent_idx],
            "results": current_room["results"][opponent_idx]
        }
    }
    logger.info(f"Пользователь {player_id} успешно получил обновления в комнате {room_id}")
    return {
        "msg": "Обновления успешно получены.",
        "ok": True,
        "status": 200,
        "data": data
    }
    


@app.post('/api/blackjack/create', response_class=JSONResponse)
async def create_blackjack_room(request: CreateRoomRequest):
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    name: str = request.name
    reward: int = request.reward
    new_room_id: int = generate_room_id()
    blackjack_rooms[new_room_id] = {
        "name": name,
        "reward": int(reward),
        "going": False,
        "active_player": randint(0, 1),
        "players": [request.player_id],
        "hands": {
            0:[choice(cards_52), choice(cards_52)],
    },
        "count": {0: 0},
        "results": {0: 0},
    }
    logger.info(f"Пользователь {request.player_id} создал комнату блэкджека с наградой {reward}$")
    return {
        "msg": "Комната успешно создана!",
        "ok": True,
        "status": 200,
        "room_id": new_room_id,
    }


@app.post('/api/blackjack/join', response_class=JSONResponse)
async def join_blackjack_room(request: JoinRequest):
    if not is_telegram(request.initData):
        logger.warning(
            f"Кто-то пытался войти с некорректными данными: {request.initData}"
        )
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    if request.room_id not in blackjack_rooms:
        logger.info(f"Пользователь {request.player_id} попытался присоединиться к несуществующей комнате {request.room_id}")
        return {"msg": "Комнаты не существует.", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[request.room_id]
    if len(current_room["players"]) > 1:
        logger.info(f"Пользователь {request.player_id} попытался присоединиться к заполненной комнате {request.room_id}")
        return {"msg": "Комната заполнена.", "ok": False, "status": 403}
    current_room["going"] = True
    current_room["players"].append(request.player_id)
    current_room["hands"][1] = [choice(cards_52), choice(cards_52)]
    current_room["count"][1] = 0
    current_room["results"][1] = 0
    logger.info(f"Пользователь {request.player_id} присоединился к комнате {request.room_id}")
    return {
        "msg": "Вы успешно присоединились к комнате!",
        "ok": True,
        "status": 200,
        "room_id": request.room_id,
        "name": current_room["name"],
        "reward": current_room["reward"]
    }


@app.post('/api/blackjack/pass', response_class=JSONResponse)
async def pass_card(request: TurnRequest):
    if not is_telegram(request.initData):
        logger.warning(f"Кто-то пытался оставить карту с некорректными данными: {request.initData}")
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    if request.room_id not in blackjack_rooms:
        logger.info(f"Пользователь {request.player_id} попытался оставить карту в несуществующей комнате {request.room_id}")
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[request.room_id]
    player_idx: int = current_room["players"].index(request.player_id)
    if current_room["active_player"] != player_idx:
        logger.info(f"Пользователь {request.player_id} пытался оставить карту, но не его ход в комнате {request.room_id}")
        return {"msg": "Не ваш ход.", "ok": False, "status": 401}
    current_room["active_player"] = int(not player_idx)  #Reverse active player
    current_room["count"][player_idx] += 1
    logger.info(f"Пользователь {request.player_id} оставил карту в комнате {request.room_id}")
    return {"msg": "Вы оставили карты", "ok": True, "status": 200}


@app.post('/api/blackjack/take', response_class=JSONResponse)
async def take_card(request: TurnRequest):
    if not is_telegram(request.initData):
        logger.warning(f"Кто-то пытался взять карту с некорректными данными: {request.initData}")
        return {"msg": "Как ты сюда попал", "ok": False, "status": 401}
    if request.room_id not in blackjack_rooms:
        logger.info(f"Пользователь {request.player_id} попытался взять карту в несуществующей комнате {request.room_id}")
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[request.room_id]
    player_idx: int = current_room["players"].index(request.player_id)
    if current_room["active_player"] != player_idx:
        logger.info(f"Пользователь {request.player_id} пытался взять карту, но не его ход в комнате {request.room_id}")
        return {"msg": "Не ваш ход.", "ok": False, "status": 401}
    current_room["hands"][player_idx].append(choice(cards_52))
    player_hand = current_room["hands"][player_idx]
    if calculate_hand_value(player_hand) > 21:
        opponent_idx: int = int(not player_idx)
        current_room[player_idx] += 1
        if current_room["count"][player_idx] > current_room["count"][
                opponent_idx]:
            current_room["count"][opponent_idx] += 1
            opponent = True
        else:
            opponent = False
        logger.info(f"У пользователя {request.player_id} перебор в комнате {request.room_id}")
        return {
            "msg": "У вас перебор.",
            "ok": True,
            "status": 202,
            "hand": player_hand,
            "opponent": opponent
        }
    logger.info(f"Пользователь {request.player_id} взял карту в комнате {request.room_id}")
    return {
        "msg": "Вы взяли карту.",
        "ok": True,
        "status": 200,
        "hand": player_hand
    }


@app.get('/api/blackjack/updates', response_class=JSONResponse)
async def get_blackjack_updates(player_id: int, room_id: str):
    if room_id not in blackjack_rooms:
        logger.info(f"Пользователь {player_id} запросил обновления в несуществующей комнате {room_id}")
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[room_id]
    if any(item == 3 for item in current_room["results"].values()):
        self_idx: int = current_room["players"].index(player_id)
        self: int = current_room["results"][self_idx]
        opponent: int = current_room["results"][int(not self_idx)]
        if self > opponent:
            logger.info(f"Пользователь {player_id} выиграл в комнате {room_id}")
            return {"msg": "Вы выиграли!", "ok": True, "status": 200}
        elif self < opponent:
            logger.info(f"Пользователь {player_id} проиграл в комнате {room_id}")
            return {"msg": "Вы проиграли!", "ok": True, "status": 200}
        else:
            logger.info(f"Ничья в комнате {room_id}")
            return {"msg": "Ничья!", "ok": True, "status": 200}
    if len(current_room["players"]) < 2:
        logger.info(f"Противник пользователя {player_id} вышел из комнаты {room_id}")
        return {
            "msg": "Противник вышел из игры! Вы выиграли!",
            "ok": True,
            "status": 200
        }
    self_idx: int = current_room["players"].index(player_id)
    opponent_idx: int = int(not self_idx)
    data = {
        "active_player": current_room["active_player"] == self_idx,
        "self": {
            "hands": current_room["hands"][self_idx],
            "count": current_room["count"][self_idx],
            "results": current_room["results"][self_idx]
        },
        "opponent": {
            "hands": current_room["hands"][opponent_idx],
            "count": current_room["count"][opponent_idx],
            "results": current_room["results"][opponent_idx]
        }
    }
    logger.info(f"Пользователь {player_id} успешно получил обновления в комнате {room_id}")
    return {
        "msg": "Обновления успешно получены.",
        "ok": True,
        "status": 200,
        "data": data
    }

@app.get('/api/blackjack/rooms', response_class=JSONResponse)
async def get_blackjack_rooms(request: Request):
    available_rooms = [{
        "room_id": room_id,
        "name": details["name"],
        "reward": details["reward"]
    } for room_id, details in blackjack_rooms.items() if not details["going"]]
    return {"ok": True, "status": 200, "rooms": available_rooms}


@app.post('/api/blackjack/leave', response_class=JSONResponse)
async def leave_blackjack_room(request: LeaveRequest):
    if request.room_id not in blackjack_rooms:
        logger.info(f"Пользователь {request.player_id} пытался выйти из несуществующей комнаты {request.room_id}")
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[request.room_id]
    if request.player_id not in current_room["players"]:
        return {"msg": "Ты не в игре!", "ok": False, "status": 401}
    current_room["players"].remove(request.player_id)
    logger.info(f"Пользователь {request.player_id} вышел из комнаты {request.room_id}")
    return {"msg": "Вы вышли из игры!", "ok": True, "status": 200}


@app.get('/api/blackjack/reward', response_class=JSONResponse)
async def get_blackjack_reward(room_id: str):
    if room_id not in blackjack_rooms:
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[room_id]
    return {
        "msg": "Награда забрана.",
        "ok": True,
        "status": 200,
        "reward": current_room["reward"]
    }

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

@app.get('/api/guess/currencies', response_class=JSONResponse)
async def get_currencies():
    async with aiohttp.ClientSession(
        headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
        }
    ) as session:
        html = await fetch(session, "https://coinmarketcap.com")
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("tbody")
        trs = table.find_all("tr", limit=20)
        coins = []
        for tr in trs:
            tds = tr.find_all("td")
            price = tds[3].get_text()
            value, rate = tds[2].get_text(" ", strip=True).rsplit(" ", maxsplit=1)
            coins.append({"value": value, "rate": rate, "price": price})
    return {"msg": "Курсы успешно получены", "ok": True, "status": 200, "coins": coins}

@app.post('/api/lottery', response_class=JSONResponse)
async def get_lottery():
    return {"msg": "Лотерея успешно получена", "ok": True, "status": 200, "lottery": "Here is value of current lottery", "time": "End time"}

@app.get("/referal", response_class=HTMLResponse)
async def referal(request: Request):
    return templates.TemplateResponse("index.html",
                                      context={"request": request})


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html",
                                      context={"request": request})


@app.get("/balance", response_class=HTMLResponse)
async def balance(request: Request):
    return templates.TemplateResponse("index.html",
                                      context={"request": request})


@app.get("/games", response_class=HTMLResponse)
async def games(request: Request):
    return templates.TemplateResponse("index.html",
                                      context={"request": request})


@app.get("/game", response_class=HTMLResponse)
async def game(request: Request):
    return templates.TemplateResponse("index.html",
                                      context={"request": request})


@app.get("/lottery", response_class=HTMLResponse)
async def lottery(request: Request):
    return templates.TemplateResponse("index.html", context=request)


async def run_fastapi():
    uvicorn.run(app=app, host="localhost", port=8002)



if __name__ == "__main__":
    uvicorn.run(app="main:app", host="localhost", port=8001, reload=True)
    asyncio.get_event_loop_policy().get_event_loop().run_until_complete(
        dp.start_polling(bot, on_startup=run_fastapi))
    #asyncio.get_running_loop()

#loop = asyncio.get_event_loop()
#loop.run_until_complete(dp.start_polling(bot))

#if __name__ == '__main__':

#    uvicorn.run(app=app, host="localhost", port=8002)
