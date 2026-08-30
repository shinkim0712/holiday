import os
import requests

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
DATA_GO_KR_KEY = os.environ["DATA_GO_KR_KEY"]  # Decoding 키
YEAR = int(os.environ.get("TARGET_YEAR", "2026"))

NOTION_API = "https://api.notion.com/v1"
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def get_holidays(year):
    holidays = []
    url = "https://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
    for month in range(1, 13):
        params = {
            "serviceKey": DATA_GO_KR_KEY,
            "solYear": year,
            "solMonth": f"{month:02d}",
            "_type": "json",
            "numOfRows": 20,
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        body = res.json()["response"]["body"]
        if body["totalCount"] == 0:
            continue
        items = body["items"]["item"]
        if isinstance(items, dict):
            items = [items]
        for item in items:
            d = str(item["locdate"])
            holidays.append(
                {"name": item["dateName"], "date": f"{d[:4]}-{d[4:6]}-{d[6:]}"}
            )
    return holidays


def existing_dates():
    res = requests.post(
        f"{NOTION_API}/databases/{DATABASE_ID}/query",
        headers=NOTION_HEADERS,
        json={"filter": {"property": "구분", "select": {"equals": "공휴일"}}},
        timeout=10,
    )
    if not res.ok:
        print(f"Notion 오류 응답: {res.text}")
    res.raise_for_status()
    results = res.json()["results"]
    return {
        r["properties"]["날짜"]["date"]["start"]
        for r in results
        if r["properties"]["날짜"]["date"]
    }


def create_page(name, date):
    res = requests.post(
        f"{NOTION_API}/pages",
        headers=NOTION_HEADERS,
        json={
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "이름": {"title": [{"text": {"content": name}}]},
                "날짜": {"date": {"start": date}},
                "구분": {"select": {"name": "공휴일"}},
            },
        },
        timeout=10,
    )
    if not res.ok:
        print(f"Notion 오류 응답: {res.text}")
    res.raise_for_status()


def main():
    already = existing_dates()
    for h in get_holidays(YEAR):
        if h["date"] in already:
            print(f"스킵(이미 있음): {h['date']} {h['name']}")
            continue
        create_page(h["name"], h["date"])
        print(f"추가됨: {h['date']} {h['name']}")


if __name__ == "__main__":
    main()
