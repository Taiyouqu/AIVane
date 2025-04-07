import json
import base64
import os
import requests
import time
import traceback

# API相关配置
DOUBAN_API_KEY = os.environ.get("DOUBAN_API_KEY", "YOUR_DOUBAN_API_KEY")
DOUBAN_API_URL = os.environ.get("DOUBAN_API_URL", "https://ark.cn-beijing.volces.com/api/v3/chat/completions")
DOUBAN_MODEL_ID = os.environ.get("DOUBAN_MODEL_ID", "doubao-1.5-vision-pro-32k-250115")
USE_PROXY = False
PROXY_HTTP = "http://127.0.0.1:7890"
PROXY_HTTPS = "http://127.0.0.1:7890"

def encode_image_to_base64(image_path):
    """将图片转换为base64编码"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        print(f"图片编码失败: {e}")
        return None

def initialize_client():
    """初始化豆包API配置"""
    global DOUBAN_API_KEY, DOUBAN_API_URL, DOUBAN_MODEL_ID, USE_PROXY, PROXY_HTTP, PROXY_HTTPS
    
    # 尝试从配置文件加载
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                DOUBAN_API_KEY = config.get("douban_api_key", DOUBAN_API_KEY)
                DOUBAN_API_URL = config.get("douban_api_url", DOUBAN_API_URL)
                DOUBAN_MODEL_ID = config.get("douban_model_id", DOUBAN_MODEL_ID)
                USE_PROXY = config.get("use_proxy", USE_PROXY)
                PROXY_HTTP = config.get("proxy_http", PROXY_HTTP)
                PROXY_HTTPS = config.get("proxy_https", PROXY_HTTPS)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
    
    if not DOUBAN_API_KEY or DOUBAN_API_KEY == "YOUR_DOUBAN_API_KEY":
        print("豆包API密钥未配置")
        return False
    return True

def query_ai(task_description, screenshot_base64, ui_elements):
    """查询豆包大模型获取执行建议"""
    if not initialize_client():
        return None
            
    # 检查任务描述是否包含历史上下文
    has_history = "任务历史" in task_description
    
    # 构建基本提示词
    base_prompt = f"""分析以下移动设备截图和界面元素信息，提供执行指定任务的精确ADB操作指令：

任务：{task_description.split('任务历史')[0].strip() if has_history else task_description}

----- 页面分析 -----
• 当前页面：[描述当前页面类型与内容]
• 任务路径：[分析从当前页面到完成任务所需的导航路径]
• 匹配程度：[完全匹配/部分匹配/不匹配]

----- 执行策略 -----
[简述最优执行策略，3-5句话简明描述]
只分析当前界面要操作的命令 不要一次性,就把当前任务所有的命令都说完了
----- 常见场景处理指南 -----
1. 聊天应用发消息：
   - 先点击搜索栏 -> 输入好友名字 -> 点击搜索结果
   - 必须点击输入框 -> 输入消息 -> 点击发送按钮
   - 注意：每个步骤都必须单独执行，特别是点击输入框和输入文本不能合并

2. 浏览器搜索：
   - 先点击地址栏/搜索框 -> 输入关键词 -> 点击搜索/回车
   - 直接输入完整网址而不是先搜索再点击
   - 使用"adb shell input keyevent 66"执行回车操作

3. 表单填写：
   - 依次点击每个输入框 -> 输入内容 -> 点击提交按钮
   - 在需要Enter的场景必须添加keyevent 66命令

4. 应用切换：
   - 返回主页(keyevent 3) -> 点击目标应用图标

5. 社交软件查找联系人：
   - 直接使用搜索栏查找好友，不要一个个浏览
   - 顺序：点击搜索栏 -> 输入名字 -> 点击回车 -> 点击结果

6. 坐标使用规则：
   - 使用任务提供的坐标，不要自行猜测坐标值
   - 每个tap命令必须使用实际的X Y坐标值

7. 应用启动策略：
   - 首选使用"adb shell am start -n 包名/活动名"方式启动
   - 如果包名启动失败，使用以下备选策略：
     * 返回主页(keyevent 3)
     * 点击桌面搜索栏
     * 输入应用名称--->如果有多个名字相同的坐标的话，只点击app的坐标（这个你要结合图片还有xml一起分析），而不是app名字的网页搜索的坐标。
     * 点击回车(keyevent 66)
     * 点击搜索结果打开应用

8. 搜索结果不匹配处理：
   首先分析页面如果有搜索输入框，就按照方案1进行。
   - 方案1 - 清除并重新搜索：
     * 点击输入框全
     * 删除文本(keyevent 67) adb shell input keyevent 67 这个命令执行30次
     * 输入新的搜索内容
     * 点击回车重新搜索

   - 方案2 - 返回上一级重试：
     * 点击返回键(keyevent 4)
     * 重新选择正确的入口
     * 重新执行搜索流程
   - 当前界面与任务明显不符时，始终优先返回上一级

9.当 XML 中缺少目标元素坐标时，构建提示词需清晰包含以下关键信息以辅助 AI 分析预测：
    界面布局特征：说明布局方式（如垂直 / 水平线性排列、网格布局等）。
    已知元素信息：提供与目标元素关联的已知元素坐标、文本内容及特征。
    目标元素特征：
    文本内容（如 "蜜雪冰城 (东门大桥时…)"）；
    相对位置（如位于某已知元素上方 / 下方 / 左侧 / 右侧，或属于某类元素集合中的第几个）；
    显示特征（如是否水平 / 垂直居中、常见尺寸比例等）。
    布局逻辑提示：可提及常见 UI 设计规律（如元素间距均匀、对齐方式等）。
    示例："界面元素为垂直排列，已知'搜索结果'坐标为 [703, 519]，目标元素'蜜雪冰城 (东门大桥时…)'是店铺名称，位于'搜索结果'正下方，且同类店铺名称习惯水平居中，与上方元素间距约为屏幕高度的 15%。请依据常规布局逻辑推测其中心坐标。"

10.发送消息发送文本都用这个指令adb shell am broadcast -a ADB_INPUT_TEXT --es msg '文本内容'
   不要用adb shell input text "文本内容"
----- ADB命令注意事项 -----
⚠️ 输入文本前必须先点击输入框 - 这是最重要的规则！
⚠️ 不要合并点击和输入操作，它们必须是独立的两个命令
⚠️ 进入新界面后，先观察界面元素，找到输入框再操作
⚠️ 点击->输入->发送的操作顺序必须严格遵守
⚠️ 不要假设任何输入框已获得焦点，总是先点击
⚠️ 包名启动应用失败时，转用桌面搜索方式
⚠️ 搜索结果不符合预期时，要么清除重试，要么返回上一级

----- 命令格式要求 -----
你必须将所有ADB命令放在```shell```代码块内，格式如下示例：

```shell
# 方法1：尝试通过包名启动应用（首选方法）
adb shell am start -n com.android.browser/.BrowserActivity  #浏览器
adb shell am start -n com.tencent.mobileqq/.activity.SplashActivity #淘宝
adb shell am start -n com.taobao.taobao/com.taobao.tao.TBMainActivity #QQ

# 方法2：如果包名启动失败，使用桌面搜索方式
# 返回主页
adb shell input keyevent 3

# 点击搜索栏
adb shell input tap 500 100

# 点击回车搜索
adb shell input keyevent 66

# 搜索结果不匹配时的处理方法1：清除并重新搜索
# 删除文本 执行30次这个命令 清除输入框的内容的时候
adb shell input keyevent 67

# 输入新的关键词
adb shell am broadcast -a ADB_INPUT_TEXT --es msg '文本内容'

# 重新搜索
adb shell input keyevent 66

# 搜索结果不匹配时的处理方法2：返回上一级
adb shell input keyevent 4

# 核心任务操作
adb shell am broadcast -a ADB_INPUT_TEXT --es msg '文本内容'  # 输入内容
adb shell input swipe X1 Y1 X2 Y2 duration  # 滑动操作
adb shell input keyevent keycode  # 按键操作

# 点击回车搜索
adb shell input keyevent 66
```

**识别元素**
{json.dumps(ui_elements, ensure_ascii=False, indent=2)}"""

    # 添加任务历史上下文部分
    if has_history:
        history_part = task_description.split('任务历史:')[1].strip()
        base_prompt += f"""

**任务历史上下文**
{history_part}

请基于上述任务历史，分析当前界面，并提供下一步操作的ADB命令。
注意：只提供当前界面需要执行的命令，不要猜测后续步骤。"""

    # 添加操作预期和备选策略部分
    base_prompt += """

**操作结果预期**
- [详细描述执行上述指令后的预期状态和结果]

**备选策略**
- [如果主策略失败，提供备选方案，例如使用不同入口或搜索方式]

使用实际坐标值，确保指令逻辑清晰连贯，并考虑当前页面状态与目标任务的最短路径。

**格式检查**
1. 确保你的ADB命令都放在```shell```代码块内
2. 不要在代码块外写命令
3. 使用实际坐标值替换X Y
4. 删除无关的示例命令
5. 在输入文本前确保先点击输入框
"""

    try:
        print("正在发送请求到豆包大模型...")
        
        # 构建系统消息，增强连续性理解
        system_message = """你是一个专业的移动设备自动化助手，擅长分析UI和提供精确的ADB操作指令。

严格遵守以下规则：
1. 所有命令必须是有效的ADB命令，以"adb shell"开头
2. 所有命令必须放在```shell代码块内，不要在代码块外写命令
3. 只提供当前任务所需的具体操作，不要预测多步骤
4. 每个分析都专注于当前屏幕的状态
5. 在使用input text命令前，必须先使用input tap命令点击输入框
6. 输入框点击和文本输入必须是两个独立命令，不能合并
7. 输入文本后如需回车，必须使用"adb shell input keyevent 66"
8. 直接使用搜索栏查找联系人，不要一个个浏览好友列表
9. 使用任务提供的坐标，不要自行猜测坐标值
10. 如果通过包名启动应用失败，改用桌面搜索方式启动应用
11. 搜索结果与任务不符时，要么清除搜索栏重试，要么返回上一级

特别注意：
- 聊天场景必须遵循：点击搜索 -> 输入名字 -> 选择好友 -> 点击输入框 -> 输入消息 -> 点击发送
- 浏览器场景必须遵循：点击地址栏 -> 输入网址 -> 点击回车
- 输入任何文本前都必须先点击输入框
- 应用打开失败时准备备选方案：回到主页 -> 点击搜索 -> 输入应用名 -> 点击搜索结果
- 搜索界面与任务不符时：清除重新输入 或 返回上一级重新操作
"""
        
        # 构建请求数据
        data = {
            "model": DOUBAN_MODEL_ID,
            "messages": [
                {
                    "role": "system", 
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": base_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_base64}"
                            }
                        }
                    ]
                }
            ]
        }
        
        # 准备请求头
        headers = {
            "Authorization": f"Bearer {DOUBAN_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 准备代理
        proxies = None
        if USE_PROXY:
            proxies = {
                "http": PROXY_HTTP,
                "https": PROXY_HTTPS
            }
        
        # 计时开始
        start_time = time.time()
        
        # 发送请求
        response = requests.post(
            DOUBAN_API_URL, 
            headers=headers, 
            json=data, 
            proxies=proxies
        )
        response_data = response.json()
        
        # 检查响应并提取内容
        if response.status_code == 200 and "choices" in response_data and len(response_data["choices"]) > 0:
            content = response_data["choices"][0]["message"]["content"]
            
            # 计时结束
            end_time = time.time()
            print(f"豆包API响应时间: {end_time - start_time:.2f}秒")
            
            return content
        else:
            print(f"豆包API返回错误: {response_data}")
            return None
            
    except Exception as e:
        print(f"豆包API调用失败: {e}")
        traceback.print_exc() if 'traceback' in globals() else print(f"详细错误信息: {str(e)}")
        return None

def test_api_connection():
    """测试豆包API连接"""
    if not initialize_client():
        return False
            
    try:
        # 简单的API测试请求
        data = {
            "model": DOUBAN_MODEL_ID,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的移动设备自动化助手。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "测试连接"
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {DOUBAN_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # 准备代理
        proxies = None
        if USE_PROXY:
            proxies = {
                "http": PROXY_HTTP,
                "https": PROXY_HTTPS
            }
        
        response = requests.post(
            DOUBAN_API_URL, 
            headers=headers, 
            json=data,
            proxies=proxies
        )
        
        if response.status_code == 200:
            print("豆包API连接测试成功!")
            return True
        else:
            print(f"豆包API连接测试失败，状态码: {response.status_code}")
            print(f"错误详情: {response.text}")
            return False
            
    except Exception as e:
        print(f"豆包API连接测试失败: {e}")
        traceback_info = str(e)
        print(f"错误详情: {traceback_info}")
        return False

def set_api_credentials(api_key, api_url=None, model_id=None):
    """设置豆包API凭证"""
    global DOUBAN_API_KEY, DOUBAN_API_URL, DOUBAN_MODEL_ID
    
    DOUBAN_API_KEY = api_key
    
    if api_url:
        DOUBAN_API_URL = api_url
    
    if model_id:
        DOUBAN_MODEL_ID = model_id
    
    print(f"豆包API凭证已更新")
    
    # 返回测试结果
    return test_api_connection()

def query_ai_with_memory(task, current_screenshot_base64, previous_screenshot_base64=None, ui_elements=None):
    """使用记忆功能查询AI，支持同时分析两张截图
    
    参数:
        task: 任务描述
        current_screenshot_base64: 当前截图的base64编码
        previous_screenshot_base64: 前一张截图的base64编码（可选）
        ui_elements: UI元素信息（可选）
        
    返回:
        str: AI的响应文本
    """
    try:
        # 构建提示词
        prompt = f"""请分析当前界面并执行以下任务: {task}

请按照以下步骤进行分析:

1. 分析当前页面:
   - 识别当前所在的应用和页面
   - 分析页面上的主要元素和布局
   - 确定当前页面的功能和状态

2. 分析任务路径:
   - 确定完成任务所需的步骤
   - 识别每个步骤需要操作的UI元素
   - 评估当前页面与目标页面的差距

3. 分析匹配度:
   - 评估当前页面与任务目标的匹配程度
   - 确定是否需要导航到其他页面
   - 识别可能的障碍或挑战

4. 分析UI变化:
   - 比较前后两张截图的差异
   - 识别新增、删除或位置变化的元素
   - 评估操作对界面的影响

5. 分析操作效果:
   - 评估上一步操作的效果
   - 确定是否需要调整操作策略
   - 识别可能的卡住或异常情况

6. 提供下一步建议:
   - 根据分析结果提供具体的操作步骤
   - 考虑界面变化和操作效果
   - 提供备选方案和异常处理策略

请提供清晰的ADB命令，确保每个命令都是有效的。命令应包含在```shell代码块内，例如:

```shell
adb shell input tap 450 800
adb shell input text "搜索内容"
```

如果检测到界面卡住，请考虑以下策略:
1. 清除搜索框内容并重新输入
2. 按返回键返回上一级
3. 关闭当前应用并重新启动
4. 重启ADB服务

请确保所有命令都是有效的ADB命令，不要包含占位符或示例命令。"""

        # 如果有UI元素信息，添加到提示中
        if ui_elements:
            # 确保ui_elements是字符串
            ui_elements_str = ui_elements
            if not isinstance(ui_elements, str):
                ui_elements_str = json.dumps(ui_elements, ensure_ascii=False, indent=2)
            prompt += f"\n\n当前界面的UI元素:\n{ui_elements_str}"
        
        # 如果有前一张截图，添加到提示中
        if previous_screenshot_base64:
            prompt += "\n\n请同时分析前后两张截图，理解界面变化和操作效果。"
        
        # 使用原有的query_ai函数
        return query_ai(prompt, current_screenshot_base64, ui_elements)
    except Exception as e:
        print(f"查询AI时出错: {e}")
        traceback.print_exc() # 打印详细错误信息
        return None
