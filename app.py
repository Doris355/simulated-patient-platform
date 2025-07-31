import gradio as gr
import json
import os
from datetime import datetime
from fpdf import FPDF
from huggingface_hub import snapshot_download
from llama_cpp import Llama

# === 路徑與模型設定 ===
ROLES_PATH = "roles.json"
LOGS_DIR = "logs"
GGUF_MODEL_REPO = "TheBloke/MythoMax-L2-13B-GGUF"
GGUF_FILENAME = "mythomax-l2-13b.Q4_K_M.gguf"

# === 準備 logs 資料夾 ===
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# === 載入角色 ===
def load_roles():
    if not os.path.exists(ROLES_PATH):
        return []
    with open(ROLES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

roles = load_roles()
role_names = [r["name"] for r in roles] if roles else []

# === 初始化 LLM 模型 ===
llm = None
def init_model():
    global llm
    if llm is None:
        model_dir = snapshot_download(
            repo_id=GGUF_MODEL_REPO,
            allow_patterns=GGUF_FILENAME,
            local_dir="models",
            local_dir_use_symlinks=False
        )
        model_path = os.path.join(model_dir, GGUF_FILENAME)
        llm = Llama(
            model_path=model_path,
            n_gpu_layers=-1,
            verbose=False
        )

# === 模擬病人回應 ===
def simulate_response(user_input, role_name):
    init_model()
    prompt = f"你現在是一位模擬病人（{role_name}）。請用病人語氣回答以下提問：{user_input}"
    output = llm(prompt, max_tokens=200)
    return output["choices"][0]["text"].strip()

# === 儲存對話紀錄 ===
def save_conversation(student_name, character, dialogue):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "character": character,
        "timestamp": timestamp,
        "dialogue": dialogue
    }
    filepath = f"{LOGS_DIR}/student_{student_name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# === 匯出 PDF ===
def export_dialogue_pdf(student_name):
    filepath = f"{LOGS_DIR}/student_{student_name}.json"
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    character = data.get("character", "未知角色")
    timestamp = data.get("timestamp", "無時間")
    dialogue = data.get("dialogue", [])
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"學生姓名：{student_name}")
    pdf.multi_cell(0, 10, f"模擬角色：{character}")
    pdf.multi_cell(0, 10, f"對話時間：{timestamp}")
    pdf.ln(5)
    for m in dialogue:
        role = "學生" if m["role"] == "student" else "模擬病人"
        text = f"{role}: {m['text']}"
        pdf.multi_cell(0, 10, text)
        pdf.ln(1)
    output_path = f"{LOGS_DIR}/{student_name}_dialogue.pdf"
    pdf.output(output_path)
    return output_path

# === 對話流程處理 ===
def chat(student_name, role_name, user_input, history):
    if not student_name:
        return history, "❌ 請輸入學生姓名"
    if not role_name:
        return history, "❌ 請選擇角色"
    history.append({"role": "student", "text": user_input})
    reply = simulate_response(user_input, role_name)
    history.append({"role": "ai", "text": reply})
    save_conversation(student_name, role_name, history)
    return history, ""

# === 顯示對話紀錄 ===
def display_chat(history):
    return "\n".join([
        f"👩‍🎓 {m['text']}" if m['role'] == "student" else f"🧑‍⚕️ {m['text']}"
        for m in history
    ])

# === 載入學生紀錄 ===
def load_student_history(student_name):
    filepath = f"{LOGS_DIR}/student_{student_name}.json"
    if not os.path.exists(filepath):
        return [], "⚠️ 找不到紀錄"
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("dialogue", []), "✅ 成功載入"

# === 顯示角色清單 ===
def list_roles():
    return "\n\n".join(
        f"🧑‍⚕️ {r['name']}（{r['age']}歲, {r['gender']}）\n職業：{r['occupation']}\n描述：{r['description']}"
        for r in roles
    )

# === Gradio 介面 ===
with gr.Blocks() as demo:
    gr.Markdown("# 🧠 模擬病人角色對話系統")

    with gr.Tab("🎓 學生模式"):
        student_name = gr.Textbox(label="學生姓名")
        role_select = gr.Dropdown(choices=role_names, label="選擇角色")
        chatbox = gr.Textbox(label="輸入問題", lines=2)
        chat_display = gr.Textbox(label="對話紀錄", lines=10)
        status = gr.Textbox(label="狀態", interactive=False)
        history_state = gr.State([])
        chat_btn = gr.Button("送出對話")
        chat_btn.click(chat, [student_name, role_select, chatbox, history_state], [history_state, status])
        chat_btn.click(display_chat, history_state, chat_display)

    with gr.Tab("👨‍🏫 教師模式"):
        student_list = gr.Textbox(label="輸入學生姓名以載入紀錄")
        teacher_display = gr.Textbox(label="對話紀錄內容", lines=20)
        load_btn = gr.Button("載入對話紀錄")
        download_btn = gr.Button("📄 導出為 PDF")
        file_output = gr.File(label="下載 PDF")
        hist_state = gr.State([])
        load_btn.click(load_student_history, student_list, [hist_state, teacher_display])
        download_btn.click(fn=export_dialogue_pdf, inputs=student_list, outputs=file_output)

    with gr.Tab("📚 角色總覽"):
        role_list = gr.Textbox(value=list_roles(), label="目前角色", lines=20)

if __name__ == "__main__":
    demo.launch()
