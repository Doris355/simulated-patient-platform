#!/bin/bash
set -e

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"

git add roles.json

if ! git diff --staged --quiet; then
  echo "偵測到檔案變更，正在提交與推送..."

  git commit -m "Auto update roles.json from Google Drive"
  git pull --rebase origin main || true
  git push

  git remote add hf https://user:$HF_TOKEN@huggingface.co/spaces/wan-yun/simulated-patient-chat || true
  git push hf HEAD:main --force
else
  echo "沒有檔案變更，跳過推送。"
fi
