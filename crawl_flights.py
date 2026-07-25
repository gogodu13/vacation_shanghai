"""
항공권 크롤러 - 네이버 항공
조건: 가는편 06-09시, 오는편 17시 이후
날짜: 7/25~7/27 출발, 7/28~8/1 도착 (3박4일~5박6일)
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time
import os
import json

BASE_URL = "https://flight.naver.com"
SAVE_DIR = "/Users/gogodu/claude/projects/summer_vacation_2026/pages"
os.makedirs(SAVE_DIR, exist_ok=True)

# 검색할 날짜 조합 (출발, 도착, 박수)
DATE_COMBOS = [
    ("20260725", "20260728", "3박4일 토~화"),
    ("20260726", "20260729", "3박4일 일~수"),
    ("20260727", "20260730", "3박4일 월~목"),
    ("20260728", "20260731", "3박4일 화~금"),
    ("20260729", "20260801", "3박4일 수~토"),
]

DESTINATIONS = [
    {"name": "오사카", "dep": "ICN", "arr": "KIX"},
    {"name": "타이베이", "dep": "ICN", "arr": "TPE"},
    {"name": "마닐라", "dep": "ICN", "arr": "MNL"},
    {"name": "홍콩", "dep": "ICN", "arr": "HKG"},
    {"name": "광저우", "dep": "ICN", "arr": "CAN"},
    {"name": "쿠알라룸푸르", "dep": "ICN", "arr": "KUL"},
]

# 시간 필터 조건
ARR_DEST_BY = 14   # 여행지 도착 ≤ 14:00 (오전~점심)
RET_FROM = 17      # 귀국편 출발 ≥ 17:00


def get_driver():
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36")
    return webdriver.Chrome(options=opts)


def wait_and_get_html(driver, url, cache_path):
    if os.path.exists(cache_path):
        print(f"    (캐시 사용)")
        with open(cache_path, encoding="utf-8") as f:
            return f.read()

    driver.get(url)
    wait = WebDriverWait(driver, 40)
    try:
        wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "[class*='loading_bar']")))
    except Exception:
        pass
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='ItemPriceList']")))
    except Exception:
        pass
    time.sleep(3)

    html = driver.page_source
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)
    return html


def to_minutes(time_str):
    """'07:30' → 450"""
    try:
        h, m = time_str.strip().split(":")
        return int(h) * 60 + int(m)
    except Exception:
        return -1


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
        price_str = f"{price_won:,}원" if price_won else ""

        if airline and legs:
            results.append({
                "airline": airline,
                "legs": legs,
                "price": price_str,
                "price_won": price_won,
            })

    return results


def filter_by_time(flights):
    """인천 출발 ≤ 12:00 & 여행지 도착 ≤ 14:00 & 귀국편 출발 ≥ 17:00
    (경유+야간비행으로 오전 도착하는 케이스 제거)"""
    matched = []
    for f in flights:
        legs = f["legs"]
        if len(legs) < 2:
            continue
        dep_icn = to_minutes(legs[0]["dep"])
        arr_dest = to_minutes(legs[0]["arr"])
        ret_dep = to_minutes(legs[1]["dep"])
        if dep_icn <= 12 * 60 and arr_dest <= ARR_DEST_BY * 60 and ret_dep >= RET_FROM * 60:
            matched.append(f)
    return matched


def filter_direct_only(flights):
    """직항만 필터 (시간 제한 없음)"""
    matched = []
    for f in flights:
        legs = f["legs"]
        if len(legs) < 2:
            continue
        go_info = legs[0].get("info", "")
        ret_info = legs[1].get("info", "")
        if "직항" in go_info and "직항" in ret_info:
            matched.append(f)
    return matched


def print_flights(flights, label):
    print(f"\n  [{label}] 조건 맞는 항공편: {len(flights)}개")
    flights.sort(key=lambda f: f["price_won"] if f["price_won"] else 9999999)
    for i, f in enumerate(flights[:5], 1):
        legs = f["legs"]
        go = f"{legs[0]['dep_code']} {legs[0]['dep']} → {legs[0]['arr_code']} {legs[0]['arr']}  ({legs[0]['info']})"
        ret = f"{legs[1]['dep_code']} {legs[1]['dep']} → {legs[1]['arr_code']} {legs[1]['arr']}  ({legs[1]['info']})"
        print(f"    {i}. {f['airline']}  {f['price']}")
        print(f"       가는편: {go}")
        print(f"       오는편: {ret}")
    return flights


def main():
    driver = get_driver()
    all_good = []
    results_by_dest = {}  # dest_name -> list of matched flights with metadata

    try:
        for dest in DESTINATIONS:
            print(f"\n{'='*55}")
            print(f"★ {dest['name']} ({dest['arr']})")
            results_by_dest[dest["name"]] = []

            for dep_date, ret_date, label in DATE_COMBOS:
                url = (
                    f"{BASE_URL}/flights/international/"
                    f"{dest['dep']}-{dest['arr']}-{dep_date}/"
                    f"{dest['arr']}-{dest['dep']}-{ret_date}"
                    f"?adult=1&fareType=Y"
                )
                cache = f"{SAVE_DIR}/{dest['name']}_{dep_date}_{ret_date}.html"
                print(f"\n  {label} ({dep_date[4:6]}/{dep_date[6:]} → {ret_date[4:6]}/{ret_date[6:]})")
                html = wait_and_get_html(driver, url, cache)
                flights = parse_flights(html)
                if dest.get("direct_only"):
                    matched = filter_direct_only(flights)
                else:
                    matched = filter_by_time(flights)
                printed = print_flights(matched, label)
                for f in printed:
                    f["dest"] = dest["name"]
                    f["dep_code"] = dest["dep"]
                    f["arr_code"] = dest["arr"]
                    f["period"] = label
                    f["dep_date"] = dep_date
                    f["ret_date"] = ret_date
                    naver_url = (
                        f"{BASE_URL}/flights/international/"
                        f"{dest['dep']}-{dest['arr']}-{dep_date}/"
                        f"{dest['arr']}-{dest['dep']}-{ret_date}"
                        f"?adult=1&fareType=Y"
                    )
                    sky_url = (
                        f"https://www.skyscanner.co.kr/transport/flights/{dest['dep']}/{dest['arr']}/"
                        f"{dep_date[2:]}/{ret_date[2:]}/?adults=1&cabinclass=economy"
                    )
                    f["naver_url"] = naver_url
                    f["sky_url"] = sky_url
                    results_by_dest[dest["name"]].append(f)
                all_good.extend(printed)

    finally:
        driver.quit()

    # JSON으로 저장
    json_path = f"{SAVE_DIR}/../results.json"
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(results_by_dest, fp, ensure_ascii=False, indent=2)
    print(f"\n결과 저장: {json_path}")

    # 전체 최저가 TOP5
    print(f"\n{'='*55}")
    print("★ 전체 조건 충족 최저가 TOP 5")
    print(f"{'='*55}")
    all_good.sort(key=lambda f: f["price_won"] if f["price_won"] else 9999999)
    seen = set()
    rank = 1
    for f in all_good:
        key = (f["dest"], f["airline"], f["legs"][0]["dep"], f["legs"][1]["dep"])
        if key in seen:
            continue
        seen.add(key)
        legs = f["legs"]
        print(f"  {rank}. [{f['dest']} / {f['period']}] {f['airline']}  {f['price']}")
        print(f"     가는편: {legs[0]['dep_code']} {legs[0]['dep']} → {legs[0]['arr_code']} {legs[0]['arr']}  ({legs[0]['info']})")
        print(f"     오는편: {legs[1]['dep_code']} {legs[1]['dep']} → {legs[1]['arr_code']} {legs[1]['arr']}  ({legs[1]['info']})")
        rank += 1
        if rank > 5:
            break


if __name__ == "__main__":
    main()
