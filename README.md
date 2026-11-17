# ATBMTT — Hệ mã dòng A5/1 và TinyA5/1

An toàn và Bảo mật thông tin — Nhóm 9. Chương trình minh họa mã hóa và giải mã bằng A5/1 và TinyA5/1, có giao diện web, mô phỏng thanh ghi và bộ kiểm thử.

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

Sử dụng **Windows và Chrome/Edge** để chạy giao diện HTML, không cần cài Python hay thư viện bổ sung.

Nếu muốn chạy bằng Python hoặc kiểm thử mã nguồn, sử dụng **Python 3.10+**. Tải dự án bằng Git hoặc chọn **Code → Download ZIP** trên GitHub:

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

Tải file zip ATBMTT, sau đó extract tất cả file, rồi nhấp vào **`chay.bat`** trong file đã extract. Giao diện sẽ hiện lên và chúng ta có thể mã hóa và giải mã theo mong muốn

**Cách 2 — Python:**
Tại thư mục ngoài cùng của dự án, chạy:

```powershell
py run_gui.py
```

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
