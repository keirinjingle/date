import csv
import json
import datetime
import os
from collections import defaultdict

today = datetime.datetime.now().strftime('%Y%m%d')
csv_filename = f"/mnt/next/keirin_data/keirin_race_list_{today}.csv"


# ✅ JSONを date フォルダに保存
output_dir = "/mnt/next/keirin_day_date/date"
os.makedirs(output_dir, exist_ok=True)
json_filename = os.path.join(output_dir, f"keirin_race_list_{today}.json")


# ネスト構造: {(venue, grade): [race_entry, ...]}
grouped = defaultdict(list)

with open(csv_filename, "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        venue = row["venue_name"]
        grade = row["grade"]

        race = {
            "race_number": int(row["race_no"].replace("R", "")),
            "start_time": row["start_time"],
            "closed_at": row["closed_at"],
            "url": row["url"],
            "players": row["players"].split(),
            "class_category": row["class_category"]
        }

        grouped[(venue, grade)].append(race)

# 出力形式に整形
final_output = []
for (venue, grade), races in grouped.items():
    final_output.append({
        "venue": venue,
        "grade": grade,
        "races": races
    })

# JSON出力
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print(f"✅ JSON出力完了: {json_filename}")
