import requests
import time
from datetime import datetime

'''
You can use this script to fetch your visit logs from the Arknights TXWY API.
After logging in to the https://ak.gryphline.com/user/visit, you can open the browser's developer tools,
go to the "Application" tab, and find the "Cookies" section to get your `ak-user-tw` cookie.
After that, go to the "Console" tab and run the following command to get your `X-Role-Token`:
```javascript
console.log(JSON.parse(window.localStorage.ONE_ACCOUNT_ROLE_META)['token']);
```
You can then copy the value and paste it into the `ROLE_TOKEN` variable below.
Make sure to replace the `USER_COOKIE` and `ROLE_TOKEN` variables with your own values.
'''

# ========= Please enter the following configuration=========
USER_COOKIE = 'your ak-user-tw cookie here'
ROLE_TOKEN = 'your X-Role-Token here'
# ===========================================================


def get_uid():
    info_session = requests.Session()
    info_session.headers.update({
        'X-Role-Token': ROLE_TOKEN,
    })
    info_session.cookies.update({
        'cookiePref': 'all',
        'ak-user-tw': USER_COOKIE,
    })
    url = 'https://ak.gryphline.com/user/api/redeem/info'
    resp = info_session.get(url)
    resp.raise_for_status()
    js = resp.json()
    if js.get('code') != 0:
        raise RuntimeError(f"API 回傳 code={js.get('code')}")
    return js['data']['uid']

def set_session():
    session = requests.Session()
    session.headers.update({
        'Content-Type':       'application/json',
        'X-Role-Token':       ROLE_TOKEN,
    })
    session.cookies.update({
        'cookiePref': 'all',
        'ak-user-tw':  USER_COOKIE,
    })
    return session

def fetch_visit_log_page(uid: int,page: int):
    url = 'https://ak.gryphline.com/user/api/redeem/visitLog'
    payload = { 'uid': uid, 'page': page }
    resp = session.post(url, json=payload)
    resp.raise_for_status()
    js = resp.json()
    if js.get('code') != 0:
        raise RuntimeError(f"API code={js.get('code')}")
    return js['data']['list']

def fetch_all_logs(uid: int, session: requests.Session):
    all_logs = []
    page = 1
    while True:
        lst = fetch_visit_log_page(uid, page)
        if not lst:
            break
        all_logs.extend(lst)
        print(f"Page {page}: {len(lst)} logs fetched")
        page += 1
        time.sleep(0.1)
    return all_logs

if __name__ == '__main__':
    uid = get_uid()
    session = set_session()
    logs = fetch_all_logs(uid, session)
    print(f"{len(logs)} logs fetched")

    for item in logs:
        item['time'] = datetime.fromtimestamp(item['ts']).strftime('%Y/%m/%d %H:%M:%S')

    import json
    with open('[api]visit_logs.json', 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)