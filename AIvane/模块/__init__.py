from .ui_helper import (
    filter_xml_content,
    display_ui_elements,
    format_elements_for_ai
)

from .adb_controller import (
    capture_screenshot,
    check_adb_connection,
    parse_and_execute_adb_commands
)

from .ai_connector import (
    query_ai,
    test_api_connection,
    set_api_credentials,
    encode_image_to_base64
)

print("模块初始化完成 - 移动设备AI代理系统")
print("- UI助手: 已加载")
print("- ADB控制器: 已加载")
print("- 豆包API连接器: 已加载")

__all__ = [
    # UI 助手模块
    'filter_xml_content', 'display_ui_elements', 'format_elements_for_ai',
    
    # ADB 控制器模块
    'capture_screenshot', 'check_adb_connection', 'parse_and_execute_adb_commands',
    
    # AI 连接器模块
    'query_ai', 'test_api_connection', 'set_api_credentials', 'encode_image_to_base64'
] 