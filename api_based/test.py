import requests
import time
from datetime import datetime
import json

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

def get_cookie(path: str):
    """
    Get the cookie value from the specified path.
    """
    global USER_COOKIE, ROLE_TOKEN
    with open(path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    if 'ak-user-tw' not in cookies:
        raise ValueError("Cookie 'ak-user-tw' not found in the cookie file.")
    USER_COOKIE = cookies['ak-user-tw']
    if 'X-Role-Token' not in cookies:
        raise ValueError("Cookie 'X-Role-Token' not found in the cookie file.")
    ROLE_TOKEN = cookies['X-Role-Token']

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

def merge_logs(records, previous_records):
    cursor_now = 0
    cursor_prev = 0
    while cursor_now < len(records) and cursor_prev < len(previous_records):
        cursor_now_bak = cursor_now
        cursor_prev_bak = cursor_prev
        # Find the next cluster (records with the same "time")
        cluster_now = [records[cursor_now]]
        cluster_prev = [previous_records[cursor_prev]]
        # If the time is the same, put into the same cluster
        cursor_now += 1
        cursor_prev += 1
        while cursor_now < len(records) and records[cursor_now]["ts"] == cluster_now[0]["ts"]:
            cluster_now.append(records[cursor_now])
            cursor_now += 1
        while cursor_prev < len(previous_records) and previous_records[cursor_prev]["ts"] == cluster_prev[0]["ts"]:
            cluster_prev.append(previous_records[cursor_prev])
            cursor_prev += 1
        # Compare the two clusters
        if len(cluster_now) == 0 or len(cluster_prev) == 0:
            break
        elif cluster_now[0]["ts"] == cluster_prev[0]["ts"]:
            # Check if the number of records in the clusters is too large
            if len(cluster_now) > 10 or len(cluster_prev) > 10:
                print(f"Warning: too many records in the same time cluster, {len(cluster_now)} vs {len(cluster_prev)}, please check manually.")
            # If the time is the same, compare the records
            if len(cluster_now) == len(cluster_prev):
                # keep the new records
                for i in range(len(cluster_prev)):
                    # keep remove previous_records[cursor_prev_bak] for len(cluster_prec) times
                    if previous_records[cursor_prev_bak]["charName"] == cluster_now[i]["charName"]:
                        previous_records.remove(previous_records[cursor_prev_bak])
                        # no need to cursor_prev_bak += 1 since the next record will come to the same place
                    else:
                        # unexpected behavior, warning
                        print(f"Warning: oprator name not matching, {previous_records[cursor_prev_bak]['charName']} vs {cluster_now[i]['charName']}")
                        previous_records.remove(previous_records[cursor_prev_bak])
                # recover cursor_prev so that it points to the next record
                cursor_prev = cursor_prev_bak
            else:
                # unexpected behavior, warning
                print(f"Warning: records length not matching, {len(cluster_now)} vs {len(cluster_prev)}, keep the longer one")
                if len(cluster_now) > len(cluster_prev):
                    # keep the new records
                    for i in range(len(cluster_prev)):
                        previous_records.remove(previous_records[cursor_prev_bak])
                        # recover cursor_prev so that it points to the next record
                        cursor_prev = cursor_prev_bak
                else:
                    # keep the previous records
                    for i in range(len(cluster_now)):
                        records.remove(records[cursor_now_bak])
                        # recover cursor_now so that it points to the next record
                        cursor_now = cursor_now_bak
                break
        else: # Time not matching, recover cursor_prev so that cursor_now can chase up
            cursor_prev = cursor_prev_bak
    return records + previous_records

if __name__ == '__main__':
    # get_cookie('../../private.json')  # development mode
    uid = get_uid()
    session = set_session()
    logs = fetch_all_logs(uid, session)
    print(f"{len(logs)} logs fetched")

    for item in logs:
        item['time'] = datetime.fromtimestamp(item['ts']).strftime('%Y/%m/%d %H:%M:%S')

    try:
        with open('visit_logs.json', 'r', encoding='utf-8') as f:
            previous_records = json.load(f)
        logs = merge_logs(logs, previous_records)
    except FileNotFoundError:
        print("visit_logs.json not found, creating a new one.")

    with open('visit_logs.json', 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

# Example output format:
#   {
#     "poolId": "LIMITED_TC_33_0_1",
#     "poolName": "",
#     "charId": "char_109_fmout",
#     "charName": "遠山",
#     "rarity": 3, # rarity = star level - 1
#     "isNew": false,
#     "ts": 1751173089,
#     "time": "2025/06/29 12:58:09"
#   },