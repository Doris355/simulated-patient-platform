import gradio as gr
import json
import os
from datetime import datetime
from fpdf import FPDF
from huggingface_hub import snapshot_download
from llama_cpp import Llama

# ===== 參數設置 =====
ROLES_PATH = "roles.json"
LOGS_DIR = "logs"
GGUF_MODEL_REPO = "TheBloke/MythoMax-L2-13B-GGUF"
GGUF_FILENAME = "mythomax-l2-13b.Q4_K_M.gguf"

# ===== 初始化目錄 =====
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# ===== 載入角色 =====
def load_roles():
    if not os.path.exists(ROLES_PATH):
        return []
    with open(ROLES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

roles = load_roles()
role_names = [r['name'] for r in roles] if roles else []

# ===== 模型初始化 =====
llm = None
def init
