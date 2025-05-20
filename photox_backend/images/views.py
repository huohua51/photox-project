# views.py
from django.conf import settings  # 导入 settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
import time
import json
import logging
import traceback
import os

from ai_image import ai_image
from .delete import delete_image_from_cloud
from .models import Image
from .serializers import ImageUploadSerializer, ImageSerializer
from save import upload_and_set_metadata  # 七牛云上传工具
from .tasks import ai_image_analysis

logger = logging.getLogger(__name__)

def welcome_view(request):
    return HttpResponse("Welcome to Photox API!")

class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]  # 只有认证用户才能上传
    parser_classes = [MultiPartParser]  # 处理 multipart/form-data 请求

    def post(self, request, *args, **kwargs):
        logger.info("开始处理图片上传请求...")
        try:
            # 记录请求信息
            logger.info(f"用户 {request.user.username} 尝试上传图片")
            logger.info(f"请求内容类型: {request.content_type}")
            logger.info(f"请求文件数量: {len(request.FILES)}")
            
            serializer = ImageUploadSerializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"表单数据验证失败: {serializer.errors}")
                return Response({
                    "code": 1,
                    "message": "表单数据验证失败",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
            logger.info("表单数据验证通过")
            
            # 检查是否有图片文件
            if 'image' not in request.FILES:
                logger.warning("请求中没有图片文件")
                return Response({
                    "code": 1,
                    "message": "没有提供图片文件"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 获取上传的图片文件
            image_file = request.FILES['image']
            logger.info(f"接收到上传的图片: {image_file.name}, 大小: {image_file.size} 字节")
            
            # 正式处理逻辑
            try:
                # 使用 FileSystemStorage 保存文件，生成临时路径
                fs = FileSystemStorage(location='/tmp')  # 存储到临时目录
                tmp_file_path = fs.save(image_file.name, image_file)  # 保存到临时目录
                tmp_file_path = fs.path(tmp_file_path)  # 获取文件的绝对路径
                logger.info(f"图片已保存到临时路径: {tmp_file_path}")

                # 使用原始图片名称或生成唯一文件名
                safe_filename = os.path.basename(image_file.name).replace(' ', '_')
                file_name = f"images/{str(time.time()).replace('.', '')}_{safe_filename}"
                logger.info(f"在七牛云中的存储路径: {file_name}")

                # 从环境变量获取七牛云的配置
                access_key = settings.QINIU_ACCESS_KEY
                secret_key = settings.QINIU_SECRET_KEY
                bucket_name = settings.QINIU_BUCKET_NAME
                logger.info(f"七牛云配置信息 - Access Key: {access_key[:5]}..., Bucket: {bucket_name}")

                if not all([access_key, secret_key, bucket_name]):
                    logger.error("七牛云配置不完整")
                    return Response({
                        "code": 1,
                        "message": "七牛云配置不完整，请配置环境变量"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 尝试AI分析，如果失败则使用默认值
                try:
                    logger.info("开始AI分析图片...")
                    tags, category = ai_image(tmp_file_path)
                    logger.info(f"AI分析结果 - 标签: {tags}, 分类: {category}")
                except Exception as e:
                    logger.error(f"AI分析图片失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    tags = ["未分类"]
                    category = "其他"
                    logger.info("使用默认标签和分类")

                # 上传图片到七牛云并获取外链 URL
                try:
                    logger.info("开始上传图片到七牛云...")
                    image_url = upload_and_set_metadata(
                        access_key=access_key,
                        secret_key=secret_key,
                        bucket_name=bucket_name,
                        file_path=tmp_file_path,  # 传递临时文件的绝对路径
                        key=file_name,  # 七牛云中的路径+文件名
                        tags=tags,
                        category=category
                    )
                    logger.info(f"上传结果 - URL: {image_url}")
                except Exception as e:
                    logger.error(f"上传到七牛云时发生异常: {str(e)}")
                    logger.error(traceback.format_exc())
                    # 删除临时文件
                    if os.path.exists(tmp_file_path):
                        fs.delete(tmp_file_path)
                    return Response({
                        "code": 1,
                        "message": f"上传到七牛云失败: {str(e)}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 删除临时文件
                logger.info("删除临时文件...")
                if os.path.exists(tmp_file_path):
                    fs.delete(tmp_file_path)

                if not image_url:
                    logger.error("图片URL为空")
                    return Response({
                        "code": 1,
                        "message": "上传到七牛云失败，未获取到图片URL"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 保存图片信息到数据库
                try:
                    logger.info("将图片信息保存到数据库...")
                    # 处理tags列表为JSON字符串
                    if isinstance(tags, list):
                        tags_json = json.dumps(tags)
                        logger.info(f"将标签列表转换为JSON字符串: {tags_json}")
                    else:
                        tags_json = tags
                    
                    image = Image.objects.create(
                        image_url=image_url,
                        title=serializer.validated_data.get('title', '') or safe_filename,
                        tags=tags_json,
                        user=request.user,  # 上传者为当前认证的用户
                        is_public=serializer.validated_data.get('is_public', False)
                    )
                    logger.info(f"数据库保存成功，图片ID: {image.id}")

                    # 构造成功响应
                    response_data = {
                        "code": 0,
                        "message": "图片上传成功",
                        "data": ImageSerializer(image).data  # 返回图片的序列化数据
                    }
                    logger.info("上传流程完成，返回成功响应")
                    return Response(response_data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.error(f"保存图片信息到数据库失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    return Response({
                        "code": 1,
                        "message": f"保存图片信息到数据库失败: {str(e)}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"图片上传处理过程中发生未预期的异常: {str(e)}")
                logger.error(traceback.format_exc())
                return Response({
                    "code": 1,
                    "message": f"服务器内部错误: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"处理请求时发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                "code": 1,
                "message": f"服务器错误: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImageListView(ListAPIView):
    permission_classes = [IsAuthenticated]  # 确保用户认证
    serializer_class = ImageSerializer  # 使用已有的序列化器

    # 自定义分页类，控制每页返回的图片数量
    class CustomPagination(PageNumberPagination):
        page_size = 10  # 默认每页显示10个图片
        page_size_query_param = 'page_size'
        max_page_size = 50  # 最大每页50个图片

    pagination_class = CustomPagination

    def get_queryset(self):
        # 只获取当前用户上传的图片
        user = self.request.user
        queryset = Image.objects.filter(user=user)

        # 获取排序参数
        ordering = self.request.query_params.get('ordering', '-created_at')  # 默认按创建时间降序排序

        return queryset.order_by(ordering)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ImageDetailView(APIView):
    permission_classes = [IsAuthenticated]  # 需要认证

    # GET 请求，获取图片详情
    def get(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"code": 1, "message": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ImageSerializer(image)
        return Response({
            "code": 0,
            "message": "Success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    # PUT 请求，修改图片信息
    def put(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"code": 1, "message": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        if image.user != request.user:
            raise PermissionDenied("You do not have permission to edit this image.")

        title = request.data.get('title', None)
        is_public = request.data.get('is_public', None)

        if title:
            image.title = title
        if is_public is not None:
            image.is_public = is_public

        image.save()

        serializer = ImageSerializer(image)

        return Response({
            "code": 0,
            "message": "Success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"code": 1, "message": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        # 只有图片的上传者可以删除该图片
        if image.user != request.user:
            raise PermissionDenied("You do not have permission to delete this image.")

        # # 删除图片文件（目前只实现了数据库的删除，七牛云上未删除）
        # delete_image_from_cloud(image.image_url)

        # 删除图片记录
        image.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

