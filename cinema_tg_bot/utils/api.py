import httpx
from cinema_tg_bot.config import API_BASE_URL


async def confirm_telegram_link(code: str, tg_id: int):
    url = f"{API_BASE_URL}telegram/link/confirm/"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={"code": code, "tg_id": tg_id})
            if r.status_code == 200:
                return True, "✅ Your Telegram account has been successfully linked!"
            return False, r.json().get("error", "Linking failed.")
    except Exception as e:
        return False, f"🚫 Connection to the API failed: {e}"


async def check_telegram_link(tg_id: int):
    url = f"{API_BASE_URL}telegram/link/check/{tg_id}/"
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            return r.status_code == 200
    except httpx.RequestError as e:
         # This covers all network-related issues: DNS errors, timeouts, etc.
        return False

async def user_profile_info(tg_id: int):
    url = f'{API_BASE_URL}telegram/user/info/{tg_id}/'
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:  # 10 секунд timeout
            r = await client.get(url)
            if r.status_code == 200:
                return True, r.json()
            else:
                return False, f"Error {r.status_code}: {r.text}"
    except httpx.RequestError as e:
        return False, f"Request failed: {str(e)}"

async def get_order_list(tg_id: int):
    url = f'{API_BASE_URL}telegram/user/orders/{tg_id}/'
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            if r.status_code == 200:
                return True, r.json()
    except httpx.RequestError as e:
        # This covers all network-related issues: DNS errors, timeouts, etc.
        return False


async def request_link_code(email: str):
    url = f'{API_BASE_URL}telegram/send-email/'
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json={'email': email})
            if r.status_code == 200:
                return True, None
            data = r.json()
            return False, data.get('error', 'Unknown error')
    except httpx.RequestError as e:
        # This covers all network-related issues: DNS errors, timeouts, etc.
        return False