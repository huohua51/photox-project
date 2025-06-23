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
from ai_classify import image_classification
from color import extract_colors_with_colorthief

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
                api_key = "sk-ff8f03a8cfbc03d7df75b7ddb6b1fb7f0bfc8116e02986306865aa9149741301"

                colors = extract_colors_with_colorthief(tmp_file_path, num_colors=2)
                result = image_classification(tmp_file_path, api_key)
                category_id = result['category_id']
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
                        category_id=category_id,  # 使用 category_id
                        colors=colors  # 使用 colors
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
                    tags_json = json.dumps(tags)

                    image = Image.objects.create(
                        image_url=image_url,
                        title=serializer.validated_data.get('title', ''),
                        tags=tags_json,  # 存入合法 JSON 字符串
                        user=request.user,
                        is_public=serializer.validated_data.get('is_public', False),
                        category_id=category_id,
                        colors=colors
                    )
                    # image = Image.objects.create(
                    #     image_url=image_url,
                    #     title=serializer.validated_data.get('title', ''),
                    #     tags=tags,
                    #     user=request.user,  # 上传者为当前认证的用户
                    #     is_public=serializer.validated_data.get('is_public', False),
                    #     category_id=category_id,  # 使用 category_id
                    #     colors=colors  # 添加颜色数据
                    # )
                    logger.info(f"数据库保存成功，图片ID: {image.id}")

                    # 自动创建对应类别的相册并添加图片
                    try:
                        # 获取类别名称
                        category_map = {
                            0: "风景", 1: "人物肖像", 2: "动物", 3: "交通工具", 4: "食品",
                            5: "建筑", 6: "电子产品", 7: "运动器材", 8: "植物花卉", 9: "医疗用品",
                            10: "办公用品", 11: "服装鞋帽", 12: "家具家居", 13: "书籍文档", 14: "艺术创作",
                            15: "工业设备", 16: "体育赛事", 17: "天文地理", 18: "儿童玩具", 19: "美妆个护",
                            20: "军事装备", 21: "宠物用品", 22: "健身器材", 23: "厨房用品", 24: "实验室器材",
                            25: "音乐器材", 26: "户外装备", 27: "珠宝首饰", 28: "虚拟场景", 29: "其他"
                        }
                        category_name = category_map.get(category_id, "其他")

                        # 查找或创建对应类别的相册
                        from albums.models import Album
                        album, created = Album.objects.get_or_create(
                            title=f"{category_name}相册",
                            user=request.user,
                            defaults={
                                'description': f'自动创建的{category_name}分类相册',
                                'is_public': False
                            }
                        )

                        # 将图片添加到相册
                        album.images.add(image)
                        logger.info(f"图片已添加到{category_name}相册")

                    except Exception as e:
                        logger.error(f"自动添加到相册失败: {str(e)}")
                        logger.error(traceback.format_exc())
                        # 这里我们不抛出异常，因为图片上传本身是成功的

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
    serializer_class = ImageSerializer  # 使用已有的序列化器

    # 自定义分页类，控制每页返回的图片数量
    class CustomPagination(PageNumberPagination):
        page_size = 10  # 默认每页显示10个图片
        page_size_query_param = 'page_size'
        max_page_size = 50  # 最大每页50个图片

    pagination_class = CustomPagination

    def get_permissions(self):
        # 如果请求公开图片，不需要认证
        is_public = self.request.query_params.get('is_public', None)
        if is_public is not None and str(is_public).lower() == 'true':
            return []
        # 否则需要认证
        return [IsAuthenticated()]

    def get_queryset(self):
        # 获取查询参数
        is_public = self.request.query_params.get('is_public', None)
        
        # 构建基础查询集
        queryset = Image.objects.all()
        
        # 如果指定了 is_public 参数
        if is_public is not None:
            # 将字符串转换为布尔值
            is_public = str(is_public).lower() == 'true'
            if is_public:
                # 如果是公开图片，返回所有公开的图片
                queryset = queryset.filter(is_public=True)
            else:
                # 如果是私有图片，只返回当前用户的图片
                if self.request.user.is_authenticated:
                    queryset = queryset.filter(user=self.request.user, is_public=False)
                else:
                    queryset = Image.objects.none()  # 未登录用户不能查看私有图片
        else:
            # 如果没有指定 is_public 参数，则只返回当前用户的图片
            if self.request.user.is_authenticated:
                queryset = queryset.filter(user=self.request.user)
            else:
                queryset = Image.objects.none()  # 未登录用户不能查看私有图片

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

