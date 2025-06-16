import asyncio
import sys
from random import choice, randint
from typing import List

import aiohttp
import schedule
import uvicorn
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import app.lottery as ltry
import app.telegram_bot as telegram_bot
from app.database import db
from app.request_models import *
from app.tech import is_tech_works
from app.utils import *

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.ms}</green> | <cyan>{file.path}:{line}:{function}</cyan> | <level>{message}</level>",
)

load_dotenv()

bot, dp = telegram_bot.get_bot()

app = FastAPI(title="SPA App", docs_url=None, redoc_url=None)
app.mount(
    "/assets", StaticFiles(directory="app/assets", check_dir=False), name="assets"
)


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except (HTTPException, StarletteHTTPException) as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            else:
                raise ex


api_app = FastAPI(title="API App", docs_url=None, redoc_url=None)
app.mount("/api", api_app)
app.mount("/", SPAStaticFiles(directory="app/templates", html=True), name="index")

dice_rooms: dict = dict()
blackjack_rooms: dict = dict()

cards_52: List[str] = [
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

templates: Jinja2Templates = Jinja2Templates(directory="app/templates")

wallets = []


@api_app.post("/initdata/check", response_class=JSONResponse)
async def check_init_data():
    if is_tech_works():
        return {"msg": "Технические работы", "ok": False, "status": 404}


@api_app.post("/lottery/topwinners", response_class=JSONResponse)
async def get_top_lottery_winners():
    winners = await ltry.get_top_winners()
    return {
        "msg": "Топ победители лотереи получены успешно",
        "ok": True,
        "status": 200,
        "winners": winners,
    }


@api_app.post("/wallet/disconnect", response_class=JSONResponse)
async def disconnect_wallet(request: Request):
    await db.remove_user_wallet(request.state.user_id)
    return {"msg": "Кошелек успешно отключен", "ok": True, "status": 200}


@api_app.post("/wallet/connect", response_class=JSONResponse)
async def connect_wallet(request: Request, data: WalletRequest):
    await db.add_user_wallet(request.state.user_id, data.wallet_address)
    return {"msg": "Кошелек успешно подключен", "ok": True, "status": 200}


@api_app.post("/lottery/deposit", response_class=JSONResponse)
async def make_lottery_deposit(request: Request, data: LotteryBetRequest):
    await ltry.make_deposit(request.state.user_id, data.reward, data.bet)
    return {"msg": "Ставка успешно принята", "ok": True, "status": 200}


@api_app.post("/guess/bet", response_class=JSONResponse)
async def make_guess_bet(request: Request, data: CoinBetRequest):
    bet = await db.create_bet(
        request.state.user_id, data.coin_name, data.bet, data.time, data.way
    )
    if not bet:
        return {"msg": "Ставка не создана", "ok": False, "status": 400}
    return {
        "msg": "Ставка успешно создана",
        "ok": True,
        "status": 201,
    }


@api_app.post("/game/params/get", response_class=JSONResponse)
async def make_game_params(request: Request):
    money, *bonus, last_visit = await db.get_game_params(request.state.user_id)
    return {
        "msg": "Параметры игры получены успешно",
        "ok": True,
        "status": 200,
        "params": {
            "money": money,
            "bonus": 1 if all(bonus) else -1,
            "last_visit": last_visit,
        },
    }


@api_app.post("/game/add/money", response_class=JSONResponse)
async def add_money(request: Request):
    await db.add_user_money_balance(request.state.user_id)
    return {"msg": "Деньги успешно добавлены", "ok": True, "status": 200}


@api_app.post("/wallet/deposit", response_class=JSONResponse)
async def get_wallet_for_deposit(request: Request, data: WalletAmountRequest):
    balances = []
    if wallets:
        for wallet in wallets:
            balances.append(await get_ton_balance(wallet))
    else:
        return {"msg": "Ошибка, кошелька нет", "ok": False, "status": 404}
    index = balances.index(min(balances))
    return {
        "msg": "Баланс успешно пополнен",
        "ok": True,
        "status": 200,
        "wallet": wallets[index],
    }


@api_app.post("/game/money", response_class=JSONResponse)
async def invest_game_money(request: Request, data: AmountRequest):
    logger.info(
        f"Пользователь {request.player_id} получил в главное игре: {request.bet}"
    )
    await db.invest_game_money(request.player_id, request.bet)
    return {"msg": "Деньги успешно вложены", "ok": True, "status": 200}


@api_app.post("/wallet/get_balance", response_class=JSONResponse)
async def get_wallet_balance(request: Request):
    player = await db.get_user(request.player_id)
    if not player:
        return {"msg": "Пользователь не найден", "ok": False, "status": 404}
    wallet = player.wallet_address
    balance = await get_ton_balance(wallet)
    logger.info(f"Баланс пользователя {request.player_id} получен: {balance}")
    return {"msg": "Баланс получен", "ok": True, "status": 200, "balance": balance}


@api_app.post("/money/check", response_class=JSONResponse)
async def check_money_amount(request: Request, data: AmountRequest):
    player = await db.get_user(request.player_id)
    if not player:
        return {"msg": "Пользователь не найден", "ok": False, "status": 404}
    logger.info(f"У пользователя: {player.money_balance}. Запрошено: {request.bet}")
    if player.money_balance < request.bet:
        return {"msg": "Недостаточно монет", "ok": False, "status": 402}
    return {"msg": "Монет достаточно", "ok": True, "status": 200}


@api_app.post("/player/get", response_class=JSONResponse)
async def get_player_by_id(request: Request):
    player = await db.get_user(request.player_id)
    if player:
        logger.info(f"Пользователь {request.player_id} был взят из базы данных")
        return {
            "msg": "Игрок успешно найден",
            "ok": True,
            "status": 200,
            "player": {
                "wallet_address": player.wallet_address,
                "money_balance": player.money_balance,
            },
        }
    else:
        logger.warning(f"Была попытка поиска пользователя под id: {request.player_id}")
        return {"ok": False, "status": 404, "msg": "Игрок не найден"}


@api_app.post("/player/post", response_class=JSONResponse)
async def create_player(request: Request, data: CreateUserRequest):
    wallet_address = request.wallet_address
    username = request.username
    telegram_id = request.telegram_id
    if await db.create_user(
        telegram_id=telegram_id, username=username, wallet_address=wallet_address
    ):
        logger.info(
            f"Создан пользователь. ID: {request.telegram_id}. Никнейм: {request.username}. Адрес кошелька: {request.wallet_address}"
        )
        return {"msg": "Игрок успешно создан", "ok": True, "status": 201}
    else:
        logger.error(
            f"Не удалось создать игрока с данными: ID: {request.telegram_id}. Никнейм: {request.username}. Адрес кошелька: {request.wallet_address}"
        )
        return {"ok": False, "status": 400, "msg": "Ошибка создания игрока"}


@api_app.post("/reward/get", response_class=JSONResponse)
async def find_out_reward(request: Request):
    """
    Get amount of reward for every of referal
    """
    reward = await db.get_referral_reward(request.player_id)
    return {"msg": "Награда забрана", "ok": True, "status": 200, "reward": reward or 0}


@api_app.post("/take-reward", response_class=JSONResponse)
async def take_reward(request: Request):
    """
    Get amount of reward for every of referal
    """
    reward = await db.take_referral_reward(request.player_id)
    return {"msg": "Награда забрана", "ok": True, "status": 200, "reward": reward}


@api_app.post("/reward/post", response_class=JSONResponse)
async def get_reward(request: Request):
    """
    Get amount of reward for every of referal
    """
    reward = await db.take_referral_reward(request.player_id)
    logger.info(f"Пользователь {request.player_id} получил награду: {reward}")
    return {"msg": "Награда забрана", "ok": True, "status": 200, "reward": reward}


@api_app.post("/referral/get", response_class=JSONResponse)
async def get_referral_count(request: Request):
    """
    Get count of referrals of certain user
    """
    referral_count = await db.get_referral_count(request.player_id)
    return {
        "msg": "Количество рефералов получено",
        "ok": True,
        "status": 200,
        "referral_count": referral_count,
    }


@api_app.post("/invite/link", response_class=JSONResponse)
async def get_invite_link(request: Request):
    """
    Get invitation link for certain user
    """
    invite_link = await get_invitation_link(request.player_id)
    return {
        "msg": "Инвайт ссылка получена",
        "ok": True,
        "status": 200,
        "invite_link": invite_link,
    }


@api_app.post("/transaction", response_class=JSONResponse)
async def create_transaction(request: Request, data: TransactionRequest):
    amount = request.amount
    transaction_type = request.transaction_type

    if await db.create_transaction(request.telegram_id, amount, transaction_type):
        logger.info(
            f"Создана транзакция. ID: {request.telegram_id}. Сумма: {amount}. Тип транзакции: {'Вывод' if transaction_type else 'Депозит'}"
        )
        return {"msg": "Транзакция успешно создана", "ok": True, "status": 201}
    else:
        logger.error(
            f"Не удалось создать транзакцию с данными: ID: {request.telegram_id}. Сумма: {amount}. Тип транзакции: {'Вывод' if transaction_type else 'Депозит'}"
        )
        return {"ok": False, "status": 400, "msg": "Ошибка создания транзакции"}


@api_app.post("/transactions/get")
async def get_transactions(request: Request):
    transactions = await db.get_user_transactions(request.player_id)
    return {
        "msg": "Транзакции получены",
        "ok": True,
        "status": 200,
        "data": transactions,
    }


@api_app.post("/game/finish", response_class=JSONResponse)
async def create_finished_game(request: Request, data: FinishedGameRequest):
    game_type = request.game_type
    amount = request.amount
    first_user_id = request.first_user_id
    second_user_id = request.second_user_id
    _hash = generate_room_id()
    if await db.mark_finished_game(
        game_type, amount, first_user_id, second_user_id, _hash
    ):
        logger.info(
            f"Игра {game_type} {f'между {first_user_id} и {second_user_id}' if second_user_id else f'от {first_user_id}'} "
            f"завершена. Сумма: {amount}"
        )
        return {"msg": "Игра успешно завершена", "ok": True, "status": 201}
    else:
        logger.error(
            f"Не удалось завершить игру с данными: тип игры {game_type}, сумма {amount}, ID первого игрока {first_user_id}, ID второго игрока {second_user_id}"
        )
        return {"ok": False, "status": 400, "msg": "Ошибка завершения игры"}


@api_app.get("/dice/rooms", response_class=JSONResponse)
async def get_dice_rooms():
    available_rooms = [
        {"room_id": room_id, "name": details["name"], "reward": details["reward"]}
        for room_id, details in dice_rooms.items()
        if not details["going"]
    ]
    return {"ok": True, "status": 200, "rooms": available_rooms}


@api_app.post("/dice/create", response_class=JSONResponse)
async def create_dice_room(request: Request, data: CreateRoomRequest):
    new_room_id = generate_room_id()
    name = request.name
    reward = request.reward
    dice_rooms[new_room_id] = {
        "name": name,
        "reward": int(reward),
        "going": False,
        "active_player": randint(0, 1),
        "players": [request.player_id],
        "hands": {
            0: 0,
        },
        "count": {0: 0},
        "results": {0: 0},
    }
    logger.info(
        f"Пользователь {request.player_id} создал комнату кубиков с наградой {reward}$"
    )
    return {
        "ok": True,
        "status": 200,
        "msg": "Комната успешно создана",
        "room_id": new_room_id,
    }


@api_app.post("/dice/join", response_class=JSONResponse)
async def join_dice_room(request: Request, data: RoomRequest):
    current_room: dict = dice_rooms[request.room_id]
    if len(current_room["players"]) > 1:
        logger.info(
            f"Пользователь {request.player_id} попытался присоединиться к заполненной комнате {request.room_id}"
        )
        return {"msg": "Комната заполнена.", "ok": False, "status": 403}
    current_room["going"] = True
    current_room["players"].append(request.player_id)
    current_room["hands"][1] = 0
    current_room["count"][1] = 0
    current_room["results"][1] = 0
    logger.info(
        f"Пользователь {request.player_id} присоединился к комнате {request.room_id}"
    )
    return {
        "msg": "Вы успешно присоединились к комнате!",
        "ok": True,
        "status": 200,
        "room_id": request.room_id,
        "name": current_room["name"],
        "reward": current_room["reward"],
    }


@api_app.post("/dice/roll", response_class=JSONResponse)
async def roll_dice(request: Request, data: RoomRequest):
    current_room: dict = dice_rooms[request.room_id]
    if current_room["active_player"] != 0:
        logger.info(
            f"Пользователь {request.player_id} попытался бросить кубики, но не его ход в комнате {request.room_id}"
        )
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
    logger.info(
        f"Пользователь {request.player_id} бросил кубики в комнате {request.room_id}"
    )
    return {"msg": "Вы бросили кубики!", "ok": True, "status": 200, "dice": dice_value}


@api_app.get("/dice/reward", response_class=JSONResponse)
async def get_dice_reward(room_id: str):
    if room_id not in dice_rooms:
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = dice_rooms[room_id]
    return {
        "msg": "Награда забрана.",
        "ok": True,
        "status": 200,
        "reward": current_room["reward"],
    }


@api_app.get("/dice/updates", response_class=JSONResponse)
async def get_dice_updates(player_id: int, room_id: str):
    if room_id not in dice_rooms:
        logger.info(
            f"Пользователь {player_id} запросил обновления в несуществующей комнате {room_id}"
        )
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
            "status": 200,
        }
    self_idx: int = current_room["players"].index(player_id)
    opponent_idx: int = int(not self_idx)
    logger.info(
        f"Пользователь {player_id} успешно получил обновления в комнате {room_id}"
    )
    return {
        "msg": "Обновления успешно получены.",
        "ok": True,
        "status": 200,
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


@api_app.post("/blackjack/create", response_class=JSONResponse)
async def create_blackjack_room(request: Request, data: CreateRoomRequest):
    name: str = request.name
    reward: int = request.reward
    new_room_id: str = generate_room_id()
    blackjack_rooms[new_room_id] = {
        "name": name,
        "reward": int(reward),
        "going": False,
        "active_player": randint(0, 1),
        "players": [request.player_id],
        "hands": {
            0: [choice(cards_52), choice(cards_52)],
        },
        "count": {0: 0},
        "results": {0: 0},
    }
    logger.info(
        f"Пользователь {request.player_id} создал комнату блэкджека с наградой {reward}$"
    )
    return {
        "msg": "Комната успешно создана!",
        "ok": True,
        "status": 200,
        "room_id": new_room_id,
    }


@api_app.post("/blackjack/join", response_class=JSONResponse)
async def join_blackjack_room(request: Request, data: RoomRequest):
    current_room: dict = blackjack_rooms[request.room_id]
    if len(current_room["players"]) > 1:
        logger.info(
            f"Пользователь {request.player_id} попытался присоединиться к заполненной комнате {request.room_id}"
        )
        return {"msg": "Комната заполнена.", "ok": False, "status": 403}
    current_room["going"] = True
    current_room["players"].append(request.player_id)
    current_room["hands"][1] = [choice(cards_52), choice(cards_52)]
    current_room["count"][1] = 0
    current_room["results"][1] = 0
    logger.info(
        f"Пользователь {request.player_id} присоединился к комнате {request.room_id}"
    )
    return {
        "msg": "Вы успешно присоединились к комнате!",
        "ok": True,
        "status": 200,
        "room_id": request.room_id,
        "name": current_room["name"],
        "reward": current_room["reward"],
    }


@api_app.post("/blackjack/pass", response_class=JSONResponse)
async def pass_card(request: Request, data: RoomRequest):
    if request.room_id not in blackjack_rooms:
        logger.info(
            f"Пользователь {request.player_id} попытался оставить карту в несуществующей комнате {request.room_id}"
        )
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[request.room_id]
    player_idx: int = current_room["players"].index(request.player_id)
    if current_room["active_player"] != player_idx:
        logger.info(
            f"Пользователь {request.player_id} пытался оставить карту, но не его ход в комнате {request.room_id}"
        )
        return {"msg": "Не ваш ход.", "ok": False, "status": 401}
    current_room["active_player"] = int(not player_idx)  # Reverse active player
    current_room["count"][player_idx] += 1
    logger.info(
        f"Пользователь {request.player_id} оставил карту в комнате {request.room_id}"
    )
    return {"msg": "Вы оставили карты", "ok": True, "status": 200}


@api_app.post("/blackjack/take", response_class=JSONResponse)
async def take_card(request: Request, data: RoomRequest):
    if request.room_id not in blackjack_rooms:
        logger.info(
            f"Пользователь {request.player_id} попытался взять карту в несуществующей комнате {request.room_id}"
        )
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[request.room_id]
    player_idx: int = current_room["players"].index(request.player_id)
    if current_room["active_player"] != player_idx:
        logger.info(
            f"Пользователь {request.player_id} пытался взять карту, но не его ход в комнате {request.room_id}"
        )
        return {"msg": "Не ваш ход.", "ok": False, "status": 401}
    current_room["hands"][player_idx].append(choice(cards_52))
    player_hand = current_room["hands"][player_idx]
    if calculate_hand_value(player_hand) > 21:
        opponent_idx: int = int(not player_idx)
        current_room[player_idx] += 1
        if current_room["count"][player_idx] > current_room["count"][opponent_idx]:
            current_room["count"][opponent_idx] += 1
            opponent = True
        else:
            opponent = False
        logger.info(
            f"У пользователя {request.player_id} перебор в комнате {request.room_id}"
        )
        return {
            "msg": "У вас перебор.",
            "ok": True,
            "status": 202,
            "hand": player_hand,
            "opponent": opponent,
        }
    logger.info(
        f"Пользователь {request.player_id} взял карту в комнате {request.room_id}"
    )
    return {"msg": "Вы взяли карту.", "ok": True, "status": 200, "hand": player_hand}


@api_app.get("/blackjack/updates", response_class=JSONResponse)
async def get_blackjack_updates(player_id: int, room_id: str):
    if room_id not in blackjack_rooms:
        logger.info(
            f"Пользователь {player_id} запросил обновления в несуществующей комнате {room_id}"
        )
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
            "status": 200,
        }
    self_idx: int = current_room["players"].index(player_id)
    opponent_idx: int = int(not self_idx)
    logger.info(
        f"Пользователь {player_id} успешно получил обновления в комнате {room_id}"
    )
    return {
        "msg": "Обновления успешно получены.",
        "ok": True,
        "status": 200,
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


@api_app.get("/blackjack/rooms", response_class=JSONResponse)
async def get_blackjack_rooms():
    available_rooms = [
        {"room_id": room_id, "name": details["name"], "reward": details["reward"]}
        for room_id, details in blackjack_rooms.items()
        if not details["going"]
    ]
    return {"ok": True, "status": 200, "rooms": available_rooms}


@api_app.post("/blackjack/leave", response_class=JSONResponse)
async def leave_blackjack_room(request: Request, data: LeaveRequest):
    if request.room_id not in blackjack_rooms:
        logger.info(
            f"Пользователь {request.player_id} пытался выйти из несуществующей комнаты {request.room_id}"
        )
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[request.room_id]
    if request.player_id not in current_room["players"]:
        return {"msg": "Ты не в игре!", "ok": False, "status": 401}
    current_room["players"].remove(request.player_id)
    logger.info(f"Пользователь {request.player_id} вышел из комнаты {request.room_id}")
    return {"msg": "Вы вышли из игры!", "ok": True, "status": 200}


@api_app.get("/blackjack/reward", response_class=JSONResponse)
async def get_blackjack_reward(room_id: str):
    if room_id not in blackjack_rooms:
        return {"msg": "Комната не найдена!", "ok": False, "status": 404}
    current_room: dict = blackjack_rooms[room_id]
    return {
        "msg": "Награда забрана.",
        "ok": True,
        "status": 200,
        "reward": current_room["reward"],
    }


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


@api_app.get("/guess/currencies", response_class=JSONResponse)
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
            coins.append({"name": value, "symbol": rate, "price": price})
    return {"msg": "Курсы успешно получены", "ok": True, "status": 200, "coins": coins}


@api_app.post("/lottery", response_class=JSONResponse)
async def get_lottery():
    end_time, amount = await ltry.get_current_lottery()
    return {
        "msg": "Лотерея успешно получена",
        "ok": True,
        "status": 200,
        "lottery": amount,
        "time": end_time,
    }


def task_mark_guess_games():
    asyncio.run_coroutine_threadsafe(
        coro=db.mark_guess_games(), loop=asyncio.get_running_loop()
    )


def clear_game_sessions():
    asyncio.run_coroutine_threadsafe(
        coro=db.clear_game_sessions(), loop=asyncio.get_running_loop()
    )


async def start_uvicorn() -> None:
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config=config)
    await server.serve()


async def start_bot() -> None:
    await dp.start_polling(bot)


async def main() -> None:
    await asyncio.gather(
        # start_bot(),
        start_uvicorn()
    )


if __name__ == "__main__":
    schedule.every().day.at("00:00").do(clear_game_sessions)
    schedule.every().hour.at(":00").do(task_mark_guess_games)
    asyncio.run(main())

    # asyncio.get_running_loop()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(dp.start_polling(bot))

# if __name__ == '__main__':

#    uvicorn.run(app=app, host="localhost", port=8002)
