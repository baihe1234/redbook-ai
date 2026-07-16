import gradio as gr
import requests
import os
from datetime import datetime

# ================== 配置 ==================
API_KEY = os.getenv("ZHIPU_API_KEY")  # 重要：从环境变量读取，不要写死！

# 简单激活码管理（买断制用） - 后期可换数据库
ACTIVATED_KEYS = {}  # {激活码: {"status": True, "activate_time": "..."} }

def check_activation_code(code):
    return code in ACTIVATED_KEYS and ACTIVATED_KEYS[code]["status"]

def activate_code(code):
    if len(code) < 8:  # 简单校验
        return False
    ACTIVATED_KEYS[code] = {"status": True, "activate_time": datetime.now().strftime("%Y-%m-%d")}
    return True

# ================== 生成函数 ==================
def generate_note(theme, selling_point, keywords, style, activation_code):
    if not activation_code or not check_activation_code(activation_code):
        return "⚠️ 请先完成支付并输入激活码。\n\n支付后我会给你激活码（终身使用）。"
    
    if not theme or not selling_point:
        return "⚠️ 请输入产品主题和核心卖点！"
    
    # 你原来的 system_prompt 和 user_prompt 保持不变...
    system_prompt = """你是一个在小红书有8万粉丝的真实穿搭博主..."""  # 保持你原来的
    
    user_prompt = f"""{system_prompt}
产品/主题：{theme}
核心卖点：{selling_point}
补充关键词：{keywords if keywords else '无'}
风格基调：{style}"""
    
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        }
        data = {
            "model": "glm-4-flash",
            "messages": [{"role": "user", "content": user_prompt}],
            "temperature": 0.95,
            "max_tokens": 4000
        }
        
        response = requests.post("https://open.bigmodel.cn/api/paas/v4/chat/completions", 
                               headers=headers, json=data, timeout=90)
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content
       
    except Exception as e:
        return f"生成失败: {str(e)}\n请稍后重试或联系我。"

# ================== Gradio 界面 ==================
with gr.Blocks(title="小红书AI笔记助手") as demo:
    gr.Markdown("""
    # ✨ 小红书AI爆款笔记生成器
    **学生党开发 · 一键生成3版真实种草文案**
    """)
    
    with gr.Tab("🎉 终身买断"):
        gr.Markdown("""
        ### 价格：**59元** 终身使用（不限次数）
        支付方式：微信转账 / 支付宝
        支付后联系我发截图 → 获得**终身激活码**
        """)
        activation_code = gr.Textbox(label="输入激活码（支付后获得）", placeholder="输入你的激活码...")
    
    with gr.Row():
        with gr.Column(scale=1):
            theme = gr.Textbox(label="📌 产品/主题", placeholder="例：亚麻连衣裙、防晒霜...")
            selling_point = gr.Textbox(label="🔥 核心卖点", lines=2, placeholder="例：显瘦遮胯、褶子不炸...")
            keywords = gr.Textbox(label="🏷️ 补充关键词（可选）", placeholder="百搭 通勤 夏日")
            style = gr.Dropdown(["温柔治愈", "干货分享", "情绪共鸣", "种草测评"], value="温柔治愈", label="🎨 风格")
            
            btn = gr.Button("🚀 生成3版笔记", variant="primary", size="large")
        
        with gr.Column(scale=2):
            output = gr.Textbox(label="📝 生成结果", lines=25)
    
    btn.click(
        generate_note, 
        inputs=[theme, selling_point, keywords, style, activation_code], 
        outputs=output
    )
    
    gr.Markdown("""
    ---
    **联系我获取激活码**：（放你的微信号）
    **使用建议**：卖点写得越具体，文案越自然真实。
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)