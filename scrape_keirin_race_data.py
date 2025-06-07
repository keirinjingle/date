import os
import csv
import time
import re  # ← ★これを追加
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup

# 会場IDマップ
keirin_venue_codes = {
    "函館": "11", "青森": "12", "いわき平": "13", "弥彦": "21", "前橋": "22", "取手": "23", "宇都宮": "24",
    "大宮": "25", "西武園": "26", "京王閣": "27", "立川": "28", "松戸": "31", "川崎": "34", "平塚": "35",
    "小田原": "36", "伊東": "37", "伊東温泉": "37", "静岡": "38", "名古屋": "42", "岐阜": "43", "大垣": "44",
    "豊橋": "45", "富山": "46", "松阪": "47", "四日市": "48", "福井": "51", "奈良": "53", "向日町": "54",
    "和歌山": "55", "岸和田": "56", "玉野": "61", "広島": "62", "防府": "63", "高松": "71", "小松島": "73",
    "高知": "74", "松山": "75", "小倉": "81", "久留米": "83", "武雄": "84", "佐世保": "85", "別府": "86",
    "熊本": "87"
}

# USB保存先ディレクトリ
os.makedirs("/mnt/next/keirin_data", exist_ok=True)
today = datetime.now().strftime('%Y%m%d')
csv_filename = f"/mnt/next/keirin_data/keirin_race_list_{today}.csv"



# CSV初期化
if not os.path.exists(csv_filename):
    with open(csv_filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "venue_name", "race_no", "start_time", "closed_at", "url", "players", "class_category", "grade"])

def create_driver():
    options = FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # 👇 geckodriver のパスを明示的に指定
    service = FirefoxService(executable_path="/usr/local/bin/geckodriver")  # ← あなたの環境に合わせて

    return webdriver.Firefox(service=service, options=options)

# Seleniumドライバ初期化
driver = create_driver()

# Netkeirinから会場一覧を取得
driver.get("https://keirin.netkeiba.com/race/")
time.sleep(3)
venue_elements = driver.find_elements(By.CSS_SELECTOR, "div.TodayRace_SlideBoxItem a.RaceCourse_List")
venue_names = [e.text.strip() for e in venue_elements]

print("✅ 本日開催中の会場一覧:")
for name in venue_names:
    print(" -", name)

# 各会場のレース情報を取得
for venue_name in venue_names:
    venue_id = keirin_venue_codes.get(venue_name)
    if not venue_id:
        print(f"⚠ 未定義の会場名: {venue_name}")
        continue

    for race_no_int in range(1, 13):
        race_id = f"{today}{venue_id.zfill(2)}{str(race_no_int).zfill(2)}"
        url = f"https://keirin.netkeiba.com/race/entry/?race_id={race_id}"

        driver.get(url)
        time.sleep(1.5)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        title = soup.title.text if soup.title else ""
        if "1970年01月01日" in title or "不明" in title:
            continue

        try:
            # 必須要素が存在するかチェック
            race_no_tag = soup.select_one("div.Race_Num span")
            race_data_tag = soup.select_one("div.Race_Data")
            class_tag = soup.select_one("div.Race_Name")

            if not race_no_tag or not race_data_tag or not class_tag:
                continue

            race_no = race_no_tag.text.strip()
            race_data = race_data_tag.text.strip()
            start_time = re.search(r"発走\s*([0-9:]+)", race_data).group(1)
            deadline = re.search(r"締切\s*([0-9:]+)", race_data).group(1)
            class_category = class_tag.text.strip()

            grade_tag = soup.select_one("span.Icon_GradeType")
            grade = grade_tag.text.strip() if grade_tag else "F2"

            # 選手名と車番を取得
            player_set = set()
            player_dict = {}
            for row in soup.select("tr.PlayerList"):
                car_no_tag = row.select_one("td[class*=Waku]")
                name_tag = row.select_one("td.Player_Info .PlayerName a")
                if car_no_tag and name_tag:
                    car_no = car_no_tag.text.strip()
                    name = name_tag.text.strip()
                    key = f"{car_no}{name}"
                    if key not in player_set:
                        player_set.add(key)
                        player_dict[int(car_no)] = key
            players = [player_dict[k] for k in sorted(player_dict.keys())]

            # CSV出力
            with open(csv_filename, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow([today, venue_name, race_no, start_time, deadline, url, " ".join(players), class_category, grade])
                print(f"✅ {venue_name} {race_no} 保存完了")

        except Exception as e:
            print(f"⚠ エラー: {url} / {e}")
            continue

driver.quit()
print(f"\n📄 全レース出力完了: {csv_filename}")
