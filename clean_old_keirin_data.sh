#!/bin/bash

# ディレクトリ設定
ROOT_DIR="/home/yusuke/keirin/keirin_day_date"
ARCHIVE_DIR="$ROOT_DIR/date"

# フォルダがなければ作成
mkdir -p "$ARCHIVE_DIR"

# ----------------------------------
# ✅ 1. 3日以上前のCSV・JSONを date/ に移動
# ----------------------------------
# find "$ROOT_DIR" -maxdepth 1 -type f \( -name "keirin_race_list_*.csv" -o -name "keirin_race_list_*.json" \) -mtime +2 -exec mv {} "$ARCHIVE_DIR" \;

# ----------------------------------
# ✅ 2. 30日以上前のCSV・JSONを削除
# ----------------------------------
find "$ARCHIVE_DIR" -maxdepth 1 -type f \( -name "keirin_race_list_*.csv" -o -name "keirin_race_list_*.json" \) -mtime +30 -exec rm {} \;
