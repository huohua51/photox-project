from rest_framework import serializers
from .models import Image
import json

class ImageSerializer(serializers.ModelSerializer):
    """序列化Image模型"""
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = ['id', 'image_url', 'title', 'tags', 'tags_list', 'user', 'created_at', 'is_public']
    
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

class ImageUploadSerializer(serializers.Serializer):
    """处理图片上传请求"""
    image = serializers.ImageField()
    title = serializers.CharField(required=False, max_length=255)
    is_public = serializers.BooleanField(required=False, default=False)