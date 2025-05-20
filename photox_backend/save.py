# from qiniu import Auth, put_file, etag
# import qiniu.config
#
#
# def upload_to_qiniu(access_key, secret_key, bucket_name, file_path, key):
#     """
#     上传文件到七牛云存储
#     :param access_key: AK
#     :param secret_key: SK
#     :param bucket_name: 存储空间名
#     :param file_path: 本地文件路径
#     :param key: 上传到七牛云后的文件名（可包含路径）
#     :return: 外链URL或None
#     """
#     # 鉴权对象
#     q = Auth(access_key, secret_key)
#
#     # 生成上传凭证
#     token = q.upload_token(bucket_name, key, 3600)
#
#     # 上传文件
#     ret, info = put_file(token, key, file_path)
#
#     if ret and ret.get('key') == key:
#         # 构建外链URL（假设使用测试域名，生产环境建议绑定自定义域名）
#         base_url = 'https://portal.qiniu.com/cdn/domain/sv81ux7sp.hn-bkt.clouddn.com'  # 替换为你的空间域名
#         url = f'{base_url}/{key}'
#         return url
#     else:
#         print("上传失败:", info)
#         return None
#
#
# # 使用示例
# if __name__ == "__main__":
#     access_key = "EbD9A-35XSz-qMgyZ1D1odgh9ul5b6muX20ZS38W"
#     secret_key = "5ZvQ5yTJXduayu3bOh_36WbBLhfEpHZano-jLOGd"
#     bucket_name = "photox666"
#     local_file = "aaa.png"  # 本地图片路径
#     file_key = "images/aaa.png"  # 七牛云中的路径+文件名
#
#     url = upload_to_qiniu(access_key, secret_key, bucket_name, local_file, file_key)
#     if url:
#         print("文件外链:", url)

from qiniu import Auth, put_file
import time
import os
import traceback
import logging

logger = logging.getLogger(__name__)

def upload_and_set_metadata(access_key, secret_key, bucket_name, file_path, key, tags, category):
    """
    优化版的七牛云上传函数，增强错误处理和日志记录
    
    参数:
    - access_key: 七牛云访问密钥AK
    - secret_key: 七牛云密钥SK
    - bucket_name: 存储桶名称
    - file_path: 本地文件路径
    - key: 上传到七牛云后的文件名（可包含路径）
    - tags: 文件标签，列表或字符串
    - category: 文件分类
    
    返回:
    - 上传成功返回文件URL，失败返回None
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"要上传的文件不存在: {file_path}")
            return None
            
        logger.info(f"准备上传文件到七牛云: {file_path}")
        logger.info(f"文件大小: {os.path.getsize(file_path)} 字节")
        logger.info(f"目标key: {key}")
        logger.info(f"访问密钥: {access_key[:5]}...")
        logger.info(f"桶名: {bucket_name}")
        
        # 验证参数
        if not all([access_key, secret_key, bucket_name, file_path, key]):
            logger.error("上传参数不完整")
            return None
        
        # 初始化认证
        try:
            q = Auth(access_key, secret_key)
            logger.info("七牛云认证初始化成功")
        except Exception as e:
            logger.error(f"七牛云认证初始化失败: {str(e)}")
            return None

        # 生成上传凭证
        try:
            token = q.upload_token(bucket_name, key, 3600)
            logger.info(f"生成上传凭证成功")
        except Exception as e:
            logger.error(f"生成上传凭证失败: {str(e)}")
            return None
        
        # 上传文件
        try:
            ret, info = put_file(token, key, file_path)
            logger.info(f"上传结果: {ret}, 信息状态码: {info.status_code}")
        except Exception as e:
            logger.error(f"执行上传操作失败: {str(e)}")
            logger.error(traceback.format_exc())
            return None

        if ret and ret.get('key') == key:
            # 构建外链URL
            base_url = 'http://sv81ux7sp.hn-bkt.clouddn.com'
            file_url = f'{base_url}/{key}'
            logger.info(f"上传成功，文件URL: {file_url}")
            return file_url
        else:
            error_msg = info.text_body if hasattr(info, 'text_body') else str(info)
            logger.error(f"上传失败: {error_msg}")
            return None
    except Exception as e:
        logger.error(f"上传文件到七牛云出错: {str(e)}")
        logger.error(traceback.format_exc())
        return None


if __name__ == "__main__":
    # 测试上传
    access_key = "NT8GPMLylWq3_WIl9aNk1zAUWTJtoWrGGVqbvKxh"
    secret_key = "uNj2QCpEElzFF4ZkFkvjrBrDITB9ZpO_0ixDbfXD"
    bucket_name = "photoxw"
    local_file = "aa.png"
    file_key = f"images/{local_file}"
    tags = ["测试标签"]
    category = "测试分类"
    
    url = upload_and_set_metadata(access_key, secret_key, bucket_name, local_file, file_key, tags, category)
    if url:
        print("文件外链:", url)