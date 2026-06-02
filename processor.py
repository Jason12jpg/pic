import os
import re
from rembg import remove
from PIL import Image

def sanitize_seo_keyword(keyword):
    """
    1. 自动净化 SEO 关键词防呆机制
    处理前: "  Nike Air Max 2026 ! "
    处理后: "nike-air-max-2026"
    """
    if not keyword or not keyword.strip():
        return "product"  # 兜底名称，防止用户不输入
        
    # 强制转为全小写
    kw = keyword.lower().strip()
    # 移除非字母、数字、空格和连字符的特殊字符（如标点符号）
    kw = re.sub(r'[^a-z0-9\s\-]', '', kw)
    # 把空格或连续的空格、连字符替换为单个连字符 "-"
    kw = re.sub(r'[\s\-]+', '-', kw)
    
    return kw

def batch_process_images(input_dir, output_dir, raw_keyword):
    """
    2. 从“单张处理”升级为“文件夹批量遍历”
    3. 加入“容错机制 (Try-Except)”
    """
    # 净化用户输入的关键词
    seo_keyword = sanitize_seo_keyword(raw_keyword)
    print(f"🔄 关键词已自动优化为 SEO 标准格式: '{seo_keyword}'")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # 支持的图片格式后缀
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
    
    # 获取文件夹内所有合法图片文件
    all_files = os.listdir(input_dir)
    image_files = [f for f in all_files if f.lower().endswith(valid_extensions)]
    
    total_count = len(image_files)
    if total_count == 0:
        print(f"⚠️ 在输入文件夹 '{input_dir}' 中没有找到支持的图片文件！")
        return
        
    print(f"📦 找到 {total_count} 张待处理图片，开始批量抠图...\n" + "="*40)
    
    success_count = 0
    # 开始文件夹循环遍历
    for index, filename in enumerate(image_files, start=1):
        input_path = os.path.join(input_dir, filename)
        
        # 按照 SEO 规则拼接新文件名 (例如: nike-air-max-2026-1.png)
        new_filename = f"{seo_keyword}-{index}.png"
        output_path = os.path.join(output_dir, new_filename)
        
        # 3. 容错机制：Try-Except 捕获单张图片的异常
        try:
            print(f"[{index}/{total_count}] 正在处理: {filename} ...")
            
            # 打开并处理图片
            with Image.open(input_path) as img:
                # 转换色彩模式，防止某些带有 CMYK 的 JPG 图报错
                if img.mode in ('CMYK', 'P'):
                    img = img.convert('RGB')
                    
                no_bg_img = remove(img)
                no_bg_img.save(output_path, "PNG")
                
            print(f"✅ 成功! 已保存为 -> {new_filename}")
            success_count += 1
            
        except Exception as e:
            # 如果某张图片损坏或由于 .DS_Store 等系统文件干扰，报错跳过，不中断整个主程序
            print(f"❌ 错误: 无法处理图片 {filename}。原因: {e}。已自动跳过该文件。")
            
    print("="*40 + f"\n🎉 批量处理完成！成功: {success_count}/{total_count} 张。")

# --- 商业级测试运行 ---
if __name__ == "__main__":
    # 模拟买家的工作流
    INPUT_FOLDER = "./input"    # 卖家放原始图的文件夹
    OUTPUT_FOLDER = "./output"  # 处理后透明图的文件夹
    
    # 如果没有 input 文件夹，自动建一个方便用户测试
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"✨ 已自动创建 '{INPUT_FOLDER}' 文件夹。请在里面放几张带背景的商品图片，然后重新运行代码。")
    else:
        # 故意模拟一个很不规范的用户输入，测试防呆机制
        user_input_keyword = "  Nike Air Max 2026 ! " 
        
        batch_process_images(INPUT_FOLDER, OUTPUT_FOLDER, user_input_keyword)
