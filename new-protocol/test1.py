import requests
import json


def get(url, bid):
    cookies = {
        # '__ddg1_': 'DKwhVnuVtTvgXGB61LRN',
        "PHPSESSID": "as2njthf17ji2r8rhevsepjt99",
        # 'a_ismobile': '0',
        # 'a_skin': 'acl',
        # 'a_is_auth': '1',
        # '_ga': 'GA1.1.772476125.1740810676',
        # '_ym_uid': '1740810676126575635',
        # '_ym_isad': '1',
        # '_ga_77BK1YJVXT': 'GS1.1.1740810675.1.0.1740810691.0.0.0',
        # '__ddg9_': '217.25.223.209',
        # '_ym_d': '1740839776',
        # '__ddg10_': '1740839777',
        # '__ddg8_': 'maKJaoGqbnlCaZ7r',
    }

    headers = {
        # "accept": "application/json, text/javascript, */*; q=0.01",
        # "accept-language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
        # "cache-control": "no-cache",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        # "dnt": "1",
        "origin": "https://akniga.org",
        # "pragma": "no-cache",
        # "priority": "u=1, i",
        # "referer": url,
        # "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        # "sec-ch-ua-mobile": "?0",
        # "sec-ch-ua-platform": '"Linux"',
        # "sec-fetch-dest": "empty",
        # "sec-fetch-mode": "cors",
        # "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        # "x-requested-with": "XMLHttpRequest",
        # 'cookie': '__ddg1_=DKwhVnuVtTvgXGB61LRN; PHPSESSID=as2njthf17ji2r8rhevsepjt99; a_ismobile=0; a_skin=acl; a_is_auth=1; _ga=GA1.1.772476125.1740810676; _ym_uid=1740810676126575635; _ym_isad=1; _ga_77BK1YJVXT=GS1.1.1740810675.1.0.1740810691.0.0.0; __ddg9_=217.25.223.209; _ym_d=1740839776; __ddg10_=1740839777; __ddg8_=maKJaoGqbnlCaZ7r',
    }

    data = {
        "bid": bid,
        "hash": '{"ct":"zdByQ00xfxYb+OLdqI/aE3MMP3Anx/gS/0PXqsrGcOkxFugEXw2oZIXLxRV9cZsW","iv":"ef3b0f7b7ece94f87c6ea75c1bc7604f","s":"3a6c32c78d15b92e"}',
        "security_ls_key": "2e7b9e88a153fe407809c78d27a0e6d0",
    }

    response = requests.post(
        f"https://akniga.org/ajax/b/{bid}", cookies=cookies, headers=headers, data=data
    )
    print(response.ok)
    print(response.content)


# get("https://akniga.org/lem-stanislav-zvezdnye-dnevniki-iyona-tihogo-tom-2", "97392")
get("https://akniga.org/glubina-pogruzhenie-62-e", "97346")
# bid = "97346"  97392
