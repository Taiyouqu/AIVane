import xml.etree.ElementTree as ET
import re
import json
import os

def calculate_center(bounds_str):
    """计算元素的中心点坐标"""
    match = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
    if match:
        left, top, right, bottom = map(int, match.groups())
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2
        return center_x, center_y
    return None, None

def extract_bounds(bounds_str):
    """从bounds字符串中提取坐标值"""
    match = re.search(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
    if match:
        left, top, right, bottom = map(int, match.groups())
        return left, top, right, bottom
    return None, None, None, None

def filter_xml_content(xml_content):
    """解析并过滤XML内容，提取有文本的元素"""
    try:
        # 解析XML
        root = ET.fromstring(xml_content)
        
        # 提取有文本的元素
        elements_with_text = []
        for i, node in enumerate(root.findall('.//*'), 1):
            text = node.get('text', '').strip()
            content_desc = node.get('content-desc', '').strip()
            
            # 只保留有文本或内容描述的元素
            if text or content_desc:
                display_text = text if text else content_desc
                bounds = node.get('bounds', 'N/A')
                resource_id = node.get('resource-id', '')
                clickable = node.get('clickable', 'false')
                class_name = node.get('class', '')
                
                # 提取坐标信息
                left, top, right, bottom = extract_bounds(bounds)
                center_x, center_y = calculate_center(bounds)
                
                element_info = {
                    'index': i,
                    'text': display_text,
                    'bounds': [left, top, right, bottom],
                    'center': [center_x, center_y],
                    'resource_id': resource_id,
                    'clickable': clickable == 'true',
                    'class': class_name
                }
                elements_with_text.append(element_info)
        
        return elements_with_text
    except Exception as e:
        print(f"解析XML时出错: {e}")
        return []

def display_ui_elements(elements):
    """显示UI元素信息"""
    if not elements:
        print("未找到包含文本的UI元素")
        return
    
    print(f"\n找到 {len(elements)} 个包含文本的UI元素:")
    
    # 整合所有元素信息到一个列表中
    all_elements = []
    
    for i, elem in enumerate(elements, 1):
        # 创建更紧凑的单行JSON格式
        output = {
            "id": i,
            "text": elem['text'],
            "center": elem['center'],
            "action": "tap"
        }
        
        if elem['clickable']:
            output["clickable"] = elem['clickable']
        
        # 将元素添加到列表
        all_elements.append(output)
    
    # 输出所有元素信息，使用紧凑的格式
    print("="*50)
    for elem in all_elements:
        print(json.dumps(elem, ensure_ascii=False) + ",")
    print("="*50)
    
    return all_elements

def search_element_by_text(elements, text):
    """根据文本内容搜索元素"""
    matches = []
    for elem in elements:
        if text.lower() in elem['text'].lower():
            matches.append(elem)
    return matches

def find_clickable_elements(elements):
    """查找可点击的元素"""
    return [elem for elem in elements if elem['clickable']]

def find_elements_by_type(elements, class_name):
    """根据类型查找元素"""
    return [elem for elem in elements if class_name.lower() in elem['class'].lower()]

def format_elements_for_ai(elements):
    """将元素格式化为AI友好的格式"""
    ai_elements = []
    for i, elem in enumerate(elements, 1):
        ai_elem = {
            "id": i,
            "text": elem['text'],
            "center": elem['center'],
            "action": "tap",
        }
        
        if elem['clickable']:
            ai_elem["clickable"] = True
        
        ai_elements.append(ai_elem)
    
    return ai_elements

def compare_ui_elements(current_elements, previous_elements):
    """比较两组UI元素，分析界面变化
    
    返回一个包含变化信息的字典，包括新增、删除和位置变化的元素
    """
    if not previous_elements:
        return {
            "new_elements": current_elements,
            "removed_elements": [],
            "position_changed": [],
            "unchanged": []
        }
    
    # 创建文本到元素的映射，用于快速查找
    current_map = {elem['text']: elem for elem in current_elements if elem['text']}
    previous_map = {elem['text']: elem for elem in previous_elements if elem['text']}
    
    # 找出新增的元素
    new_texts = set(current_map.keys()) - set(previous_map.keys())
    new_elements = [current_map[text] for text in new_texts]
    
    # 找出删除的元素
    removed_texts = set(previous_map.keys()) - set(current_map.keys())
    removed_elements = [previous_map[text] for text in removed_texts]
    
    # 找出位置变化的元素
    position_changed = []
    unchanged = []
    
    # 检查共同元素的位置变化
    common_texts = set(current_map.keys()) & set(previous_map.keys())
    for text in common_texts:
        current_elem = current_map[text]
        previous_elem = previous_map[text]
        
        # 如果中心点坐标不同，则认为位置发生了变化
        if current_elem['center'] != previous_elem['center']:
            position_changed.append({
                'text': text,
                'previous_position': previous_elem['center'],
                'current_position': current_elem['center']
            })
        else:
            unchanged.append(current_elem)
    
    return {
        "new_elements": new_elements,
        "removed_elements": removed_elements,
        "position_changed": position_changed,
        "unchanged": unchanged
    }

def format_ui_changes(changes):
    """格式化UI变化信息，生成人类可读的报告"""
    report = []
    
    # 新增元素
    if changes["new_elements"]:
        report.append(f"新增元素 ({len(changes['new_elements'])}):")
        for elem in changes["new_elements"]:
            report.append(f"  - {elem['text']} 在坐标 {elem['center']}")
    
    # 删除元素
    if changes["removed_elements"]:
        report.append(f"删除元素 ({len(changes['removed_elements'])}):")
        for elem in changes["removed_elements"]:
            report.append(f"  - {elem['text']} 从坐标 {elem['center']} 移除")
    
    # 位置变化
    if changes["position_changed"]:
        report.append(f"位置变化 ({len(changes['position_changed'])}):")
        for change in changes["position_changed"]:
            report.append(f"  - {change['text']} 从 {change['previous_position']} 移动到 {change['current_position']}")
    
    # 未变化元素
    if changes["unchanged"]:
        report.append(f"未变化元素 ({len(changes['unchanged'])}):")
        for elem in changes["unchanged"][:5]:  # 只显示前5个，避免报告过长
            report.append(f"  - {elem['text']} 保持在坐标 {elem['center']}")
        if len(changes["unchanged"]) > 5:
            report.append(f"  - ... 以及 {len(changes['unchanged']) - 5} 个其他未变化元素")
    
    return "\n".join(report)

def analyze_ui_changes(current_xml, previous_xml=None):
    """分析UI变化，比较两个XML的差异
    
    返回一个包含变化信息的字典和格式化的报告
    """
    # 解析当前XML
    current_elements = filter_xml_content(current_xml)
    
    # 解析前一个XML（如果有）
    previous_elements = filter_xml_content(previous_xml) if previous_xml else None
    
    # 比较变化
    changes = compare_ui_elements(current_elements, previous_elements)
    
    # 格式化报告
    report = format_ui_changes(changes)
    
    return changes, report

def are_images_identical(image1_path, image2_path):
    """比较两张图片是否相同
    
    参数:
        image1_path: 第一张图片的路径
        image2_path: 第二张图片的路径
        
    返回:
        bool: 如果图片相同返回True，否则返回False
    """
    try:
        import hashlib
        
        # 计算两张图片的MD5哈希值
        def get_image_hash(image_path):
            with open(image_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        
        # 如果文件不存在，返回False
        if not os.path.exists(image1_path) or not os.path.exists(image2_path):
            return False
        
        # 比较文件大小
        if os.path.getsize(image1_path) != os.path.getsize(image2_path):
            return False
        
        # 比较文件哈希值
        hash1 = get_image_hash(image1_path)
        hash2 = get_image_hash(image2_path)
        
        return hash1 == hash2
    except Exception as e:
        print(f"比较图片时出错: {e}")
        return False

def are_ui_structures_identical(current_xml, previous_xml):
    """比较两个UI结构是否相同
    
    参数:
        current_xml: 当前UI的XML内容
        previous_xml: 前一个UI的XML内容
        
    返回:
        bool: 如果UI结构相同返回True，否则返回False
    """
    if not previous_xml:
        return False
    
    try:
        # 解析XML内容
        current_elements = filter_xml_content(current_xml)
        previous_elements = filter_xml_content(previous_xml)
        
        # 如果元素数量不同，UI结构不同
        if len(current_elements) != len(previous_elements):
            return False
        
        # 比较每个元素的文本和位置
        for i, current_elem in enumerate(current_elements):
            previous_elem = previous_elements[i]
            
            # 比较文本
            if current_elem['text'] != previous_elem['text']:
                return False
            
            # 比较中心点坐标
            if current_elem['center'] != previous_elem['center']:
                return False
        
        # 所有元素都相同
        return True
    except Exception as e:
        print(f"比较UI结构时出错: {e}")
        return False 