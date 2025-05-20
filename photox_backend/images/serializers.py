from rest_framework import serializers
from .models import Image
import json

class ImageSerializer(serializers.ModelSerializer):
    """序列化Image模型"""
    tags_list = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField() 
    
    class Meta:
        model = Image
        fields = ['id', 'image_url', 'title', 'tags', 'tags_list', 'user', 'created_at', 'is_public', 'category_id', 'category', 'colors']
    
    def get_tags_list(self, obj):
        """获取标签列表"""
        return obj.get_tags_as_list()
    
    def to_representation(self, instance):
        """自定义返回格式"""
        data = super().to_representation(instance)
        # 如果tags是列表，直接返回
        if isinstance(instance.tags, list):
            data['tags'] = instance.tags
        # 如果是已经是JSON字符串，就保持原样
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
