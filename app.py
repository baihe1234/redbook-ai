import gradio as gr
import requests
import os
import json
from datetime import datetime

# ================== 配置 ==================
API_KEY = os.getenv("ZHIPU_API_KEY")

# 激活码存储文件
KEYS_FILE = "activated_keys.json"

def load_keys():
    if os.path.exists(KEYS_FILE):
        with open(KEYS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_keys(keys):
    with open(KEYS_FILE, 'w') as f:
        json.dump(keys, f)

ACTIVATED_KEYS = load_keys()

# ================== 激活码管理 ==================
def check_activation_code(code):
    if not code:
        return False
    keys = load_keys()
    return code in keys and keys[code].get("status", False)

def activate_code(code):
    if len(code) < 6:
        return False
    keys = load_keys()
    keys[code] = {"status": True, "activate_time": datetime.now().strftime("%Y-%m-%d %H:%M")}
    save_keys(keys)
    return True

# ================== 生成函数 ==================
def generate_note(theme, selling_point, keywords, style, activation_code):
    # 检查激活码
    if not activation_code or not check_activation_code(activation_code):
        return """⚠️ **请先购买后输入激活码使用**

💡 **购买终身使用：59元**
- 不限次数生成
- 永久有效
- 付款后自动获得激活码

👇 **点击下方「购买方式」Tab 购买**
付款后自动显示激活码，无需等待！"""
    
    if not theme or not selling_point:
        return "⚠️ 请输入产品主题和核心卖点！"
    
    system_prompt = """你是一个擅长写种草文案的博主，擅长写让用户忍不住收藏的内容。

要求：
1. 生成3个不同角度的版本
2. 每个版本包含：标题 + 正文 + 5个标签
3. 语气真实自然，像普通人在分享
4. 不要用"绝绝子""yyds"等烂大街词汇
5. 适当加emoji增加活泼感

输出格式：
【版本1】
标题：xxx
正文：xxx
标签：#xxx #xxx

【版本2】
标题：xxx
正文：xxx
标签：#xxx #xxx

【版本3】
标题：xxx
正文：xxx
标签：#xxx #xxx"""
    
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
        
        response = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/chat/completions", 
            headers=headers, 
            json=data, 
            timeout=90
        )
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content']
        return content
       
    except Exception as e:
        return f"生成失败: {str(e)}\n请稍后重试或联系我。"

# ================== 管理员功能 ==================
def admin_generate_code(admin_key, count=1):
    if admin_key != "baihe123":
        return "⚠️ 管理员密码错误"
    
    import random
    import string
    codes = []
    for _ in range(int(count)):
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        activate_code(code)
        codes.append(code)
    return f"✅ 生成的激活码：\n" + "\n".join(codes)

# ================== Gradio 界面 ==================
with gr.Blocks(title="AI文案笔记助手", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # ✨ AI爆款文案笔记生成器
    **输入激活码即可使用 · 59元终身买断 · 付款自动发码**
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # 主功能
            with gr.Tab("📝 生成笔记"):
                with gr.Row():
                    with gr.Column(scale=1):
                        theme = gr.Textbox(label="📌 产品/主题", placeholder="例：亚麻连衣裙、防晒霜...")
                        selling_point = gr.Textbox(label="🔥 核心卖点", lines=2, placeholder="例：显瘦遮胯、褶子不炸...")
                        keywords = gr.Textbox(label="🏷️ 补充关键词（可选）", placeholder="百搭 通勤 夏日")
                        style = gr.Dropdown(
                            ["温柔治愈", "干货分享", "情绪共鸣", "种草测评"], 
                            value="温柔治愈", 
                            label="🎨 风格"
                        )
                        activation_code = gr.Textbox(
                            label="🔑 激活码", 
                            placeholder="输入激活码后使用..."
                        )
                        btn = gr.Button("🚀 生成3版笔记", variant="primary", size="large")
                    
                    with gr.Column(scale=2):
                        output = gr.Textbox(label="📝 生成结果", lines=28)
            
            # 购买方式
            with gr.Tab("💳 购买方式"):
                gr.Markdown("""
                ### 🎉 终身买断 · 59元
                - ✅ 不限次数生成
                - ✅ 永久有效
                - ✅ 付款后自动获得激活码
                """)
                
                gr.HTML('''
                <div style="text-align:center; padding:20px;">
                    <a href="https://mbd.pub/你的商品链接" target="_blank">
                        <button style="background:#ff6b6b; color:white; font-size:24px; padding:15px 50px; border:none; border-radius:12px; cursor:pointer; box-shadow:0 4px 15px rgba(255,107,107,0.4);">
                            💰 立即购买（59元）
                        </button>
                    </a>
                    <p style="color:#999; margin-top:10px;">支持微信 / 支付宝 · 付款后自动显示激活码</p>
                </div>
                ''')
                
                gr.Markdown("""
                ---
                **📱 购买流程**：
                1. 点击上方按钮，跳转支付页面
                2. 微信/支付宝支付 59 元
                3. 页面自动显示激活码
                4. 复制激活码，回到本页面使用
                
                💬 有问题加微信：**hb17430659**
                """)
            
            # 管理员
            with gr.Tab("🔧 管理员"):
                gr.Markdown("### 生成激活码（批量导入发卡平台）")
                gr.Markdown("> 管理员密码：`baihe123`")
                admin_key = gr.Textbox(label="管理员密码", type="password")
                code_count = gr.Number(label="生成数量", value=10)
                admin_btn = gr.Button("生成")
                admin_output = gr.Textbox(label="结果", lines=10)
                admin_btn.click(admin_generate_code, inputs=[admin_key, code_count], outputs=admin_output)
    
    gr.Markdown("""
    ---
    **💡 提示**：卖点写得越具体，文案越自然真实
    """)

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("PORT", 7860)),  # 这行是关键
        share=False
    )