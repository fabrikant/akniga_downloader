import requests
from fake_useragent import UserAgent
from Crypto.Cipher import AES
from base64 import b64encode
from crypto import get_akniga_encrypt_dict, decrypt
import json

# from Crypto.Random import get_random_bytes

ASSETS = "ymXEKzvUkuo5G03.1C159BD535E9793"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0"
AKNIGA_URL = "https://akniga.org"


def get_m3u_url(book_url):

    session = requests.session()
    session.headers.update({"User-Agent": USER_AGENT})

    resp = session.get(book_url)
    if not resp.ok:
        return None

    content = resp.text
    security_ls_key = (
        content.split("LIVESTREET_SECURITY_KEY")[1]
        .split("=")[1]
        .split(",")[0]
        .replace("'", "")
        .strip()
    )
    bid = content.split("data-bid")[1].split("=")[1].split('"')[1]
    phpsessid = resp.cookies["PHPSESSID"]

    data = {
        "bid": bid,
        "hash": get_akniga_encrypt_dict(ASSETS, security_ls_key),
        "security_ls_key": security_ls_key,
    }

    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Origin": AKNIGA_URL,
        }
    )

    # cookies = {"PHPSESSID": phpsessid+"1"}
    # resp = session.post(f"{AKNIGA_URL}/ajax/b/{bid}", data=data, cookies=cookies)
    resp = session.post(f"{AKNIGA_URL}/ajax/b/{bid}", data=data)

    # print(resp.status_code)
    if not resp.ok:
        return None

    # print(resp.content)
    json_data = json.loads(resp.text)
    hres = json.loads(json_data["hres"])
    srv = json_data["srv"]

    print(hres)
    decrypt_path = decrypt(security_ls_key, hres["s"], hres["ct"])
    pass


# #"2e7b9e88a153fe407809c78d27a0e6d0"
# # "{\"ct\":\"I9Y0FYwiL/le3qd5NAUFFTLZBQmcLnBstd55WnDfdC8vznlRNrIaJgABJ/wxc32C\",\"iv\":\"571529020e50abaff3cd66f5ed50bcbe\",\"s\":\"959ba8e70ec66bc8\"}"
# def get_hash(security_ls_key):
#     assets = "ymXEKzvUkuo5G03.1C159BD535E9793"
#     cipher = AES.new(security_ls_key.encode("utf8"), AES.MODE_EAX)
#     ciphertext, tag = cipher.encrypt_and_digest(assets.encode())
#     nonce = cipher.nonce
#     # print(b64encode(ciphertext).decode())
#     # print(b64encode(nonce).decode())
#     # print(b64encode(tag).decode())

#     key = "959ba8e70ec66bc8".encode()
#     ciphertext = "I9Y0FYwiL/le3qd5NAUFFTLZBQmcLnBstd55WnDfdC8vznlRNrIaJgABJ/wxc32C".encode()
#     nonce= "571529020e50abaff3cd66f5ed50bcbe".encode()

#     cipher = AES.new(key, AES.MODE_EAX)
#     plaintext = cipher.decrypt_and_verify(ciphertext)

#     print(b64encode(ciphertext).decode())
#     #CSwHy3ir3MZ7yvZ4CzHbgYOsKgzhMqjq6wEuutU7vJJTJ0c38ExWkAY1QkLO
#     print(plaintext.decode())


def get_book_ajax(bid, phpsessid, url):

    # cookies = {"PHPSESSID": phpsessid}
    cookies = {"PHPSESSID": str(phpsessid), "a_ismobile": "0"}
    # cookies = {"PHPSESSID": "as2njthf17ji2r8rhevsepjt99"}

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "dnt": "1",
        "origin": "https://akniga.org",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": url,
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        # "x-requested-with": "XMLHttpRequest",
        # 'cookie': '__ddg1_=DKwhVnuVtTvgXGB61LRN; PHPSESSID=as2njthf17ji2r8rhevsepjt99; a_ismobile=0; a_skin=acl; a_is_auth=1; _ga=GA1.1.772476125.1740810676; _ym_uid=1740810676126575635; _ym_isad=1; _ga_77BK1YJVXT=GS1.1.1740810675.1.0.1740810691.0.0.0; __ddg9_=217.25.223.209; _ym_d=1740839776; __ddg10_=1740839777; __ddg8_=maKJaoGqbnlCaZ7r',
    }

    data = {
        "bid": bid,
        "hash": '{"ct":"zdByQ00xfxYb+OLdqI/aE3MMP3Anx/gS/0PXqsrGcOkxFugEXw2oZIXLxRV9cZsW","iv":"ef3b0f7b7ece94f87c6ea75c1bc7604f","s":"3a6c32c78d15b92e"}',
        "security_ls_key": "2e7b9e88a153fe407809c78d27a0e6d0",
    }

    resp = requests.post(
        f"https://akniga.org/ajax/b/{bid}", data=data, headers=headers, cookies=cookies
    )
    print(resp.ok)
    print(resp.content)
    # if resp.ok:
    #     pass


if __name__ == "__main__":

    book_url = "https://akniga.org/glubina-pogruzhenie-62-e"
    get_m3u_url(book_url)
    # session = get_session()
    # bid, security_ls_key, phpsessid = get_bid_and_key(session, book_url)
    # print(bid)
    # get_book_ajax(bid, phpsessid, book_url)
