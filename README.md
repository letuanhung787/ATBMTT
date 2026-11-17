# ATBMTT — Hệ mã dòng A5/1 và TinyA5/1 | Nhóm 9

Dự án môn **An toàn và Bảo mật thông tin**: triển khai và minh họa hệ mã dòng A5/1 GSM và TinyA5/1 (phiên bản rút gọn phục vụ học tập). Có giao diện web offline, chương trình Python/Tkinter, CLI, mã kiểm thử và ví dụ về rủi ro tái sử dụng dòng khóa.

## Thành viên

- Trịnh Duy Thành
- Nguyên Như Chí Kiên
- Lê Tuấn Hưng
- Nguyễn Thanh Thảo

## 1. Chạy chương trình nhanh nhất

**Trên Windows:** chọn **Code → Download ZIP** trên GitHub, giải nén, nhấp đúp `chay.bat` **ở thư mục ngoài cùng**. File này chuyển tiếp đến `ATBMTT-main/ATBMTT-main/chay.bat` để mở giao diện `giao_dien.html` trong trình duyệt. Không cần cài Python, Flask, npm hay kết nối Internet để sử dụng giao diện HTML đã ghép sẵn.

Ngoài ra có thể mở trực tiếp `ATBMTT-main/ATBMTT-main/giao_dien.html` bằng Chrome/Edge.

**Chạy từ terminal tại thư mục ngoài cùng của repository:**

```powershell
py run_gui.py
```

`run_gui.py` ngoài cùng chuyển đến chương trình bên trong. Để chạy giao diện Tkinter cũ:

```powershell
py run_gui.py --desktop
```

**Lưu ý:** không tách riêng `chay.bat` hoặc `run_gui.py` khỏi cây thư mục đã tải về. Không còn dùng `chay_web.bat` (đã được loại bỏ do trùng chức năng).

## 2. Chức năng

- **TinyA5/1:** 3 thanh ghi 6/8/9 bit, khóa web là trạng thái nhị phân **23 bit**, ví dụ khóa `10010101001110100110000`, plaintext `111` → ciphertext `011` → giải mã `111`.
- **A5/1 GSM:** 3 thanh ghi 19/22/23 bit, khóa 64 bit và số khung 22 bit; kiểm tra với hai burst 114 bit của vector tham chiếu Briceno/Goldberg/Wagner.
- **Nhị phân:** mã hóa, giải mã và xem các pha «Trước», «Quyết định majority», «Sau khi quay» bằng các nút Trước / Phát / Tạm dừng / Tiếp. Giới hạn 4096 bit cho phần mô phỏng.
- **Văn bản:** mã hóa văn bản UTF-8 thành hex và giải mã ngược; giới hạn dữ liệu đầu vào 64 KiB.
- **File:** xử lý file văn bản/ảnh/nhị phân tại máy, tối đa 2 MiB; mã hóa thêm đuôi `.a51`, giải mã bỏ đuôi đó hoặc thêm `.restored`.
- **Đối chiếu:** hiển thị kết quả kỳ vọng, thực tế và PASS/FAIL đối với ví dụ TinyA5/1 và vector A5/1.

Đây là công cụ minh họa, **không được dùng A5/1 hoặc TinyA5/1 để bảo vệ dữ liệu thực tế**. Bản mã không có cơ chế xác thực hay bảo vệ tính toàn vẹn; kết quả giải mã bằng khóa sai không nhất thiết sinh lỗi.

## 3. Cấu trúc repository

```text
ATBMTT/
├── README.md                       # Hướng dẫn chung duy nhất
├── chay.bat                        # Trình khởi chạy ở thư mục ngoài
├── run_gui.py                      # Chuyển tiếp vào chương trình trong
└── ATBMTT-main/
    └── ATBMTT-main/                # Thư mục dự án Python / web
        ├── chay.bat                # Mở giao diện HTML
        ├── run_gui.py              # Web mặc định; --desktop cho Tkinter
        ├── run_gui_doc_lap.py      # Bản Tkinter độc lập dự phòng
        ├── giao_dien.html          # Bản web offline đã ghép
        ├── requirements.txt
        ├── src/                    # a51.py, tiny_a51.py
        ├── ui/                     # binary.py, cli.py, gui.py, web/
        │   └── web/               # index.html, styles.css, core.js, app.js, build.py
        ├── tests/                  # pytest, kiểm thử lõi web/UI
        ├── attacks/                # Minh họa tái sử dụng dòng khóa
        ├── data/                   # File mẫu
        └── docs/                   # Tài liệu chi tiết
```

Trong các lệnh từ mục 4 trở đi, **chuyển vào thư mục dự án bên trong trước**:

```powershell
cd ATBMTT-main/ATBMTT-main
```

## 4. Cài đặt Python và chạy kiểm thử

Giao diện web offline không cần Python. Python 3.10+ dành cho CLI, Tkinter, chạy demo và kiểm thử; dùng `requirements.txt` để cài `pytest`:

```powershell
py -m pip install -r requirements.txt
py -m pytest -q
node tests/web_core.cjs
```

Kiểm thử trình duyệt `tests/web_ui.py` dùng Playwright và Chromium, cần cài riêng trong môi trường phát triển; chúng không phải phụ thuộc để chạy `giao_dien.html`.

```powershell
python tests/web_ui.py
```

Các bài test Python bao gồm kiểm tra vector A5/1, TinyA5/1, vòng mã hóa–giải mã, lỗi đầu vào, CLI và minh họa tái sử dụng dòng khóa. `tests/web_core.cjs` kiểm tra lõi JavaScript và vector đối chiếu.

## 5. Chạy CLI và các demo Python

**CLI TinyA5/1** sử dụng khóa là số nguyên không dấu 32 bit (thập phân hoặc hex), **khác định dạng khóa Tiny 23 bit trực tiếp của giao diện web**:

```powershell
python -m ui.cli encrypt data/sample_plain.txt data/sample_encrypted.bin 0x1A2B3C4D
python -m ui.cli decrypt data/sample_encrypted.bin data/sample_decrypted.txt 0x1A2B3C4D
```

CLI từ chối dùng cùng đường dẫn nguồn/đích và từ chối ghi đè file đầu ra đã tồn tại. Hãy chọn tên đầu ra chưa tồn tại khi chạy lại.

Các demo độc lập:

```powershell
python src/a51.py
python src/tiny_a51.py
python test.py
python -m attacks.keystream_reuse
```

`test.py` sử dụng các lõi trong `src/` và file demo tạm.

## 6. Giao diện Tkinter cũ và bản dự phòng

Từ thư mục dự án bên trong, có thể thiết lập môi trường Python riêng trên Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run_gui.py --desktop
```

Tkinter cần bộ cài Python hỗ trợ Tcl/Tk và môi trường đồ họa.

Giao diện Tkinter cũ có ba tab:
1. **Nhị phân / Tính tay:** Tiny nhận trạng thái 23 bit trực tiếp; A5/1 nhận khóa nhị phân 64 bit và frame nhị phân 22 bit, có bảng theo bước (tối đa 4096 bit).
2. **Văn bản:** UTF-8 ↔ hex. Tiny ở tab này nhận số nguyên 32 bit, rồi chuyển thành trạng thái 23 bit theo quy ước Python.
3. **File:** mã hóa/giải mã dữ liệu byte theo khối, giữ trạng thái dòng khóa. Bản Tkinter không ghi đè file đích đã có.

`run_gui_doc_lap.py` là bản Tkinter dự phòng. Nó có quy ước nhập liệu riêng (Tiny trực tiếp 23 bit), không phải giao diện web; không thay thế `run_gui.py` chính bằng file này khi không cần.

## 7. Quy ước thuật toán và API

**A5/1:**
- `src/a51.py` có lớp `A51Cipher(key_bits, frame_number)`: cần đúng 64 bit khóa theo thứ tự nạp và frame trong khoảng 22 bit.
- Với khóa số, biểu diễn thành **8 byte big-endian** và nạp **bit thấp trước trong từng byte**. Nạp frame bit thấp trước, khởi động 100 nhịp majority. Các thanh ghi dài 19/22/23 bit, bit clock là [8]/[10]/[10], tap R3 là [7,20,21,22].
- `process_bytes()` dùng cho cả mã hóa và giải mã. Vector tham chiếu sử dụng khóa `0x1223456789ABCDEF`, frame `0x134` và hai burst 114 bit.

**TinyA5/1:**
- `src/tiny_a51.py` có `TinyA51Cipher(r1, r2, r3)` nhận ba danh sách bit dài 6/8/9. Các clock là [1]/[3]/[3]; tap lần lượt [2,4,5] / [6,7] / [2,7,8]. Mỗi bit dòng khóa trong mã thực thi được lấy **sau khi quay**.
- `TinyA51(key)` nhận khóa nguyên không dấu 32 bit và biến thành trạng thái 23 bit bằng `(key & ((1 << 23) - 1)) ^ (key >> 23)`, chia 6/8/9 bit theo thứ tự bit thấp trước. Đây chỉ là cách khởi tạo minh họa, có thể cho trạng thái trùng nhau.
- `ui/web/core.js` dùng **chuỗi nhị phân 23 bit trực tiếp** làm trạng thái Tiny. Khác biệt đáng chú ý giữa web và CLI là **cách nhập/chuyển khóa**, không phải mặc định khác clock/tap. Các chú thích cũ trong một số tệp Python về vị trí clock hoặc thời điểm lấy S có chỗ không khớp lệnh thực thi; ưu tiên đối chiếu mã và bộ kiểm thử.
- Để giải mã, phải khởi tạo lại cipher từ cùng khóa/trạng thái ban đầu (và frame nếu là A5/1). Đối tượng đã xử lý dữ liệu sẽ tiếp tục tiến dòng khóa.

## 8. Phát triển giao diện và tài liệu

Chỉnh sửa mã nguồn HTML/CSS/JavaScript trong `ui/web/`, rồi tại thư mục dự án bên trong chạy:

```powershell
python ui/web/build.py
```

Lệnh tạo lại `giao_dien.html` độc lập; không chỉ chỉnh file ghép rồi quên cập nhật nguồn.

Tài liệu tham khảo:
- [Giao diện web: đặc tả, đối chiếu source và kiểm thử](ATBMTT-main/ATBMTT-main/docs/giao_dien_web.md)
- [Ví dụ tính tay TinyA5/1 phiên bản lưu trong docs](ATBMTT-main/ATBMTT-main/docs/tiny_hand_example.md) — **lưu ý:** nội dung mô tả cũ tại đây có thể khác các vị trí clock/tap đang thực thi; cần đối chiếu mã nguồn trước khi dùng làm đáp án.

## 9. Đóng góp và tài liệu nộp môn

Để thể hiện lịch sử đóng góp, có thể tạo nhánh riêng theo thành viên:

```bash
git clone https://github.com/playforfreeinhere/ATBMTT.git
git checkout -b feature/<ten-thanh-vien>
# Chỉnh sửa, commit, rồi đẩy nhánh
git push origin feature/<ten-thanh-vien>
```

Tài liệu nộp môn có thể gồm báo cáo Word (phân tích thuật toán, sơ đồ khối, tính tay ví dụ, phân công), slide thuyết trình và video demo 3–5 phút. Nếu dùng công cụ AI hỗ trợ viết hoặc kiểm thử, nhóm cần ghi nhận trung thực và tự xác minh kết quả.
