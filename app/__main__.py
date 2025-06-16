import asyncio
import sys
from random import choice, randint
from typing import List

import aiohttp
import schedule
import uvicorn
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, status
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

dice_rooms = dict()
blackjack_rooms = dict()

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
async def check_init_data() -> JSONResponse:
    if is_tech_works():
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="Технические работы"
        )
    return JSONResponse({"msg": "Инициализация успешна"})


@api_app.post("/lottery/topwinners", response_class=JSONResponse)
async def get_top_lottery_winners() -> JSONResponse:
    winners = await ltry.get_top_winners()
    return JSONResponse(
        {
            "msg": "Топ победители лотереи получены успешно",
            "winners": winners,
        }
    )


@api_app.post("/wallet/disconnect", response_class=JSONResponse)
async def disconnect_wallet(request: Request) -> JSONResponse:
    await db.remove_user_wallet(request.state.user_id)
    return JSONResponse({"msg": "Кошелек успешно отключен"})


@api_app.post("/wallet/connect", response_class=JSONResponse)
async def connect_wallet(request: Request, data: WalletRequest) -> JSONResponse:
    await db.add_user_wallet(request.state.user_id, data.wallet_address)
    return JSONResponse({"msg": "Кошелек успешно подключен"})


@api_app.post("/lottery/deposit", response_class=JSONResponse)
async def make_lottery_deposit(
    request: Request, data: LotteryBetRequest
) -> JSONResponse:
    await ltry.make_deposit(request.state.user_id, data.reward, data.bet)
    return JSONResponse({"msg": "Ставка успешно принята"})


@api_app.post("/guess/bet", response_class=JSONResponse)
async def make_guess_bet(request: Request, data: CoinBetRequest) -> JSONResponse:
    if not await db.create_bet(
        request.state.user_id, data.coin_name, data.bet, data.time, data.way
    ):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Ставка не создана")
    return JSONResponse(
        {
            "msg": "Ставка успешно создана",
        },
        status.HTTP_201_CREATED,
    )


@api_app.post("/game/params/get", response_class=JSONResponse)
async def make_game_params(request: Request) -> JSONResponse:
    money, *bonus, last_visit = await db.get_game_params(request.state.user_id)
    return JSONResponse(
        {
            "msg": "Параметры игры получены успешно",
            "params": {
                "money": money,
                "bonus": 1 if all(bonus) else -1,
                "last_visit": last_visit,
            },
        }
    )


@api_app.post("/game/add/money", response_class=JSONResponse)
async def add_money(request: Request) -> JSONResponse:
    await db.add_user_money_balance(request.state.user_id)
    return JSONResponse({"msg": "Деньги успешно добавлены"})


@api_app.post("/wallet/deposit", response_class=JSONResponse)
async def get_wallet_for_deposit(
    request: Request, data: WalletAmountRequest
) -> JSONResponse:
    balances = []
    if wallets:
        for wallet in wallets:
            balances.append(await get_ton_balance(wallet))
    else:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Кошельки не найдены")
    index = balances.index(min(balances))
    return JSONResponse(
        {
            "msg": "Баланс успешно пополнен",
            "wallet": wallets[index],
        }
    )


@api_app.post("/game/money", response_class=JSONResponse)
async def invest_game_money(request: Request, data: AmountRequest) -> JSONResponse:
    logger.info(
        f"Пользователь {request.state.user_id} получил в главное игре: {data.bet}"
    )
    await db.invest_game_money(request.state.user_id, data.bet)
    return JSONResponse({"msg": "Деньги успешно вложены"})


@api_app.post("/wallet/get_balance", response_class=JSONResponse)
async def get_wallet_balance(request: Request) -> JSONResponse:
    if not (player := await db.get_user(request.state.user_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    wallet = player.wallet_address
    balance = await get_ton_balance(wallet)
    logger.info(f"Баланс пользователя {request.state.user_id} получен: {balance}")
    return JSONResponse({"msg": "Баланс получен", "balance": balance})


@api_app.post("/money/check", response_class=JSONResponse)
async def check_money_amount(request: Request, data: AmountRequest) -> JSONResponse:
    if not (player := await db.get_user(request.state.user_id)):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    logger.info(f"У пользователя: {player.money_balance}. Запрошено: {data.bet}")
    if player.money_balance < data.bet:
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED, detail="Недостаточно монет"
        )
    return JSONResponse({"msg": "Монет достаточно"})


@api_app.post("/player/get", response_class=JSONResponse)
async def get_player_by_id(request: Request) -> JSONResponse:
    if not (player := await db.get_user(request.state.user_id)):
        logger.warning(
            f"Была попытка поиска пользователя под id: {request.state.user_id}"
        )
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    logger.info(f"Пользователь {request.state.user_id} был взят из базы данных")
    return JSONResponse(
        {
            "msg": "Игрок успешно найден",
            "player": {
                "wallet_address": player.wallet_address,
                "money_balance": player.money_balance,
            },
        }
    )


@api_app.post("/player/post", response_class=JSONResponse)
async def create_player(request: Request, data: CreateUserRequest) -> JSONResponse:
    wallet_address = data.wallet_address
    username = data.username
    telegram_id = data.telegram_id
    if not await db.create_user(
        telegram_id=telegram_id, username=username, wallet_address=wallet_address
    ):
        logger.error(
            f"Не удалось создать игрока с данными: ID: {data.telegram_id}. Никнейм: {data.username}. Адрес кошелька: {data.wallet_address}"
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Ошибка создания игрока"
        )
    logger.info(
        f"Создан пользователь. ID: {data.telegram_id}. Никнейм: {data.username}. Адрес кошелька: {data.wallet_address}"
    )
    return JSONResponse({"msg": "Игрок успешно создан"}, status.HTTP_201_CREATED)


@api_app.post("/reward/get", response_class=JSONResponse)
async def find_out_reward(request: Request) -> JSONResponse:
    """
    Get amount of reward for every of referal
    """
    reward = await db.get_referral_reward(request.state.user_id)
    return JSONResponse({"msg": "Награда забрана", "reward": reward or 0})


@api_app.post("/take-reward", response_class=JSONResponse)
async def take_reward(request: Request) -> JSONResponse:
    """
    Get amount of reward for every of referal
    """
    reward = await db.take_referral_reward(request.state.user_id)
    return JSONResponse({"msg": "Награда забрана", "reward": reward})


@api_app.post("/reward/post", response_class=JSONResponse)
async def get_reward(request: Request) -> JSONResponse:
    """
    Get amount of reward for every of referal
    """
    reward = await db.take_referral_reward(request.state.user_id)
    logger.info(f"Пользователь {request.state.user_id} получил награду: {reward}")
    return JSONResponse({"msg": "Награда забрана", "reward": reward})


@api_app.post("/referral/get", response_class=JSONResponse)
async def get_referral_count(request: Request) -> JSONResponse:
    """
    Get count of referrals of certain user
    """
    referral_count = await db.get_referral_count(request.state.user_id)
    return JSONResponse(
        {
            "msg": "Количество рефералов получено",
            "referral_count": referral_count,
        }
    )


@api_app.post("/invite/link", response_class=JSONResponse)
async def get_invite_link(request: Request) -> JSONResponse:
    """
    Get invitation link for certain user
    """
    invite_link = await get_invitation_link(request.state.user_id)
    return JSONResponse(
        {
            "msg": "Ссылка для приглашения получена",
            "invite_link": invite_link,
        }
    )


@api_app.post("/transaction", response_class=JSONResponse)
async def create_transaction(
    request: Request, data: TransactionRequest
) -> JSONResponse:
    amount = data.amount
    transaction_type = data.transaction_type

    if not await db.create_transaction(request.state.user_id, amount, transaction_type):
        logger.error(
            f"Не удалось создать транзакцию с данными: ID: {request.state.user_id}. Сумма: {amount}. Тип транзакции: {'Вывод' if transaction_type else 'Депозит'}"
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Ошибка создания транзакции"
        )

    logger.info(
        f"Создана транзакция. ID: {request.state.user_id}. Сумма: {amount}. Тип транзакции: {'Вывод' if transaction_type else 'Депозит'}"
    )
    return JSONResponse({"msg": "Транзакция успешно создана"}, status.HTTP_201_CREATED)


@api_app.post("/transactions/get")
async def get_transactions(request: Request) -> JSONResponse:
    transactions = await db.get_user_transactions(request.state.user_id)
    return JSONResponse(
        {
            "msg": "Транзакции получены",
            "data": transactions,
        }
    )


@api_app.post("/game/finish", response_class=JSONResponse)
async def create_finished_game(
    request: Request, data: FinishedGameRequest
) -> JSONResponse:
    game_type = data.game_type
    amount = data.amount
    first_user_id = data.first_user_id
    second_user_id = data.second_user_id
    _hash = generate_room_id()
    if not await db.mark_finished_game(
        game_type, amount, first_user_id, second_user_id, _hash
    ):
        logger.error(
            f"Не удалось завершить игру с данными: тип игры {game_type}, сумма {amount}, ID первого игрока {first_user_id}, ID второго игрока {second_user_id}"
        )
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Ошибка завершения игры"
        )

    logger.info(
        f"Игра {game_type} {f'между {first_user_id} и {second_user_id}' if second_user_id else f'от {first_user_id}'} "
        f"завершена. Сумма: {amount}"
    )
    return JSONResponse({"msg": "Игра успешно завершена"}, status.HTTP_201_CREATED)


@api_app.get("/dice/rooms", response_class=JSONResponse)
async def get_dice_rooms() -> JSONResponse:
    available_rooms = [
        {"room_id": room_id, "name": details["name"], "reward": details["reward"]}
        for room_id, details in dice_rooms.items()
        if not details["going"]
    ]
    return JSONResponse({"rooms": available_rooms})


@api_app.post("/dice/create", response_class=JSONResponse)
async def create_dice_room(request: Request, data: CreateRoomRequest) -> JSONResponse:
    new_room_id = generate_room_id()
    name = data.name
    reward = data.reward
    dice_rooms[new_room_id] = {
        "name": name,
        "reward": int(reward),
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


@api_app.post("/dice/join", response_class=JSONResponse)
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


@api_app.post("/dice/roll", response_class=JSONResponse)
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


@api_app.get("/dice/reward", response_class=JSONResponse)
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


@api_app.get("/dice/updates", response_class=JSONResponse)
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


@api_app.post("/blackjack/create", response_class=JSONResponse)
async def create_blackjack_room(
    request: Request, data: CreateRoomRequest
) -> JSONResponse:
    name = data.name
    reward = data.reward
    new_room_id = generate_room_id()
    blackjack_rooms[new_room_id] = {
        "name": name,
        "reward": int(reward),
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


@api_app.post("/blackjack/join", response_class=JSONResponse)
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


@api_app.post("/blackjack/pass", response_class=JSONResponse)
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


@api_app.post("/blackjack/take", response_class=JSONResponse)
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


@api_app.get("/blackjack/updates", response_class=JSONResponse)
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


@api_app.get("/blackjack/rooms", response_class=JSONResponse)
async def get_blackjack_rooms() -> JSONResponse:
    available_rooms = [
        {"room_id": room_id, "name": details["name"], "reward": details["reward"]}
        for room_id, details in blackjack_rooms.items()
        if not details["going"]
    ]
    return JSONResponse({"rooms": available_rooms})


@api_app.post("/blackjack/leave", response_class=JSONResponse)
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


@api_app.get("/blackjack/reward", response_class=JSONResponse)
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


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


@api_app.get("/guess/currencies", response_class=JSONResponse)
async def get_currencies() -> JSONResponse:
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
    return JSONResponse({"msg": "Курсы успешно получены", "coins": coins})


@api_app.post("/lottery", response_class=JSONResponse)
async def get_lottery() -> JSONResponse:
    end_time, amount = await ltry.get_current_lottery()
    return JSONResponse(
        {
            "msg": "Лотерея успешно получена",
            "lottery": amount,
            "time": end_time,
        }
    )


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
