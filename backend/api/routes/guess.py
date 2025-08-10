from typing import Annotated

import aiohttp
from bs4 import BeautifulSoup
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse

from backend.db.actions import Actions
from backend.db.session import AsyncSession, get_session
from backend.domain.games import CoinBetRequest

router = APIRouter(prefix="/guess", tags=["guess"])


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


@router.get("/currencies", response_class=JSONResponse)
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


@router.post("/bet", response_class=JSONResponse)
async def make_guess_bet(
    request: Request,
    data: CoinBetRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    if not await Actions(session).create_bet(
        request.state.user_id, data.coin_name, data.bet, data.time, data.way
    ):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Ставка не создана")
    return JSONResponse(
        {
            "msg": "Ставка успешно создана",
        },
        status.HTTP_201_CREATED,
    )
