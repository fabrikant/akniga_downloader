import requests

cookies = {
    # '__ddg8_': 'ouzpkDxjjBBlnnit',
    # '__ddg10_': '1740921226',
    # '__ddg9_': '217.25.223.209',
    # '__ddg1_': '6HIeHInE07wYk9arkUBZ',
    'PHPSESSID': '4bocdrparpekuq6fc21sd9el24',
    # 'a_ismobile': '0',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:135.0) Gecko/20100101 Firefox/135.0',
    # 'Accept': 'application/json, text/javascript, */*; q=0.01',
    # 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'https://akniga.org',
    # 'DNT': '1',
    # 'Sec-GPC': '1',
    # 'Connection': 'keep-alive',
    # 'Referer': 'https://akniga.org/glubina-pogruzhenie-62-e',
    # 'Cookie': '__ddg8_=ouzpkDxjjBBlnnit; __ddg10_=1740921226; __ddg9_=217.25.223.209; __ddg1_=6HIeHInE07wYk9arkUBZ; PHPSESSID=4bocdrparpekuq6fc21sd9el24; a_ismobile=0',
    # 'Sec-Fetch-Dest': 'empty',
    # 'Sec-Fetch-Mode': 'cors',
    # 'Sec-Fetch-Site': 'same-origin',
    # 'Pragma': 'no-cache',
    # 'Cache-Control': 'no-cache',
    # Requests doesn't support trailers
    # 'TE': 'trailers',
}

data = {
    'bid': '97346',
    'hash': '{"ct":"p0uv6O/dAa6XU/rAS4cOQeD8I1EJMs/CIjT8IsvMVeQpjMa8TuitqnP+3LYfjCKv","iv":"4421a792bd9a7428f7cc41bf93530d7a","s":"7ff766f1d0445676"}',
    'security_ls_key': '4745d8c5be191840af2869acca790237',
}

resp = requests.post('https://akniga.org/ajax/b/97346', cookies=cookies, headers=headers, data=data)
print(resp.status_code)
print(resp.content)