"""
캐시된 HTML 재파싱 — 시간 필터 없음, 직항 우선 정렬
"""
from bs4 import BeautifulSoup
import re
import os

SAVE_DIR = "/Users/gogodu/claude/projects/summer_vacation_2026/pages"
BASE_URL = "https://flight.naver.com"

DESTINATIONS = [
    {"name": "후쿠오카", "dep": "ICN", "arr": "FUK"},
    {"name": "오사카",   "dep": "ICN", "arr": "KIX"},
    {"name": "도쿄",    "dep": "ICN", "arr": "NRT"},
    {"name": "삿포로",  "dep": "ICN", "arr": "CTS"},
    {"name": "타이베이","dep": "ICN", "arr": "TPE"},
    {"name": "홍콩",    "dep": "ICN", "arr": "HKG"},
    {"name": "상하이",  "dep": "ICN", "arr": "PVG"},
    {"name": "충칭",    "dep": "ICN", "arr": "CKG"},
    {"name": "광저우",  "dep": "ICN", "arr": "CAN"},
    {"name": "하노이",  "dep": "ICN", "arr": "HAN"},
    {"name": "나트랑",  "dep": "ICN", "arr": "CXR"},
    {"name": "방콕",    "dep": "ICN", "arr": "BKK"},
    {"name": "마닐라",  "dep": "ICN", "arr": "MNL"},
    {"name": "쿠알라룸푸르", "dep": "ICN", "arr": "KUL"},
]

DATE_COMBOS = [
    ("20260725", "20260728", "7/25~7/28"),
    ("20260726", "20260729", "7/26~7/29"),
    ("20260727", "20260730", "7/27~7/30"),
    ("20260728", "20260731", "7/28~7/31"),
    ("20260729", "20260801", "7/29~8/1"),
]


def extract_price(price_block):
    promoted = price_block.select_one("[class*='item_promoted'] [class*='item_num']")
    if not promoted:
        promoted = price_block.select_one("[class*='item_num']")
    if promoted:
        num = re.sub(r"[^\d]", "", promoted.text.strip())
        return int(num) if num else 0
    return 0


def parse_flights(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for inner in soup.select("[class*='combination_inner']"):
        card = inner.select_one("[class*='combination_item']")
        price_block = inner.select_one("[class*='ItemPriceList']")
        if not card:
            continue
        airline_el = card.select_one("[class*='airline_name']")
        airline = airline_el.text.strip() if airline_el else ""
        times = card.select("[class*='route_time']")
        codes = card.select("[class*='route_code']")
        details = card.select("[class*='route_details']")
        legs = []
        for i in range(0, min(len(times), len(codes)), 2):
            dep_t = times[i].text.strip() if i < len(times) else ""
            arr_t = times[i+1].text.strip() if i+1 < len(times) else ""
            dep_c = codes[i].text.strip() if i < len(codes) else ""
            arr_c = codes[i+1].text.strip() if i+1 < len(codes) else ""
            info = details[i//2].text.strip() if i//2 < len(details) else ""
            legs.append({"dep": dep_t, "arr": arr_t, "dep_code": dep_c, "arr_code": arr_c, "info": info})
        price_won = extract_price(price_block) if price_block else 0
        if airline and legs and price_won:
            results.append({"airline": airline, "legs": legs, "price_won": price_won})
    return results


def is_direct(flight):
    legs = flight["legs"]
    if len(legs) < 2:
        return False
    return "직항" in legs[0].get("info", "") and "직항" in legs[1].get("info", "")


def main():
    # 도시별 최저가 (직항/전체) 수집
    summary = []  # {name, arr, price, airline, go, ret, date, direct}

    for dest in DESTINATIONS:
        best_direct = None
        best_any = None

        for dep_date, ret_date, label in DATE_COMBOS:
            cache = f"{SAVE_DIR}/{dest['name']}_{dep_date}_{ret_date}.html"
            if not os.path.exists(cache):
                continue
            with open(cache, encoding="utf-8") as f:
                html = f.read()
            flights = parse_flights(html)
            for fl in flights:
                if len(fl["legs"]) < 2:
                    continue
                fl["date"] = label
                if is_direct(fl):
                    if best_direct is None or fl["price_won"] < best_direct["price_won"]:
                        best_direct = fl
                if best_any is None or fl["price_won"] < best_any["price_won"]:
                    best_any = fl

        # 직항 최저가 우선, 없으면 전체 최저가
        best = best_direct or best_any
        if best:
            legs = best["legs"]
            go = f"{legs[0]['dep']}→{legs[0]['arr']} ({legs[0]['info']})"
            ret = f"{legs[1]['dep']}→{legs[1]['arr']} ({legs[1]['info']})"
            summary.append({
                "name": dest["name"],
                "arr": dest["arr"],
                "price": best["price_won"],
                "airline": best["airline"],
                "go": go,
                "ret": ret,
                "date": best["date"],
                "direct": is_direct(best),
            })

    summary.sort(key=lambda x: x["price"])

    print(f"\n{'='*65}")
    print(f"{'도시':<8} {'최저가':>10}  {'직항':^4}  {'일정':<12}  {'항공사'}")
    print(f"{'='*65}")
    for s in summary:
        tag = "직항" if s["direct"] else "경유"
        print(f"{s['name']:<8} {s['price']:>9,}원  {tag:^4}  {s['date']:<12}  {s['airline']}")
        print(f"         가는편: {s['go']}")
        print(f"         오는편: {s['ret']}")
        naver = (
            f"https://flight.naver.com/flights/international/"
            f"ICN-{s['arr']}-{s['date'][:4].replace('/','')}/"
        )
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
