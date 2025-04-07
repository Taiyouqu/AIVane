import subprocess
import time
import os
import uiautomator2 as u2
import traceback
import base64
from 模块.ui_helper import are_images_identical, are_ui_structures_identical

def encode_image_to_base64(image_path):
    """将图片编码为Base64字符串"""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"图片编码失败: {e}")
        return None

def execute_adb_command(command):
    """执行ADB命令并返回成功/失败状态和输出
    
    参数:
        command: ADB命令
        
    返回:
        tuple: (成功/失败, 输出内容)
    """
    try:
        # 处理sleep命令
        if command.startswith("sleep "):
            sleep_time = float(command.split("sleep ")[1])
            print(f"等待 {sleep_time} 秒...")
            time.sleep(sleep_time)
            return True, ""
        
        # 处理ADB shell sleep命令
        if "adb shell sleep" in command:
            sleep_time = float(command.split("sleep")[1].strip())
            print(f"等待 {sleep_time} 秒...")
            time.sleep(sleep_time)
            return True, ""
        
        # 执行ADB命令
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        output_str = output.decode('utf-8', errors='replace').strip()
        
        return True, output_str
    except subprocess.CalledProcessError as e:
        error_output = e.output.decode('utf-8', errors='replace').strip()
        print(f"命令执行失败: {error_output}")
        return False, error_output
    except Exception as e:
        print(f"执行命令时出错: {str(e)}")
        return False, str(e)

def capture_screenshot(output_path="screenshot.png"):
    """使用ADB截取手机屏幕"""
    try:
        subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screenshot.png"], check=True)
        subprocess.run(["adb", "pull", "/sdcard/screenshot.png", output_path], check=True)
        subprocess.run(["adb", "shell", "rm", "/sdcard/screenshot.png"], check=True)
        print(f"截图已保存至 {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"截图失败: {e}")
        return None

def check_adb_connection():
    """检查ADB连接状态"""
    try:
        result = subprocess.run(["adb", "devices"], check=True, capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        
        # 第一行是标题，至少要有两行才表示有设备连接
        if len(lines) < 2:
            print("未检测到已连接的设备")
            return False
        
        # 检查连接的设备
        devices = []
        for line in lines[1:]:
            if line and not line.startswith('*') and not line.strip() == "":
                parts = line.split('\t')
                if len(parts) >= 2:
                    device_id, status = parts[0], parts[1]
                    devices.append((device_id, status))
        
        if devices:
            print(f"检测到 {len(devices)} 个设备:")
            for device_id, status in devices:
                print(f"  设备: {device_id}, 状态: {status}")
            return True
        else:
            print("未检测到已连接的设备")
            return False
    except subprocess.CalledProcessError as e:
        print(f"检查ADB连接失败: {e}")
        return False
    except Exception as e:
        print(f"检查ADB连接时发生错误: {e}")
        return False

def tap_screen(x, y):
    """点击屏幕指定坐标"""
    command = f"adb shell input tap {x} {y}"
    return execute_adb_command(command)

def swipe_screen(x1, y1, x2, y2, duration=300):
    """滑动屏幕"""
    command = f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}"
    return execute_adb_command(command)

def input_text(text):
    """输入文本"""
    try:
        # 替换特殊字符和空格
        sanitized_text = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
        
        # 首先尝试使用uiautomator2输入文本（更可靠）
        try:
            d = u2.connect()
            # 尝试找到一个可输入的文本框
            edit_boxes = d(className="android.widget.EditText")
            if edit_boxes.exists:
                print("找到可输入文本框，使用UI Automator输入文本")
                edit_boxes[0].set_text(text)
                return True, "文本已输入"
        except Exception as e:
            print(f"UI Automator输入失败: {e}，尝试使用ADB命令")
        
        # 如果UI Automator失败，尝试使用ADB命令
        command = f"adb shell input text '{sanitized_text}'"
        return execute_adb_command(command)
    except Exception as e:
        print(f"输入文本失败: {e}")
        return False, str(e)

def press_key(keycode):
    """按下按键"""
    # 常用按键代码：
    # 3 - HOME, 4 - BACK, 66 - ENTER, 26 - POWER, 
    # 24 - VOLUME_UP, 25 - VOLUME_DOWN, 82 - MENU
    command = f"adb shell input keyevent {keycode}"
    return execute_adb_command(command)

def launch_app(package_name, activity_name=None):
    """启动应用"""
    # 首先尝试通过包名/活动名启动
    if activity_name:
        command = f"adb shell am start -n {package_name}/{activity_name}"
    else:
        command = f"adb shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
    
    success, output = execute_adb_command(command)
    
    # 检查输出中是否包含错误信息
    if not success or "Error" in output or "does not exist" in output:
        print(f"通过包名启动应用失败，尝试通过桌面搜索启动...")
        
        # 从包名中提取可能的应用名（简单处理）
        app_name = package_name.split('.')[-1]
        if app_name == "android":
            # 尝试从包名中获取更有意义的部分
            parts = package_name.split('.')
            if len(parts) > 2:
                app_name = parts[-2]
        
        # 执行备选启动策略：回到主页
        execute_adb_command("adb shell input keyevent 3")
        time.sleep(1.5)  # 等待主页加载
        
        try:
            # 尝试连接设备并查找搜索栏
            d = u2.connect()
            
            # 先尝试找到搜索框元素
            search_elements = d(text="搜索").exists or d(desc="搜索").exists or d(resourceId=".*search.*").exists
            
            if search_elements:
                print("找到桌面搜索元素，点击它...")
                if d(text="搜索").exists:
                    d(text="搜索").click()
                elif d(desc="搜索").exists:
                    d(desc="搜索").click()
                elif d(resourceId=".*search.*").exists:
                    d(resourceId=".*search.*").click()
            else:
                # 如果找不到搜索元素，尝试点击典型的搜索栏位置（屏幕上方中间）
                print("未找到搜索元素，尝试点击屏幕上方中间位置...")
                screen_width, screen_height = d.window_size()
                execute_adb_command(f"adb shell input tap {screen_width//2} {screen_height//8}")
            
            time.sleep(1)  # 等待搜索栏准备好
            
            # 输入应用名
            execute_adb_command(f'adb shell input text "{app_name}"')
            time.sleep(0.5)
            
            # 按回车键
            execute_adb_command("adb shell input keyevent 66")
            time.sleep(1.5)
            
            # 点击第一个搜索结果（假设是目标应用）
            result_found = False
            
            # 尝试查找与应用名匹配的元素
            if d(text=app_name).exists:
                d(text=app_name).click()
                result_found = True
            elif d(textContains=app_name).exists:
                d(textContains=app_name).click()
                result_found = True
            
            # 如果没有找到，点击屏幕上第一个可能的结果位置
            if not result_found:
                print("尝试点击第一个搜索结果...")
                execute_adb_command(f"adb shell input tap {screen_width//2} {screen_height//4}")
            
            time.sleep(2)  # 等待应用启动
            return True, "通过桌面搜索方式启动应用"
            
        except Exception as e:
            print(f"通过桌面搜索启动应用失败: {e}")
            traceback.print_exc()
            return False, f"应用启动失败: {str(e)}"
    
    return success, output

def stop_app(package_name):
    """停止应用"""
    command = f"adb shell am force-stop {package_name}"
    return execute_adb_command(command)

def clear_app_data(package_name):
    """清除应用数据"""
    command = f"adb shell pm clear {package_name}"
    return execute_adb_command(command)

def clear_search_text(d=None):
    """清除搜索框或输入框中的文本
    
    首先尝试通过UI Automator操作，如果失败则使用ADB命令模拟手动操作
    """
    try:
        # 尝试通过UI Automator清除
        if d is None:
            d = u2.connect()
        
        # 查找输入框
        input_fields = d(className="android.widget.EditText")
        if input_fields.exists:
            print("找到输入框，尝试清除内容...")
            input_field = input_fields[0]
            
            # 先尝试直接清除
            try:
                input_field.clear_text()
                print("成功清除输入框内容")
                return True, "通过UI Automator清除成功"
            except Exception as e:
                print(f"直接清除失败: {e}，尝试其他方法")
        
        # UI Automator直接清除失败，尝试模拟长按全选和删除
        print("尝试通过长按全选和删除键清除内容...")
        
        # 找到输入框位置
        if input_fields.exists:
            bounds = input_fields[0].info['bounds']
            center_x = (bounds['left'] + bounds['right']) // 2
            center_y = (bounds['top'] + bounds['bottom']) // 2
        else:
            # 如果找不到输入框，尝试使用屏幕上部的通用位置
            screen_width, screen_height = d.window_size()
            center_x = screen_width // 2
            center_y = screen_height // 6
        
        # 1. 长按选择全部文本
        execute_adb_command(f"adb shell input swipe {center_x} {center_y} {center_x} {center_y} 1000")
        time.sleep(0.5)
        
        # 2. 删除所选文本
        execute_adb_command("adb shell input keyevent 67")  # KEYCODE_DEL
        time.sleep(0.5)
        
        # 3. 再次按删除确保清除
        execute_adb_command("adb shell input keyevent 67")
        
        print("通过长按和删除键清除内容完成")
        return True, "通过长按和删除键清除成功"
        
    except Exception as e:
        print(f"清除搜索文本失败: {e}")
        traceback.print_exc()
        return False, f"清除搜索文本失败: {str(e)}"

def parse_and_execute_adb_commands(commands_text, previous_commands=None):
    """解析并执行AI提供的ADB命令
    
    参数:
        commands_text: 包含ADB命令的文本
        previous_commands: 上一次执行的命令列表，用于比较变化
    """
    import re
    
    # 提取命令
    commands = []
    
    # 尝试从shell代码块中提取命令
    shell_block_pattern = r"```shell\s*([\s\S]*?)\s*```"
    shell_blocks = re.findall(shell_block_pattern, commands_text)
    
    if shell_blocks:
        for block in shell_blocks:
            # 提取以adb开头的行
            adb_commands = [line.strip() for line in block.split('\n') if line.strip().startswith('adb')]
            commands.extend(adb_commands)
    
    # 如果没有找到shell代码块，尝试直接从文本中提取以adb开头的行
    if not commands:
        lines = commands_text.split('\n')
        commands = [line.strip() for line in lines if line.strip().startswith('adb')]
    
    # 如果仍然没有找到命令，尝试使用正则表达式匹配类似ADB命令的内容
    if not commands:
        adb_pattern = r'adb\s+shell\s+[a-zA-Z0-9_\-\.\/\s]+'
        potential_commands = re.findall(adb_pattern, commands_text)
        commands = [cmd.strip() for cmd in potential_commands]
    
    # 检查命令序列中是否有input text命令但前面没有input tap命令
    # 这表示AI想要输入文本但忘记先点击输入框
    processed_commands = []
    need_find_input_field = False
    need_clear_search = False
    
    # 检查是否有需要保持距离的命令对
    for i, cmd in enumerate(commands):
        # 检查是否需要清除搜索内容（如果连续输入两次文本到同一输入框）
        if "input text" in cmd and i > 0:
            # 如果前一条命令是输入文本，且现在又要输入文本，可能需要先清除
            if i > 0 and "input text" in commands[i-1]:
                need_clear_search = True
                print("\n⚠️ 检测到连续输入文本，可能需要先清除搜索框")
                
                try:
                    d = u2.connect()
                    clear_success, _ = clear_search_text(d)
                    if clear_success:
                        print("✅ 自动清除搜索框内容成功")
                    else:
                        print("❌ 自动清除搜索框内容失败，仍继续执行命令")
                except Exception as e:
                    print(f"自动清除搜索框内容时出错: {e}")
                
            # 检查前面是否有点击操作
            has_previous_tap = False
            for prev_cmd in commands[max(0, i-3):i]:  # 检查前3个命令
                if "input tap" in prev_cmd:
                    has_previous_tap = True
                    break
            
            if not has_previous_tap:
                print("\n⚠️ 警告: 在输入文本前没有点击输入框的命令")
                need_find_input_field = True
                
                try:
                    # 尝试使用uiautomator2找到输入框
                    d = u2.connect()
                    input_fields = d(className="android.widget.EditText")
                    
                    if input_fields.exists:
                        print("✅ 找到输入框，自动添加点击命令")
                        input_field = input_fields[0]
                        bounds = input_field.info['bounds']
                        center_x = (bounds['left'] + bounds['right']) // 2
                        center_y = (bounds['top'] + bounds['bottom']) // 2
                        
                        # 添加点击输入框的命令
                        tap_cmd = f"adb shell input tap {center_x} {center_y}"
                        processed_commands.append(tap_cmd)
                        print(f"添加命令: {tap_cmd}")
                        
                        # 添加短暂延迟，确保输入框获得焦点
                        processed_commands.append("adb shell sleep 0.5")
                    else:
                        print("❌ 无法找到输入框，请手动点击输入框后再输入文本")
                except Exception as e:
                    print(f"自动查找输入框时出错: {e}")

        # 检查是否需要在特定命令后添加等待时间
        if "am broadcast -a ADB_INPUT_TEXT" in cmd or "input text" in cmd:
            processed_commands.append(cmd)
            
            # 直接添加等待和自动截图命令
            processed_commands.append("adb shell sleep 1")  # 等待输入完成
            
            # 检查下一条命令是否是回车(keyevent 66)或点击确认
            if i < len(commands) - 1 and ("keyevent 66" in commands[i+1] or ("input tap" in commands[i+1] and "search" in commands_text.lower())):
                # 如果下一条命令是回车或搜索相关点击，这是重要的跳转点
                print("\n🔍 检测到输入后可能的界面跳转点")
                print("系统将在执行下一步前暂停并重新截图分析当前界面")
                
                # 添加等待并截图的特殊标记，实际执行时会处理
                processed_commands.append("##SPECIAL_ACTION:SCREENSHOT_AND_PAUSE##")
            
            continue
        
        processed_commands.append(cmd)
    
    # 如果有前一次的命令，比较变化
    if previous_commands:
        print("\n命令变化分析:")
        print("="*60)
        
        # 找出新增的命令
        new_commands = [cmd for cmd in processed_commands if cmd not in previous_commands]
        if new_commands:
            print(f"新增命令 ({len(new_commands)}):")
            for cmd in new_commands:
                print(f"  + {cmd}")
        
        # 找出删除的命令
        removed_commands = [cmd for cmd in previous_commands if cmd not in processed_commands]
        if removed_commands:
            print(f"删除命令 ({len(removed_commands)}):")
            for cmd in removed_commands:
                print(f"  - {cmd}")
        
        # 找出修改的命令
        modified_commands = []
        for i, cmd in enumerate(processed_commands):
            if i < len(previous_commands) and cmd != previous_commands[i]:
                modified_commands.append((previous_commands[i], cmd))
        
        if modified_commands:
            print(f"修改命令 ({len(modified_commands)}):")
            for old_cmd, new_cmd in modified_commands:
                print(f"  - {old_cmd}")
                print(f"  + {new_cmd}")
        
        print("="*60)
    
    # 执行命令
    if not processed_commands:
        print("❌ 无法从AI响应中提取有效的ADB命令")
        return False
    
    print("\n执行以下ADB命令:")
    for cmd in processed_commands:
        if cmd.startswith("##SPECIAL_ACTION"):
            print(f"  [特殊动作: 截图并分析]")
        else:
            print(f"  {cmd}")
    
    # 改进命令执行逻辑，支持逐步执行并等待
    executed_commands = []
    i = 0
    while i < len(processed_commands):
        cmd = processed_commands[i]
        
        # 处理特殊命令
        if cmd.startswith("##SPECIAL_ACTION"):
            if "SCREENSHOT_AND_PAUSE" in cmd:
                print("\n🔍 执行特殊动作: 截图并分析当前界面")
                
                # 自动截图
                screenshot_path = os.path.join("screenshots", f"analysis_{int(time.time())}.png")
                capture_screenshot(screenshot_path)
                
                print("\n✅ 已截图并保存至:", screenshot_path)
                print("\n⚠️ 重要提示: 请检查输入内容是否正确")
                print("系统已暂停执行后续命令，需要手动继续")
                
                # 询问用户是否继续执行后续命令
                continue_execution = input("\n是否继续执行后续命令? (y/n): ")
                if continue_execution.lower() != 'y':
                    print("用户选择中断命令序列")
                    return True  # 返回成功，因为这是用户的选择
            
            # 处理完特殊命令后继续下一条
            i += 1
            continue
            
        # 处理普通命令
        print(f"\n执行ADB命令: {cmd}")
        
        # 处理特殊命令：sleep
        if "sleep" in cmd:
            try:
                # 提取睡眠时间
                sleep_time = float(cmd.split("sleep")[1].strip())
                print(f"等待 {sleep_time} 秒...")
                time.sleep(sleep_time)
                executed_commands.append(cmd)
                i += 1  # 继续下一条命令
                continue
            except ValueError:
                print(f"无效的sleep命令格式: {cmd}")
                i += 1  # 跳过此命令
                continue
        
        # 检查是否是进入搜索模式的关键命令
        is_search_related = "broadcast -a ADB_INPUT_TEXT" in cmd or "input text" in cmd
        
        # 执行命令
        success, output = execute_adb_command(cmd)
        if success:
            executed_commands.append(cmd)
            if output:
                print(f"命令执行结果: {output}")
            else:
                print("命令执行结果: 成功")
                
            # 处理搜索相关命令后的特殊等待
            if is_search_related:
                print("\n⏱️ 等待输入完成...")
                time.sleep(1)  # 等待输入操作完成
        else:
            if "am broadcast" in cmd and "ADB_INPUT_TEXT" in cmd:
                # 如果broadcast命令失败，尝试使用input text替代
                alternate_cmd = cmd.replace("am broadcast -a ADB_INPUT_TEXT --es msg", "input text")
                print(f"⚠️ broadcast命令失败，尝试替代命令: {alternate_cmd}")
                
                alt_success, alt_output = execute_adb_command(alternate_cmd)
                if alt_success:
                    executed_commands.append(alternate_cmd)
                    if alt_output:
                        print(f"替代命令执行结果: {alt_output}")
                    else:
                        print("替代命令执行结果: 成功")
                else:
                    print(f"❌ 替代命令也失败: {alt_output}")
            else:
                print(f"❌ 命令执行失败: {output}")
            
            # 如果关键命令失败，考虑中断执行流程
            if "am start" in cmd or "keyevent 3" in cmd:
                print("⚠️ 关键导航命令失败，命令序列中断执行")
                break
        
        # 命令执行后等待UI响应
        if "tap" in cmd or "swipe" in cmd or "keyevent" in cmd:
            # 短暂等待UI响应
            time.sleep(1)
        elif "am start" in cmd:
            # 应用启动需要更长时间
            print("等待应用启动...")
            time.sleep(2.5)
        
        # 继续下一条命令
        i += 1
    
    return len(executed_commands) > 0

def handle_stuck_interface(d, current_xml, previous_xml, current_screenshot_path, previous_screenshot_path):
    """处理界面卡住的情况
    
    参数:
        d: uiautomator2设备对象
        current_xml: 当前UI的XML内容
        previous_xml: 前一个UI的XML内容
        current_screenshot_path: 当前截图的路径
        previous_screenshot_path: 前一张截图的路径
        
    返回:
        tuple: (是否成功处理, 处理策略描述)
    """
    # 检查图片和UI结构是否相同
    images_identical = are_images_identical(current_screenshot_path, previous_screenshot_path)
    ui_identical = are_ui_structures_identical(current_xml, previous_xml)
    
    if not (images_identical or ui_identical):
        return False, "界面未卡住，无需特殊处理"
    
    print("\n⚠️ 检测到界面可能卡住，尝试以下策略:")
    
    # 策略1: 尝试清除搜索框内容
    try:
        print("\n策略1: 尝试清除搜索框内容...")
        success, message = clear_search_text(d)
        if success:
            print("✅ 成功清除搜索框内容")
            return True, "已清除搜索框内容，请重新输入搜索内容"
        else:
            print(f"❌ 清除搜索框内容失败: {message}")
    except Exception as e:
        print(f"清除搜索框内容时出错: {e}")
    
    # 策略2: 尝试按返回键
    try:
        print("\n策略2: 尝试按返回键...")
        success, _ = execute_adb_command("adb shell input keyevent 4")
        if success:
            print("✅ 成功按返回键")
            return True, "已按返回键，请重新尝试操作"
        else:
            print("❌ 按返回键失败")
    except Exception as e:
        print(f"按返回键时出错: {e}")
    
    # 策略3: 尝试关闭当前应用
    try:
        print("\n策略3: 尝试关闭当前应用...")
        # 获取当前应用包名
        success, output = execute_adb_command("adb shell dumpsys window | grep mCurrentFocus")
        if success and "mCurrentFocus" in output:
            # 提取包名
            import re
            match = re.search(r"(\S+)/\S+}", output)
            if match:
                package_name = match.group(1)
                print(f"当前应用包名: {package_name}")
                
                # 强制停止应用
                success, _ = execute_adb_command(f"adb shell am force-stop {package_name}")
                if success:
                    print(f"✅ 成功关闭应用: {package_name}")
                    return True, f"已关闭应用 {package_name}，请重新启动应用"
                else:
                    print(f"❌ 关闭应用失败: {package_name}")
            else:
                print("无法提取当前应用包名")
        else:
            print("无法获取当前应用信息")
    except Exception as e:
        print(f"关闭应用时出错: {e}")
    
    # 策略4: 尝试重启ADB服务
    try:
        print("\n策略4: 尝试重启ADB服务...")
        success, _ = execute_adb_command("adb kill-server")
        if success:
            print("✅ 成功停止ADB服务")
            time.sleep(2)
            success, _ = execute_adb_command("adb start-server")
            if success:
                print("✅ 成功重启ADB服务")
                return True, "已重启ADB服务，请重新尝试操作"
            else:
                print("❌ 启动ADB服务失败")
        else:
            print("❌ 停止ADB服务失败")
    except Exception as e:
        print(f"重启ADB服务时出错: {e}")
    
    # 所有策略都失败
    return False, "所有处理策略都失败，请手动检查设备状态" 