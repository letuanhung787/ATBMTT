# ATBMTT — Hệ mã dòng A5/1 và TinyA5/1

An toàn và Bảo mật thông tin — Nhóm 9. Chương trình minh họa mã hóa và giải mã bằng A5/1 và TinyA5/1, có giao diện cửa sổ Tkinter, giao diện web offline, mô phỏng thanh ghi và bộ kiểm thử.

## 1. Thành viên nhóm

- Trịnh Duy Thành
- Nguyên Như Chí Kiên
- Lê Tuấn Hưng
- Nguyễn Thanh Thảo

## 2. Chức năng chính

- Mã hóa và giải mã với **A5/1** và **TinyA5/1**.
- Xử lý chuỗi bit, văn bản UTF-8 và file.
- Mô phỏng các bước dịch thanh ghi, tính majority và tạo dòng khóa.
- Kiểm thử và đối chiếu kết quả thuật toán.
  
## 3. Cấu trúc mã nguồn

```text
ATBMTT/
├── README.md                   # Hướng dẫn cài đặt và chạy
├── chay.bat                    # Mở chương trình trên Windows
├── run_gui.py                  # Khởi chạy bằng Python
└── ATBMTT-main/
    └── ATBMTT-main/
        ├── giao_dien.html      # Giao diện web offline
        ├── chay.bat
        ├── run_gui.py
        ├── requirements.txt    # Phụ thuộc Python
        ├── src/                # Thuật toán A5/1 và TinyA5/1
        ├── ui/                 # Giao diện web, Tkinter và CLI
        ├── tests/              # Bộ kiểm thử
        ├── attacks/            # Mã minh họa
        ├── data/               # Dữ liệu mẫu
        └── docs/               # Tài liệu chi tiết
```

## 4. Yêu cầu môi trường và cài đặt

Giao diện mặc định là **cửa sổ Tkinter** như hình demo. Cần **Python 3.10+**, có thành phần **Tcl/Tk** (bộ cài Python trên Windows thường có sẵn). Bản web offline vẫn mở được bằng Chrome/Edge mà không cần Python.

Để chạy chương trình hoặc kiểm thử mã nguồn, sử dụng **Python 3.10+**. Tải dự án bằng Git hoặc chọn **Code → Download ZIP** trên GitHub:

```bash
git clone https://github.com/playforfreeinhere/ATBMTT.git
cd ATBMTT
```

Cài đặt các thư viện cho phần Python và kiểm thử:

```powershell
cd ATBMTT-main/ATBMTT-main
py -m pip install -r requirements.txt
```

## 5. Hướng dẫn chạy chương trình

**Cách 1 — Windows:**

Tải và giải nén toàn bộ dự án, cài Python có Tcl/Tk rồi nhấp đúp **`chay.bat`**. Chương trình mở cửa sổ với hai tab **Nhị phân / Tính tay** và **Văn bản / File**. Thuật toán, khóa và frame dùng chung cho hai tab. Tiny nhận khóa nhị phân đúng 23 bit; A5/1 nhận khóa 64 bit và frame 22 bit ở dạng số thập phân hoặc `0x...`.

**Cách 2 — Python:**
Tại thư mục ngoài cùng của dự án, chạy:

```powershell
py run_gui.py
```

Để mở giao diện web thay vì cửa sổ:

```powershell
py run_gui.py --web
```

Trong tab **Văn bản / File**, nhập văn bản → Mã hóa → Đưa kết quả lên đầu vào → Giải mã. Các nút **Mã hóa file... / Giải mã file...** mở hộp chọn file và tên đầu ra mới; không ghi đè file có sẵn. Để giải mã ảnh, chọn file `.a51`, giữ khóa/thuật toán/frame và mở file khôi phục bằng trình xem ảnh.

Tiny Python dùng clock 1/3/3, các tap 2/4/5, 6/7, 2/7/8 và lấy S sau khi dịch. Ví dụ khóa `10010101001110100110000`: `111 → 011 → 111`. Giao diện không dùng quy tắc Tiny cũ trong ảnh tham khảo.

**Chạy kiểm thử:** tại `ATBMTT-main/ATBMTT-main`:

```powershell
py -m pytest -q
```

Khi chỉnh sửa mã nguồn web trong `ui/web/`, tạo lại giao diện HTML bằng:

```powershell
py ui/web/build.py
```

## 6. Đóng góp của các thành viên

Mã nguồn được quản lý bằng **Git và GitHub**. Có thể xem lịch sử các thay đổi, người thực hiện và nội dung commit tại:

**[Lịch sử commit của dự án](https://github.com/playforfreeinhere/ATBMTT/commits/main/)**

---
