#!/bin/bash
set -e  # 發生錯誤就終止腳本

# 設定 Git 使用者資訊
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

# 加入 roles.json 到 Git 暫存區
git add roles.json

# 判斷是否有變更再提交與推送
if ! git diff --staged --quiet; then
  echo "偵測到檔案變更，正在提交與推送..."

  git commit -m "Auto update roles.json from Google Drive"

  # 避免 remote main 分支快轉錯誤
  git pull --rebase origin main || true
  git push

  # 新增 Hugging Face 遠端（已存在就跳過）
  git remote add hf https://user:$HF_TOKEN_
