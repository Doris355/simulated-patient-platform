import gradio as gr
import json
import os

def load_roles():
    if not os.path.exists("roles.json"):
        return [{"error": "找不到 roles.json"}]
    with open("roles.json", "r", encoding="utf-8") as f:
        return json.load(f)

roles = load_roles()

def list_roles():
    if isinstance(roles, dict) and "error" in roles[0]:
        return "❌ 錯誤：" + roles[0]["error"]
    return "\n\n".join(
        f"🧑‍⚕️ {r['name']}（{r['age']}歲, {r['gender']}）\n職業：{r['occupation']}\n描述：{r['description']}"
        for r in roles
    )

demo = gr.Interface(
    fn=list_roles,
    inputs=[],
    outputs="text",
    title="模擬病人角色清單",
    description="從 roles.json 讀取的模擬病人角色"
)

if __name__ == "__main__":
    demo.launch()
