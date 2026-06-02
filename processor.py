import os
import re
import threading
from tkinter import filedialog, messagebox
import customtkinter as ctk
from rembg import remove
from PIL import Image

# ==========================================
# 1. 核心商业逻辑（防呆净化机制）
# ==========================================
def sanitize_seo_keyword(keyword):
    if not keyword or not keyword.strip():
        return "product"  # 兜底名称
        
    kw = keyword.lower().strip()
    # 移除非字母、数字、空格和连字符的特殊字符
    kw = re.sub(r'[^a-z0-9\s\-]', '', kw)
    # 把空格或连续的连字符替换为单个连字符 "-"
    kw = re.sub(r'[\s\-]+', '-', kw)
    return kw

# ==========================================
# 2. 工业级 UI 界面与多线程交互
# ==========================================
class BulkImageProcessorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 窗口基础设置 ---
        self.title("电商图片 AI 批量抠图 & SEO 重命名神器 v1.0")
        self.geometry("650x550")
        ctk.set_appearance_mode("dark")  # 默认高端暗黑模式
        ctk.set_default_color_theme("blue")

        # --- 路径变量 ---
        self.input_dir = ""
        self.output_dir = ""

        # --- UI 栅格化行式布局 ---
        # 1. 大标题
        self.title_label = ctk.CTkLabel(self, text="E-commerce Image AI Optimizer", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # 2. 选择输入文件夹行
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(fill="x", padx=30, pady=10)
        self.input_label = ctk.CTkLabel(self.input_frame, text="待处理图片文件夹:", width=130, anchor="w")
        self.input_label.pack(side="left", padx=10, pady=10)
        self.input_entry = ctk.CTkEntry(self.input_frame, placeholder_text="请选择原始图片目录...", width=320)
        self.input_entry.pack(side="left", padx=10, pady=10)
        self.input_btn = ctk.CTkButton(self.input_frame, text="浏览", width=80, command=self.select_input_dir)
        self.input_btn.pack(side="left", padx=10, pady=10)

        # 3. 选择输出文件夹行
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.pack(fill="x", padx=30, pady=10)
        self.output_label = ctk.CTkLabel(self.output_frame, text="抠图完成存放地:", width=130, anchor="w")
        self.output_label.pack(side="left", padx=10, pady=10)
        self.output_entry = ctk.CTkEntry(self.output_frame, placeholder_text="请选择保存目录...", width=320)
        self.output_entry.pack(side="left", padx=10, pady=10)
        self.output_btn = ctk.CTkButton(self.output_frame, text="浏览", width=80, command=self.select_output_dir)
        self.output_btn.pack(side="left", padx=10, pady=10)

        # 4. 输入 SEO 关键词行
        self.keyword_frame = ctk.CTkFrame(self)
        self.keyword_frame.pack(fill="x", padx=30, pady=10)
        self.keyword_label = ctk.CTkLabel(self.keyword_frame, text="SEO 核心关键词:", width=130, anchor="w")
        self.keyword_label.pack(side="left", padx=10, pady=10)
        self.keyword_entry = ctk.CTkEntry(self.keyword_frame, placeholder_text="例如: Nike Air Max 2026 (自动净化格式)", width=420)
        self.keyword_entry.pack(side="left", padx=10, pady=10)

        # 5. 独家隐私承诺日志显示框
        self.log_textbox = ctk.CTkTextbox(self, width=590, height=180, font=ctk.CTkFont(family="Courier", size=12))
        self.log_textbox.pack(pady=15)
        self.log("💡 软件启动成功！完全本地化运行，100% 保护您的选品隐私。\n首次运行会自动下载约100MB的AI抠图模型，请保持联网。第二次使用可完全断网。")

        # 6. 一键启动核心 CTA 大按钮
        self.start_btn = ctk.CTkButton(self, text="🚀 一键开启批量 AI 抠图 & SEO 命名", font=ctk.CTkFont(size=16, weight="bold"), height=45, fg_color="#2cbb55", hover_color="#229944", command=self.start_processing_thread)
        self.start_btn.pack(pady=10)

    # --- 交互逻辑控制 ---
    def select_input_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.input_dir = directory
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, directory)

    def select_output_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir = directory
            self.output_entry.delete(0, "end")
            self.output_entry.insert(0, directory)

    def log(self, text):
        self.log_textbox.insert("end", text + "\n")
        self.log_textbox.see("end")

    def start_processing_thread(self):
        if not self.input_dir or not self.output_dir:
            messagebox.showerror("错误", "请先选择输入和输出文件夹！")
            return
        
        # 激活锁定状态，防止重复点击
        self.start_btn.configure(state="disabled", text="正在批量处理中...")
        
        # 开启后台异步线程，确保前台 GUI 丝滑拖动不卡死
        threading.Thread(target=self.run_batch_logic, daemon=True).start()

    def run_batch_logic(self):
        """核心执行主线：引入最高规格的 try...finally 结构"""
        try:
            raw_keyword = self.keyword_entry.get()
            seo_keyword = sanitize_seo_keyword(raw_keyword)
            
            self.log(f"\n[系统通知] 关键词已净化为 SEO 标准格式: '{seo_keyword}'")
            
            valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
            all_files = os.listdir(self.input_dir)
            image_files = [f for f in all_files if f.lower().endswith(valid_extensions)]

            total_count = len(image_files)
            if total_count == 0:
                self.log("⚠️ 提示: 输入文件夹里没有任何支持的图片格式！")
                return

            self.log(f"📦 发现 {total_count} 张待处理图片，AI 开始批量作业...\n" + "-"*50)

            success_count = 0
            for index, filename in enumerate(image_files, start=1):
                input_path = os.path.join(self.input_dir, filename)
                new_filename = f"{seo_keyword}-{index}.png"
                output_path = os.path.join(self.output_dir, new_filename)

                # 内部循环容错，确保单张坏图不影响全局
                try:
                    self.log(f"[{index}/{total_count}] 正在处理: {filename}...")
                    with Image.open(input_path) as img:
                        # 兼容性护城河：防止印刷级 CMYK 报错闪退
                        if img.mode in ('CMYK', 'P'):
                            img = img.convert('RGB')
                        no_bg_img = remove(img)
                        no_bg_img.save(output_path, "PNG")
                    
                    self.log(f"  └─ 改名成功: -> {new_filename}")
                    success_count += 1
                except Exception as single_error:
                    self.log(f"  └─ ❌ 无法处理此图片，原因: {single_error}。已自动跳过。")

            self.log("-"*50 + f"\n🎉 批量任务全部结束！成功率: {success_count}/{total_count}")
            messagebox.showinfo("大功告成", f"批量抠图已全部完成！\n成功处理 {success_count} 张图片。")
            
        except Exception as system_critical_error:
            # 捕获外部灾难性致命错误，并在日志中给出直观提示
            self.log(f"❌ 发生致命系统级错误: {system_critical_error}")
            messagebox.showerror("系统崩溃", f"程序遭遇未知异常，已被保护性拦截:\n{system_critical_error}")
        finally:
            # 无论发生什么情况，按钮状态必须无条件恢复解锁
            self.reset_button()

    def reset_button(self):
        self.start_btn.configure(state="normal", text="🚀 一键开启批量 AI 抠图 & SEO 命名")

# ==========================================
# 3. 独立程序启动入口
# ==========================================
if __name__ == "__main__":
    app = BulkImageProcessorApp()
    app.mainloop()
