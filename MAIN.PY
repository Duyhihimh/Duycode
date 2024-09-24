import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
from PIL import Image, ImageTk,ImageChops, ImageOps #chops ảnh cắt

class MaximizedWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("BÌNH NGUYÊN VÔ VỌNG")
        self.state('zoomed')  # Maximize the window

        # Tạo frame
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Tạo nút import image
        import_button = ttk.Button(main_frame, text="Import Image", command=self.import_image)
        import_button.pack(pady=10)

        # Tạo lable hiển thị path
        self.path_label = ttk.Label(main_frame, text="No image selected", wraplength=800)
        self.path_label.pack(pady=10)

        # Tạo frame chứa hai ảnh gốc là ELA1
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(expand=True, fill='both')        

        # Tạo label hiển thị ảnh gốc
        self.image_label = ttk.Label(image_frame)
        self.image_label.pack(side='left', expand=True, fill='both', padx=10)

        # Tạo label hiển thị ảnh ELA1
        self.ela_image_label = ttk.Label(image_frame)
        self.ela_image_label.pack(side='right', expand=True, fill='both', padx=10)
        
        # Tạo label hiển thị ảnh ELA2
        self.ela_image_labe2 = ttk.Label(image_frame)
        self.ela_image_labe2.pack(side='right', expand=True, fill='both', padx=10)
       

    def import_image(self):
        #chỉ đang chọn các loại file như png ,jpg ,jpeg ,gif ,bmp
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        
        if file_path:
            try:
                #Show đường dẫn image
                self.path_label.config(text=f"Image path: {file_path}")
                
                # Mở và réize image
                image = Image.open(file_path)
                image.thumbnail((800, 600))  # Resize 8 6, sau này phải resize tầm đó nhưng giữ tỉ lệ
                
                # Convert image cho tkinter
                photo = ImageTk.PhotoImage(image)
                
                # Update image label
                self.image_label.config(image=photo)
                self.image_label.image = photo  
                
                # Hiện ảnh ELA 1
                ela_image1 = self.perform_ela(image)
                ela_photo1 = ImageTk.PhotoImage(ela_image1)

                # Update lable ELA 1
                self.ela_image_label.config(image=ela_photo1)
                self.ela_image_label.image = ela_photo1

                # Hiện ảnh ELA 2 dạng màu trắng
                ela_image2 = self.calculate_ela(image)
                ela_photo2 = ImageTk.PhotoImage(ela_image2)

                # Update lable ELA 2
                self.ela_image_labe2.config(image=ela_photo2)
                self.ela_image_labe2.image = ela_photo2

            except Exception as e:
                #Ko load được ảnh
                self.path_label.config(text=f"Error loading image: {e}")

    def calculate_ela(self, image):
        # Chuyển đổi ảnh sang numpy array
        img_array = np.array(image)
        
        # Giảm chất lượng ảnh
        quality = 90
        img_compressed = ImageOps.exif_transpose(image.copy())
        img_compressed.save("temp.jpg", "JPEG", quality=quality)
        img_compressed = Image.open("temp.jpg")
        img_compressed_array = np.array(img_compressed)
        
        # Tính toán ELA
        ela = np.abs(img_array.astype(int) - img_compressed_array.astype(int))
        ela = np.mean(ela, axis=2)  # Trung bình các kênh màu nếu là ảnh màu
        
        # Chuẩn hóa và chuyển đổi thành ảnh
        ela = (ela * 255 / np.max(ela)).astype(np.uint8)
        ela_image2 = Image.fromarray(ela)
        ela_image2 = ela_image2.convert("RGB")  # Đảm bảo ảnh là RGB
        
        return ela_image2
    

    def perform_ela(self, image, quality=90):
        """
        :param image: Ảnh gốc.
        :param quality: Mức độ nén (compression quality)
        """
        # Lưu ảnh với chất lượng nén cụ thể, hiện tại cho 90 sau thêm entry get quality sau
        ela_temp_filename = "temp_ela.jpg"
        image.save(ela_temp_filename, 'JPEG', quality=quality)

        # Mở lại ảnh đã nén
        
        compressed_image = Image.open(ela_temp_filename)

        # Tính toán sự khác biệt giữa ảnh gốc và ảnh nén
        ela_image2 = ImageChops.difference(image, compressed_image)

        # scale diffrnt để rể quan sát
        extrema = ela_image2.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale = 255.0 / max_diff if max_diff != 0 else 1  # Bắt lỗi không chia cho 0
        ela_image2 = ela_image2.point(lambda p: p * scale)

        # Trả về ảnh ELA đã được xử lý
        return ela_image2


if __name__ == "__main__":
    app = MaximizedWindow()
    app.mainloop()
