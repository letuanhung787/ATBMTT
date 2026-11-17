# Giao diện web A5/1 & TinyA5/1 — tài liệu đối chiếu mã nguồn

> Giao diện mặc định hiện là cửa sổ Tkinter (`py run_gui.py` hoặc `chay.bat`). Mở web bằng `py run_gui.py --web`. Tài liệu dưới đây cho giao diện web `giao_dien.html`, đồng bộ với mã ở `ui/web/`, `src/`, `ui/` và các bộ kiểm thử trên nhánh `main`. Đây là chương trình minh họa thuật toán phục vụ học tập, không phải giải pháp bảo mật dữ liệu thực tế.

## 1. Thành phần mã nguồn và cách chạy

| Tệp | Vai trò |
| --- | --- |
| `giao_dien.html` | Giao diện web độc lập đã được ghép sẵn để chạy offline. |
| `ui/web/index.html` | Cấu trúc giao diện, ô nhập và nút điều khiển. |
| `ui/web/styles.css` | Kiểu hiển thị. |
| `ui/web/core.js` | Hai lõi TinyA5/1 và A5/1 bằng JavaScript, xử lý bit/byte và vector đối chiếu. |
| `ui/web/app.js` | Chuyển tab, kiểm tra dữ liệu, hiển thị từng bước, xử lý file và tải kết quả. |
| `ui/web/build.py` | Ghép bốn tệp web thành `giao_dien.html`. |
| `src/tiny_a51.py` | Lõi TinyA5/1 Python dùng trong CLI và giao diện Tkinter. |
| `src/a51.py` | Lõi A5/1 Python. |
| `ui/binary.py`, `ui/gui.py`, `ui/cli.py` | Chế độ tính bit, giao diện Tkinter và CLI. |

**Chạy giao diện web:** mở `giao_dien.html` bằng Chrome/Edge. `chay.bat` hiện mở Tkinter. Chạy `py run_gui.py --web` để mở tệp HTML trong trình duyệt. Để mở giao diện Tkinter, chạy `py run_gui.py --desktop` (cần Python và Tkinter).

Bản HTML đã ghép **không cần** Python, Flask, npm, tài khoản hoặc Internet khi sử dụng. Nếu máy chặn việc mở tệp `file://`, có thể chạy `py -m http.server 8000` tại thư mục dự án rồi truy cập `http://localhost:8000/giao_dien.html`.

**Khi sửa nguồn web**, chạy tại thư mục chứa `README.md`:

```bash
python ui/web/build.py
```

Lệnh trên ghi lại `giao_dien.html`; không nên chỉ sửa trực tiếp bản HTML đã ghép vì lần build sau có thể ghi đè thay đổi. `ui/web/index.html` khi mở riêng cần các tệp CSS/JS cùng thư mục; tệp được phân phối để chạy độc lập là `giao_dien.html`.

## 2. Thuật toán theo mã nguồn hiện tại

Các chỉ số bit đều tính từ **0 ở bên trái thanh ghi**, là phía nạp feedback; khi dịch, feedback được thêm vào đầu mảng và bit cuối bị bỏ đi. Ba thanh ghi được dịch có điều kiện theo bit đa số (majority) của ba bit clock đã đọc **trước khi dịch**.

### 2.1. TinyA5/1 (23 bit)

Trong `ui/web/core.js`, Tiny lấy khóa **đúng 23 ký tự 0/1** và cắt trực tiếp thành X (6 bit), Y (8 bit), Z (9 bit). Khóa này chính là trạng thái ban đầu của ba thanh ghi, không phải khóa GSM 64 bit. Không dùng số khung.

| Thanh ghi | Độ dài | Bit clock | Bit phản hồi XOR (tap) | Bit đầu ra |
| --- | ---: | --- | --- | --- |
| X / R1 | 6 | [1] | [2], [4], [5] | [5] |
| Y / R2 | 8 | [3] | [6], [7] | [7] |
| Z / R3 | 9 | [3] | [2], [7], [8] | [8] |

Mỗi bước: (1) đọc clock X[1], Y[3], Z[3]; (2) tính majority; (3) chỉ quay thanh ghi có bit clock bằng majority; (4) lấy **S = X[5] XOR Y[7] XOR Z[8] từ trạng thái sau quay**; (5) tính bit kết quả `C = P XOR S`. Giải mã thực hiện cùng phép XOR bằng một bộ mã mới khởi tạo cùng khóa.

**Ví dụ web dùng để đối chiếu đặc tả Chương 4 của PDF:**

```text
Khóa Tiny: 10010101001110100110000
Plaintext: 111
Keystream: 100
Ciphertext: 011
Giải mã 011 với cùng khóa: 111
```

**Đối chiếu với `src/tiny_a51.py`:** Theo các phép gán và lệnh thực thi trong `TinyA51Cipher.step_verbose()`, lõi Python hiện dùng **cùng vị trí clock, tap và phép XOR bit đầu ra sau quay** như lõi web. Các chú thích về clock, tap và thứ tự lấy S trong lõi Python đã được cập nhật theo các lệnh đang thực thi.

Tuy vậy, **định dạng khóa không giống nhau ở mọi chế độ**:

- Web ở cả ba tab: Tiny nhận **trạng thái 23 bit trực tiếp**; ở `ui/binary.py` của Tkinter cũng nhận trạng thái 23 bit trực tiếp.
- `TinyA51(key)` trong Python (dùng cho CLI; giao diện Tkinter hiện dùng khóa 23 bit trực tiếp ở cả hai tab): nhận **số nguyên không dấu 32 bit**, chuyển thành trạng thái 23 bit bằng `(key & ((1 << 23) - 1)) ^ (key >> 23)`, sau đó tách bit **thấp trước** thành ba thanh ghi 6/8/9 bit.
- Vì cách chuyển khóa khác nhau, **không nhập một giá trị khóa theo hai định dạng rồi mặc định sẽ có cùng dòng khóa**. Chỉ so sánh kết quả khi ba thanh ghi bắt đầu ở đúng cùng trạng thái.

### 2.2. A5/1 đầy đủ (64 bit)

`ui/web/core.js` và `src/a51.py` dùng ba thanh ghi, clock và tap sau:

| Thanh ghi | Độ dài | Bit clock | Bit phản hồi XOR (tap) | Bit đầu ra |
| --- | ---: | --- | --- | --- |
| R1 | 19 | [8] | [13], [16], [17], [18] | [18] |
| R2 | 22 | [10] | [20], [21] | [21] |
| R3 | 23 | [10] | [7], [20], [21], [22] | [22] |

- Khóa web: số nguyên thập phân hoặc hex có tiền tố `0x`, trong khoảng 0 đến `2^64 - 1` (các số nhỏ hơn được hiểu như khóa 64 bit có thêm bit 0 ở đầu).
- Frame: số nguyên thập phân hoặc hex, từ 0 đến `2^22 - 1`.
- Ban đầu cả ba thanh ghi bằng 0. Nạp 64 bit khóa bằng cách xử lý lần lượt 8 byte theo thứ tự **big-endian**, nhưng nạp **bit thấp trước trong từng byte**; sau đó nạp 22 bit frame theo thứ tự bit thấp trước.
- Khi nạp, cả ba thanh ghi đều quay và XOR bit nạp vào feedback. Tiếp theo chạy **100 nhịp majority** để khởi động, chưa xuất dòng khóa. Mỗi nhịp sinh dòng khóa sau đó quay theo majority rồi lấy XOR các bit cuối.
- `src/a51.py` nhận danh sách 64 bit đã sắp đúng thứ tự nạp và số frame nguyên, thay vì trực tiếp nhận chuỗi thập phân/hex. `ui/gui.py` đảm nhận chuyển khóa số thành dãy bit tương ứng.

Web đối chiếu 2 burst, mỗi burst 114 bit, của vector tham chiếu Briceno/Goldberg/Wagner (thêm 6 bit 0 để đóng gói mỗi burst thành 15 byte):

```text
Khóa: 0x1223456789ABCDEF
Frame: 0x134
114 bit đầu:  534eaa582fe8151ab6e1855a728c00
114 bit tiếp: 24fd35a35d5fb6526d32f906df1ac0
```

Đây là vector tham chiếu A5/1, **không phải** vector NIST hoặc RFC.

## 3. Giao diện và luồng xử lý thực tế

Trên thanh công cụ: chọn `TinyA5/1` hoặc `A5/1 GSM`; trường frame chỉ xuất hiện với A5/1. Nút **Nạp ví dụ** cập nhật khóa và dữ liệu mẫu. Nút **Kiểm thử đối chiếu** hiển thị kết quả kỳ vọng/thực tế cùng trạng thái PASS/FAIL. Đổi thuật toán sẽ nạp lại ví dụ.

### 3.1. Tab Nhị phân

Có hai khung **Mã hóa** và **Giải mã**. Nhập chuỗi bit không rỗng, chỉ gồm `0`/`1`, tối đa **4096 bit** để hiển thị từng bước. Tiny cần khóa nhị phân 23 bit; A5/1 cần khóa số 64 bit và frame 22 bit theo cách nhập nêu trên. Sau khi mã hóa có nút đưa bản mã và khóa sang khung giải mã; muốn giải mã đúng A5/1 cũng phải giữ **cùng frame**.

Bộ mô phỏng hiển thị mỗi bit qua **ba pha**: «Trước khi quay», «Quyết định quay theo majority», «Sau khi quay · sinh bit S». Có nút **Trước**, **Phát/Tạm dừng** và **Tiếp**; phát tự động chuyển pha khoảng **700 ms/lần**. Phần thông tin gồm bit clock trước quay, majority, các thanh ghi quay/giữ, bit S, phép XOR và dòng khóa lũy tích. Ở pha sau quay, bit clock được tô trên **trạng thái mới**, nhưng giá trị quyết định quay vẫn là giá trị đọc **trước khi quay**.

### 3.2. Tab Văn bản UTF-8

- Mã hóa: dùng `TextEncoder` chuyển văn bản thành UTF-8, xử lý các byte bằng XOR dòng khóa, hiển thị ciphertext dạng **hex**.
- Giải mã: kiểm tra hex có đủ cặp ký tự, chuyển thành byte, giải mã, rồi dùng `TextDecoder('utf-8', {fatal: true})`. Nếu kết quả không phải UTF-8 hợp lệ, giao diện báo lỗi.
- Giới hạn tối đa **65.536 byte (64 KiB)** cho văn bản đầu vào sau khi đổi sang byte. Không có bộ mô phỏng từng pha trong tab này.
- Không nhầm chuỗi ký tự `111` (UTF-8 gồm ba byte) với bản rõ **3 bit** `111` trong tab Nhị phân.

### 3.3. Tab File thật

Người dùng chọn file trên máy, nhập khóa, rồi nhấn **Mã hóa file** hoặc **Giải mã file**. Web đọc file vào bộ nhớ bằng `arrayBuffer()`, xử lý trong trình duyệt theo khối **4096 byte**, nhưng dùng **cùng một đối tượng Cipher** xuyên suốt để giữ trạng thái dòng khóa. Giới hạn mỗi file **2 MiB**.

File mã hóa được tải về với đuôi `.a51`. Khi giải mã, nếu tên kết thúc bằng `.a51` thì bỏ đuôi đó; nếu không thì thêm `.restored`. Chương trình tạo URL tải xuống từ `Blob` và giải phóng URL khi cần. Nội dung file **chỉ gồm các byte kết quả**; không có header lưu khóa, thuật toán, frame, IV hoặc mã xác thực. Chọn sai thiết lập có thể tạo dữ liệu sai mà không được phát hiện.

Tính năng web vận hành tại máy người dùng, không có lệnh gửi file lên server. Không dùng khóa/dòng khóa lặp lại để bảo vệ dữ liệu thật; A5/1 và TinyA5/1 chỉ dùng ở đây để giảng dạy.

## 4. Kiểm tra và giới hạn của kết quả

Chạy tại thư mục gốc dự án (thư mục chứa `tests/`):

```bash
node tests/web_core.cjs
python tests/web_ui.py
python -m pytest -q
```

- `tests/web_core.cjs` kiểm tra vector Tiny, 2 burst A5/1, mã hóa/giải mã UTF-8 và byte, xử lý theo khối, và từ chối đầu vào sai.
- `tests/web_ui.py` kiểm tra thao tác giao diện và file qua **Playwright + Chromium** (cần cài riêng cho kiểm thử trình duyệt, không phải yêu cầu để dùng HTML).
- `tests/test_vectors.py` kiểm thử lõi Python, vector tham chiếu A5/1, Tiny, CLI và lỗi đầu vào.

Các lệnh là **hướng dẫn chạy bộ kiểm thử có trong repository**, không hàm ý các bài test đã được chạy trong lần cập nhật tài liệu này. Lõi web và lõi Python được triển khai bằng hai ngôn ngữ khác nhau; khi thay đổi bất kỳ lõi nào, cần kiểm tra lại vector và tính tương thích trước khi tuyên bố kết quả của hai giao diện giống nhau.

## 5. Nguồn tham khảo và lưu ý

Tài liệu PDF được nhóm dùng để tham khảo bố cục và ví dụ TinyA5/1: `1007410230-Khung-Bao-Cao-Mon-an-Toan-Bảo-Mật-Thong-Tin.pdf` (Chương 4, hình 3–5, trang PDF 19–21), theo ghi nhận trong tài liệu cũ. **Đặc tả hành vi trong tài liệu này được ưu tiên đối chiếu với source code hiện có trên GitHub**, không suy diễn rằng mã nguồn web được lấy từ mã tác giả PDF.

Với cùng cấu trúc LFSR, vẫn cần thống nhất **khóa/trạng thái đầu vào, thứ tự nạp bit, thời điểm lấy S, và frame** trước khi so sánh mã hóa giữa Python, Tkinter, CLI và web. 
