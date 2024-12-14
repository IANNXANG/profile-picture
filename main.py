from PIL import Image, ImageOps
import os
import numpy as np

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        if os.path.isfile(img_path):
            with Image.open(img_path) as img:
                # 检查图像大小是否符合要求
                images.append(img.copy())  # 使用copy避免原始文件被修改
    return images

def get_image_diff(image1, image2):
    # 计算两张彩色图片的均方误差，针对RGB三个通道分别计算然后取平均
    diff = np.mean((np.array(image1, dtype=np.float32) - np.array(image2, dtype=np.float32)) ** 2, axis=(0,1))
    mean_diff = np.mean(diff)
    return mean_diff

def create_mosaic(target_image, source_images, block_size):
    target_width, target_height = target_image.size
    mosaic_image = Image.new('RGB', (target_width, target_height))

    # 计算可以容纳多少个完整的block
    num_blocks_width = target_width // block_size
    num_blocks_height = target_height // block_size

    for y in range(num_blocks_height):
        for x in range(num_blocks_width):
            # 确保每个block的尺寸是正确的
            target_block = target_image.crop((x * block_size, y * block_size, (x + 1) * block_size, (y + 1) * block_size))
            best_match_index = min(range(len(source_images)), key=lambda i: get_image_diff(target_block, source_images[i]))
            best_match = source_images[best_match_index]
            mosaic_image.paste(best_match, (x * block_size, y * block_size))

    # 处理剩余的宽度部分
    for y in range(num_blocks_height):
        if target_width % block_size != 0:
            x = num_blocks_width
            target_block = target_image.crop((x * block_size, y * block_size, target_width, (y + 1) * block_size))
            best_match_index = min(range(len(source_images)), key=lambda i: get_image_diff(target_block.resize((block_size, block_size)), source_images[i]))
            best_match = source_images[best_match_index].resize((target_width - x * block_size, block_size))
            mosaic_image.paste(best_match, (x * block_size, y * block_size))

    # 处理剩余的高度部分
    for x in range(num_blocks_width):
        if target_height % block_size != 0:
            y = num_blocks_height
            target_block = target_image.crop((x * block_size, y * block_size, (x + 1) * block_size, target_height))
            best_match_index = min(range(len(source_images)), key=lambda i: get_image_diff(target_block.resize((block_size, block_size)), source_images[i]))
            best_match = source_images[best_match_index].resize((block_size, target_height - y * block_size))
            mosaic_image.paste(best_match, (x * block_size, y * block_size))

    # 处理右下角剩余部分
    if target_width % block_size != 0 and target_height % block_size != 0:
        x = num_blocks_width
        y = num_blocks_height
        target_block = target_image.crop((x * block_size, y * block_size, target_width, target_height))
        best_match_index = min(range(len(source_images)), key=lambda i: get_image_diff(target_block.resize((block_size, block_size)), source_images[i]))
        best_match = source_images[best_match_index].resize((target_width - x * block_size, target_height - y * block_size))
        mosaic_image.paste(best_match, (x * block_size, y * block_size))

    return mosaic_image

# 设置参数
block_size = 32  # 图片库中每张图片的大小（需要和required_size一致）
source_folder = 'bird'  # 图片库路径
target_image_path = '微信头像.jpg'  # 目标图片路径


# 加载图片库
source_images = load_images_from_folder(source_folder)

if not source_images:
    print("No valid images found in the source folder.")
else:
    # 加载目标图片
    target_image = Image.open(target_image_path)

    # 创建马赛克图片
    mosaic_image = create_mosaic(target_image, source_images, block_size)

    # 保存结果
    mosaic_image.save('微信头像拼接图.jpg')