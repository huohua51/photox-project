import logging
import json
from rest_framework import serializers
from .models import Image

# 初始化日志记录器
logger = logging.getLogger(__name__)

def extract_first_label(tags_list):
    """
    从每个 tag 字符串中提取第一个有效标签词。
    支持格式如：'850: "teddy, teddy bear"' → 'teddy'
    """
    result = []
    for item in tags_list:
        try:
            # 分割冒号，取后面的部分
            label_str = item.split(":", 1)[1].strip()  # 如：'teddy, teddy bear'

            # 去除开头的单引号或双引号，并去除空格
            label_str = label_str.strip().strip("'").strip('"')

            # 取逗号前的第一个词
            first_label = label_str.split(",")[0].strip()

            result.append(first_label)
        except Exception as e:
            logger.error(f"解析标签失败: {e}, 原始项: {item}")
            continue  # 跳过错误项
    return result


def safe_load_tags(tags_data):
    """
    安全地将可能为字符串或多次编码的 JSON 数据转换成列表。
    处理多种格式：
      - 正常 list
      - JSON str (单层/双层编码)
      - 混乱格式（带多余引号或被错误 split）
    """
    if isinstance(tags_data, list):
        return tags_data

    if not isinstance(tags_data, str):
        return []

    # Step 1: 尝试直接解析原始字符串为 list
    try:
        parsed = json.loads(tags_data)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass  # 忽略错误继续尝试

    # Step 2: 如果仍然失败，可能是嵌套了多层 json.dumps()
    try:
        decoded_once = json.loads(tags_data)
        if isinstance(decoded_once, str):
            decoded_twice = json.loads(decoded_once)
            if isinstance(decoded_twice, list):
                return decoded_twice
        else:
            return decoded_once
    except json.JSONDecodeError:
        pass

    # Step 3: 如果还是失败，可能是字符串被错误切分（如 ["a", -> ['a', ...]）
    # 这里可以尝试修复一些常见格式问题
    try:
        # 修复常见的非法格式（比如被手动拼接破坏的字符串）
        fixed = tags_data.replace('\"', '"').replace("''", '"').replace(" '", " \"").replace("' ", "\" ")
        parsed_fixed = json.loads(fixed)
        if isinstance(parsed_fixed, list):
            return parsed_fixed
    except json.JSONDecodeError:
        pass

    # Step 4: 所有解析都失败，返回空列表
    logger.warning(f"无法解析 tags 字段: {tags_data}")
    return []


class ImageSerializer(serializers.ModelSerializer):
    """序列化Image模型"""
    tags_list = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField() 

    class Meta:
        model = Image
        fields = [
            'id', 'image_url', 'title', 'tags', 'tags_list',
            'user', 'created_at', 'is_public',
            'category_id', 'category', 'colors'
        ]
    
    def get_tags_list(self, obj):
        """获取标签列表"""
        return obj.get_tags_as_list()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        # 获取原始 tags 字段
        raw_tags = instance.tags

        # 安全解析并提取第一个标签词
        parsed_tags = safe_load_tags(raw_tags)
        clean_tags = extract_first_label(parsed_tags)

        # 替换原来的 tags 字段
        data['tags'] = clean_tags

        return data

    def get_category(self, obj):
        category_map = {
            0: "风景", 1: "人物肖像", 2: "动物", 3: "交通工具", 4: "食品",
            5: "建筑", 6: "电子产品", 7: "运动器材", 8: "植物花卉", 9: "医疗用品",
            10: "办公用品", 11: "服装鞋帽", 12: "家具家居", 13: "书籍文档", 14: "艺术创作",
            15: "工业设备", 16: "体育赛事", 17: "天文地理", 18: "儿童玩具", 19: "美妆个护",
            20: "军事装备", 21: "宠物用品", 22: "健身器材", 23: "厨房用品", 24: "实验室器材",
            25: "音乐器材", 26: "户外装备", 27: "珠宝首饰", 28: "虚拟场景", 29: "其他"
        }
        return category_map.get(obj.category_id, "未知")


class ImageUploadSerializer(serializers.Serializer):
    """处理图片上传请求"""
    image = serializers.ImageField()
    title = serializers.CharField(required=False, max_length=255)
    is_public = serializers.BooleanField(required=False, default=False)