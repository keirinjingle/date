#!/bin/bash
set -e

# パスの設定（新サーバー用）
ROOT_DIR="/home/yusuke/keirin/keirin_day_date"
REPO_DIR="/mnt/next/keirin_project_repo"
DATA_DIR="/mnt/next/keirin_day_date/date"
TODAY=$(date +"%Y%m%d")
WEBHOOK_URL="https://discord.com/api/webhooks/1360747161519657160/wJvC1HBtFw1gFYPq3-rC5Ym3bkDAYRVwUGWas0kZq9UGU3UNp-Qf4mrjZC2juXv7j6MQ"  # ← あなたのWebhook URLに変更

# Discord通知用関数
send_discord() {
  local msg="$1"
  curl -H "Content-Type: application/json" \
       -X POST \
       -d "{\"content\": \"$msg\"}" \
       "$WEBHOOK_URL"
}

# 1. スクレイピング実行
cd "$ROOT_DIR"
if ! /usr/bin/python3 scrape_keirin_race_data.py; then
  send_discord "⚠️ scrape_keirin_race_data.py でエラーが発生しました。"
  exit 1
fi

# 2. JSON変換
if ! /usr/bin/python3 convert_keirin_csv_to_json.py; then
  send_discord "⚠️ convert_keirin_csv_to_json.py でエラーが発生しました。"
  exit 1
fi

# 3. GitHubへアップロード（コピーせずにそのまま）
cd "$DATA_DIR"

# GitHubの最新内容を先に取り込む（rebase）
git pull origin main --rebase

# ファイル追加・コミット（変更がない場合はスキップ）
git add "keirin_race_list_${TODAY}.json"
git commit -m "Add race data for ${TODAY}" || true

# プッシュ実行
git push origin main
PUSH_STATUS=$?


# Discord通知
if [ $PUSH_STATUS -eq 0 ]; then
  send_discord "✅ ${TODAY} のデータ処理完了（GitHub：push済または変更なし）"
else
  send_discord "❌ GitHubへのpushに失敗しました。"
  exit 1
fi

# 4. 古いファイルの整理（clean_old_keirin_data.sh の実行）
if bash "$ROOT_DIR/clean_old_keirin_data.sh"; then
  send_discord "🗂 古いファイルの整理を完了しました。"
else
  send_discord "⚠️ clean_old_keirin_data.sh の実行に失敗しました。"
fi
