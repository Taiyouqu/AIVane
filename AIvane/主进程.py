import uiautomator2 as u2
import time
import os
import json
import sys
import traceback
from 模块 import (
    # UI 助手
    filter_xml_content, display_ui_elements, format_elements_for_ai,
    # ADB 控制器
    capture_screenshot, check_adb_connection, parse_and_execute_adb_commands, encode_image_to_base64,
    # AI 连接器
    query_ai, test_api_connection, set_api_credentials
)

# 配置信息
CONFIG_FILE = "config.json"

def load_config():
    """加载配置文件"""
    default_config = {
        "openai_api_key": "YOUR_OPENAI_API_KEY",  # OpenAI API密钥
        "screenshot_folder": "screenshots",
        "debug_mode": False
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                print("配置已加载")
                return config
        else:
            print(f"配置文件不存在，创建默认配置: {CONFIG_FILE}")
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            return default_config
    except Exception as e:
        print(f"加载配置出错: {e}")
        return default_config

def save_config(config):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print("配置已保存")
        return True
    except Exception as e:
        print(f"保存配置出错: {e}")
        return False

def setup_environment(config):
    """设置环境"""
    # 创建截图文件夹
    os.makedirs(config["screenshot_folder"], exist_ok=True)
    
    # 设置API凭证
    api_success = set_api_credentials(
        config["douban_api_key"], 
        config.get("douban_api_url"), 
        config.get("douban_model_id")
    )
    
    if not api_success:
        print("警告: 豆包API连接测试失败，请检查凭证")
    
    # 检查ADB连接
    adb_success = check_adb_connection()
    if not adb_success:
        print("警告: ADB连接测试失败，请检查设备连接")
    
    return api_success and adb_success

def configure_api():
    """配置API设置"""
    config = load_config()
    
    print("\n===== 豆包API 配置 =====")
    print(f"当前豆包API密钥: {config.get('douban_api_key', '')[:5]}{'*' * 10}" if config.get('douban_api_key', '') and len(config.get('douban_api_key', '')) > 5 else "未设置")
    print(f"当前豆包API地址: {config.get('douban_api_url', '')}")
    print(f"当前豆包模型ID: {config.get('douban_model_id', '')}")
    print(f"代理设置: {'启用' if config.get('use_proxy', False) else '禁用'}")
    if config.get('use_proxy', False):
        print(f"HTTP代理: {config.get('proxy_http', '')}")
        print(f"HTTPS代理: {config.get('proxy_https', '')}")
    
    new_key = input("输入新的豆包API密钥 (或按Enter保持不变): ")
    if new_key.strip():
        config['douban_api_key'] = new_key.strip()
    
    new_url = input("输入新的豆包API地址 (或按Enter保持不变): ")
    if new_url.strip():
        config['douban_api_url'] = new_url.strip()
    
    new_model = input("输入新的豆包模型ID (或按Enter保持不变): ")
    if new_model.strip():
        config['douban_model_id'] = new_model.strip()
    
    use_proxy = input("是否使用代理? (y/n, 默认为n): ").lower()
    config['use_proxy'] = use_proxy == 'y'
    
    if config['use_proxy']:
        new_http_proxy = input(f"输入HTTP代理地址 (当前: {config.get('proxy_http', '')}, 或按Enter保持不变): ")
        if new_http_proxy.strip():
            config['proxy_http'] = new_http_proxy.strip()
        
        new_https_proxy = input(f"输入HTTPS代理地址 (当前: {config.get('proxy_https', '')}, 或按Enter保持不变): ")
        if new_https_proxy.strip():
            config['proxy_https'] = new_https_proxy.strip()
    
    save_config(config)
    print("正在测试新的API配置...")
    
    # 导入模块进行测试
    from 模块.ai_connector import set_api_credentials
    
    api_success = set_api_credentials(
        config["douban_api_key"], 
        config.get("douban_api_url"), 
        config.get("douban_model_id")
    )
    if api_success:
        print("✅ API配置测试成功")
    else:
        print("❌ API配置测试失败")
    
    return config

def print_banner():
    """打印程序启动横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║             移动设备 AI 代理 (Mobile AI Agent)            ║
    ║                                                           ║
    ║       基于豆包大模型的Android设备自动化控制系统       ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("系统初始化中...")

def show_help():
    """显示帮助信息"""
    help_text = """
    === 移动设备AI代理使用说明 ===
    
    基本命令:
      帮助 - 显示此帮助信息
      退出 - 退出程序
      配置 - 配置豆包API
      连接 - 检查设备连接
      截图 - 获取当前屏幕截图
      停止 - 停止当前执行的任务流程（按Ctrl+C也可中断）
    
    任务指令示例:
      打开浏览器并搜索GitHub
      打开设置并开启WiFi
      返回主页，打开相机并拍照
    
    使用说明:
      1. 确保Android设备已通过USB连接并启用调试
      2. 在提示符下输入清晰任务指令
      3. 系统会自动截图、分析界面并提供操作建议
      4. 系统将自动执行操作并继续分析下一步
      5. 所有步骤将自动连续执行，直到任务完成
      6. 随时可按Ctrl+C中断当前任务流程
    """
    print(help_text)

def analyze_and_execute_task(d, config, task, current_screenshot_path, previous_screenshot_path=None, task_history=None, previous_commands=None):
    """分析当前屏幕并执行任务，然后返回是否需要继续循环"""
    if task_history is None:
        task_history = []
    
    try:
        # 1. 获取UI层次结构
        print("正在分析屏幕UI元素...")
        try:
            current_xml_content = d.dump_hierarchy()
            
            # 如果有前一张截图，尝试获取其XML内容
            previous_xml_content = None
            if previous_screenshot_path and os.path.exists(previous_screenshot_path):
                try:
                    # 尝试从缓存中获取前一个XML
                    previous_xml_path = previous_screenshot_path.replace('.png', '.xml')
                    if os.path.exists(previous_xml_path):
                        with open(previous_xml_path, 'r', encoding='utf-8') as f:
                            previous_xml_content = f.read()
                            print("✅ 已加载前一张截图的XML内容用于对比分析")
                except Exception as e:
                    print(f"⚠️ 无法加载前一张截图的XML内容: {e}")
            
            # 检查界面是否卡住
            if previous_screenshot_path and os.path.exists(previous_screenshot_path):
                from 模块.adb_controller import handle_stuck_interface
                stuck_handled, stuck_message = handle_stuck_interface(
                    d, 
                    current_xml_content, 
                    previous_xml_content, 
                    current_screenshot_path, 
                    previous_screenshot_path
                )
                
                if stuck_handled:
                    print(f"\n✅ {stuck_message}")
                    # 等待一段时间，让界面稳定
                    time.sleep(2)
                    # 重新获取UI结构
                    current_xml_content = d.dump_hierarchy()
            
            # 分析UI变化
            from 模块.ui_helper import analyze_ui_changes
            changes, changes_report = analyze_ui_changes(current_xml_content, previous_xml_content)
            
            # 保存当前XML内容，以便下次分析
            try:
                xml_path = current_screenshot_path.replace('.png', '.xml')
                with open(xml_path, 'w', encoding='utf-8') as f:
                    f.write(current_xml_content)
            except Exception as e:
                print(f"⚠️ 无法保存XML内容: {e}")
            
            # 显示UI变化报告
            if previous_xml_content:
                print("\n界面变化分析:")
                print("="*60)
                print(changes_report)
                print("="*60)
            
            # 处理UI元素
            ui_elements = filter_xml_content(current_xml_content)
            ui_elements_formatted = display_ui_elements(ui_elements)
            ui_elements_for_ai = format_elements_for_ai(ui_elements)
        except Exception as e:
            print(f"❌ 分析UI元素失败: {e}")
            return False
        
        # 2. 将截图转换为base64
        current_screenshot_base64 = encode_image_to_base64(current_screenshot_path)
        if not current_screenshot_base64:
            print("❌ 当前图片编码失败，无法继续")
            return False
            
        # 如果有前一张截图，也进行编码
        previous_screenshot_base64 = None
        if previous_screenshot_path and os.path.exists(previous_screenshot_path):
            previous_screenshot_base64 = encode_image_to_base64(previous_screenshot_path)
            if previous_screenshot_base64:
                print("✅ 已加载前一张截图用于对比分析")
            else:
                print("⚠️ 前一张图片编码失败，将只分析当前截图")
        
        # 3. 查询AI
        print(f"\n正在分析任务: {task}")
        print("正在咨询豆包大模型，这可能需要几秒钟...")
        
        # 如果有任务历史，将其添加到提示中
        context = "\n\n任务历史:\n" + "\n".join(task_history) if task_history else ""
        
        # 如果有UI变化报告，也添加到提示中
        if previous_xml_content:
            context += f"\n\n界面变化分析:\n{changes_report}"
        
        # 如果有界面卡住处理信息，也添加到提示中
        if 'stuck_message' in locals():
            context += f"\n\n界面卡住处理:\n{stuck_message}"
        
        # 使用带记忆功能的AI查询
        from 模块.ai_connector import query_ai_with_memory
        ai_response = query_ai_with_memory(
            task + context, 
            current_screenshot_base64, 
            previous_screenshot_base64, 
            ui_elements_for_ai
        )
        
        if not ai_response:
            print("❌ 无法获取豆包大模型响应")
            return False
        
        # 4. 显示响应
        print("\n豆包大模型响应:")
        print("="*60)
        print(ai_response)
        print("="*60)
        
        # 添加到任务历史
        task_history.append(f"步骤 {len(task_history)+1}:\n{ai_response}")
        
        # 5. 执行ADB命令
        success = parse_and_execute_adb_commands(ai_response, previous_commands)
        
        # 如果命令提取失败，尝试添加提示重新请求
        if not success:
            print("\n❌ 无法提取有效ADB命令，尝试重新请求...")
            
            # 添加格式提示
            retry_prompt = task + context + "\n\n上一次请求没有提供有效的ADB命令，请确保在```shell代码块内提供至少一个有效的ADB命令。例如:\n```shell\nadb shell input tap 450 800\n```"
            
            # 重新请求
            print("正在重新咨询豆包大模型...")
            ai_response = query_ai_with_memory(
                retry_prompt, 
                current_screenshot_base64, 
                previous_screenshot_base64, 
                ui_elements_for_ai
            )
            
            if ai_response:
                print("\n豆包大模型新响应:")
                print("="*60)
                print(ai_response)
                print("="*60)
                
                # 替换任务历史中的最后一个条目
                if task_history:
                    task_history[-1] = f"步骤 {len(task_history)}:\n{ai_response}"
                
                # 重新尝试执行
                success = parse_and_execute_adb_commands(ai_response, previous_commands)
        
        if success:
            print("\n✅ 当前步骤执行完成!")
            
            # 6. 等待并重新截图
            wait_time = config.get("wait_time_between_steps", 2)
            print(f"\n等待 {wait_time} 秒...")
            time.sleep(wait_time)
            
            print("\n正在捕获执行后的屏幕状态...")
            new_screenshot_path = os.path.join(config["screenshot_folder"], f"result_{int(time.time())}.png")
            capture_screenshot(new_screenshot_path)
            
            # 提取当前执行的命令，用于下次比较
            import re
            current_commands = []
            shell_block_pattern = r"```shell\s*([\s\S]*?)\s*```"
            shell_blocks = re.findall(shell_block_pattern, ai_response)
            
            if shell_blocks:
                for block in shell_blocks:
                    # 提取以adb开头的行
                    adb_commands = [line.strip() for line in block.split('\n') if line.strip().startswith('adb')]
                    current_commands.extend(adb_commands)
            
            # 7. 自动继续执行下一步（不再询问用户）
            print("\n自动继续执行下一步...")
            return analyze_and_execute_task(d, config, task, new_screenshot_path, current_screenshot_path, task_history, current_commands)
        else:
            print("\n❌ 任务执行遇到问题，请检查并重试")
            return False
            
    except Exception as e:
        print(f"\n❌ 执行任务时出错: {e}")
        traceback.print_exc()
        return False

def mobile_ai_agent():
    """移动AI代理主函数"""
    try:
        # 加载配置
        config = load_config()
        
        # 检查环境是否准备就绪
        env_ready = setup_environment(config)
        if not env_ready:
            setup_choice = input("\n环境检查发现问题，是否进行配置? (y/n): ")
            if setup_choice.lower() == 'y':
                config = configure_api()
            else:
                print("警告: 环境可能未正确配置，可能影响程序运行")
                print("提示: 如果通过包名启动应用失败，将自动尝试通过桌面搜索方式打开应用")
        
        # 连接设备
        print("\n正在连接设备...")
        try:
            d = u2.connect()
            print("✅ 设备已连接")
            print("提示: 系统已启用智能应用启动功能，如包名启动失败将自动尝试桌面搜索")
            print("提示: 系统已启用记忆功能，将同时分析前后两张截图进行对比")
        except Exception as e:
            print(f"❌ 设备连接失败: {e}")
            print("请确保设备已正确连接并已安装ATX代理")
            return
        
        # 主循环
        while True:
            try:
                print("\n" + "="*60)
                task = input("\n请输入任务指令 (输入'帮助'查看命令列表): ")
                task = task.strip()
                
                # 处理特殊命令
                if task.lower() in ['退出', 'exit', 'quit']:
                    print("程序结束，感谢使用!")
                    break
                elif task.lower() in ['帮助', 'help']:
                    show_help()
                    continue
                elif task.lower() in ['配置', 'config', 'setup']:
                    config = configure_api()
                    continue
                elif task.lower() in ['连接', 'connect']:
                    check_adb_connection()
                    continue
                elif task.lower() in ['截图', 'screenshot']:
                    screenshot_path = capture_screenshot(
                        os.path.join(config["screenshot_folder"], f"screenshot_{int(time.time())}.png")
                    )
                    if screenshot_path:
                        print(f"截图已保存: {screenshot_path}")
                    continue
                elif task.lower() in ['停止', 'stop']:
                    print("没有正在执行的任务流程")
                    continue
                
                # 执行常规任务流程
                print("\n开始执行任务自动化流程...")
                
                # 1. 捕获屏幕截图
                current_screenshot_path = capture_screenshot(
                    os.path.join(config["screenshot_folder"], "current_screen.png")
                )
                if not current_screenshot_path:
                    print("❌ 无法获取屏幕截图，请检查设备连接")
                    continue
                
                # 2. 检查是否有前一张截图
                previous_screenshot_path = None
                screenshot_folder = config["screenshot_folder"]
                if os.path.exists(screenshot_folder):
                    screenshot_files = [f for f in os.listdir(screenshot_folder) if f.endswith('.png')]
                    if screenshot_files:
                        # 按修改时间排序，获取最新的截图
                        latest_screenshot = max(screenshot_files, key=lambda f: os.path.getmtime(os.path.join(screenshot_folder, f)))
                        if latest_screenshot != os.path.basename(current_screenshot_path):
                            previous_screenshot_path = os.path.join(screenshot_folder, latest_screenshot)
                            print(f"✅ 已找到前一张截图: {previous_screenshot_path}")
                
                # 3. 开始任务分析和执行循环
                analyze_and_execute_task(d, config, task, current_screenshot_path, previous_screenshot_path)
                
            except KeyboardInterrupt:
                print("\n操作已中断")
                print("提示: 输入'停止'可以停止当前任务流程")
                continue
            except Exception as e:
                print(f"\n❌ 执行任务时出错: {e}")
                if config.get("debug_mode", False):
                    traceback.print_exc()
                continue
                
    except Exception as e:
        print(f"Mobile AI Agent运行出错: {e}")
        traceback.print_exc()
        print("\n请确保:")
        print("1. 已安装所需库: pip install uiautomator2 pillow requests")
        print("2. 设备已通过USB连接并已启用USB调试")
        print("3. 已安装ATX代理 (python -m uiautomator2 init)")
        print("4. API密钥配置正确")

if __name__ == "__main__":
    print_banner()
    try:
        mobile_ai_agent()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as e:
        print(f"\n程序遇到未处理的错误: {e}")
        traceback.print_exc()
        print("\n请检查环境配置及依赖项是否正确安装")
