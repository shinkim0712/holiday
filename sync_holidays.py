import os
import requests
from notion_client import Client

NOTION_TOKEN = os.environ["NOTION_TOKEN"]
DATABASE_ID = os.environ["NOTION_DATABASE_ID"]
DATA_GO_KR_KEY = os.environ["DATA_GO_KR_KEY"]  # Decoding 키
YEAR = int(os.environ.get("TARGET_YEAR", "2026"))

notion = Client(auth=NOTION_TOKEN)


def get_holidays(year):
    holidays = []
    url = "http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo"
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
    result = notion.databases.query(
        database_id=DATABASE_ID,
        filter={"property": "구분", "select": {"equals": "공휴일"}},
    )
    return {
        r["properties"]["날짜"]["date"]["start"]
        for r in result["results"]
        if r["properties"]["날짜"]["date"]
    }


def main():
    already = existing_dates()
    for h in get_holidays(YEAR):
        if h["date"] in already:
            print(f"스킵(이미 있음): {h['date']} {h['name']}")
            continue
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "이름": {"title": [{"text": {"content": h["name"]}}]},
                "날짜": {"date": {"start": h["date"]}},
                "구분": {"select": {"name": "공휴일"}},
            },
        )
        print(f"추가됨: {h['date']} {h['name']}")


if __name__ == "__main__":
    main()
