class TinyA51Cipher:
    """
    Lớp cài đặt core thuật toán TinyA5/1.
    Cấu trúc 3 thanh ghi LFSR:
      - R1: 6 bits  (Clock bit: R1[2], Taps feedback: R1[2] ^ R1[5]) 
      - R2: 8 bits  (Clock bit: R2[3], Taps feedback: R2[4] ^ R2[7])
      - R3: 9 bits  (Clock bit: R3[3], Taps feedback: R3[5] ^ R3[8])
    """
    def __init__(self, r1_init: list[int], r2_init: list[int], r3_init: list[int]): #Khởi tạo trạng thái ban đầu cho 3 thanh ghi dạng mảng bit 0/1
        for bits, length in ((r1_init, 6), (r2_init, 8), (r3_init, 9)):             # Vòng lặp kiểm tra lần lượt 3 thanh ghi bits = r1 số nguyên độ dài 6 còn lại tg tự
            if len(bits) != length or any(bit not in (0, 1) for bit in bits):       # Kiểm tra hai điều kiện số lượng bit dúng không ? Có ít nhất một giá trị 0 hoặc 1 không?
                raise ValueError(f"Register must contain exactly {length} bits") # Nếu phát hiện lỗi chương trình báo lỗi 
        self.r1 = list(r1_init)
        self.r2 = list(r2_init)
        self.r3 = list(r3_init) # Ba dòng này sao chép trạng thái ban đầu vào các thuộc tính của đối tượng.
        
    def _get_majority(self, c1: int, c2: int, c3: int) -> int: # Hàm tính bit đa số trả về một bit chiếm đa số
        return 1 if (c1 + c2 + c3) >= 2 else 0                 # Nếu tổng ba bit từ 2 trở lên trả về 1 còn lại trả về 0
    def _clock_r1(self) -> int: # Khởi tạo hàm dịch thanh ghi r1 một lần (R1 có 6 bit)
        feedback = self.r1[2] ^ self.r1[4] ^ self.r1[5]  # Bit phản hồi : Lấy bit ở vị trí 2 XOR với bit ở vị trí 4 XOR với bit ở vị trí 5   
        self.r1 = [feedback] + self.r1[:-1] # bit của r1 mới sẽ là : bit đầu : bit phản hồi vừa tính ; những bit còn lại sẽ bỏ bit cuối, dịch tất cả các bit sang phải 1 vị trí
         return feedback # Trả về bit phản hồi để ghi vào log
    def _clock_r2(self) -> int: # Tương tự R1 nhưng bit phản hồi sử dụng bit ở vị trí 6 và 7 (R2 có 8 bit)
        feedback = self.r2[6] ^ self.r2[7] 
        self.r2 = [feedback] + self.r2[:-1]
        return feedback
    def _clock_r3(self) -> int: # Tương tự R1 nhưng bit phản hồi sử dụng bit ở vị trí 2, 7 và 8 (R3 có 9 bit)
        feedback = self.r3[2] ^ self.r3[7] ^ self.r3[8]
        self.r3 = [feedback] + self.r3[:-1]
        return feedback
    def step_verbose(self, step_number: int) -> tuple[int, dict]: # Khởi tạo hàm sinh dòng khóa dùng để khai báo một phương thức thực hiện 1 nhịp và xuất ra thông tin chi tiết (verbose) về trạng thái bên trong của nhịp đó
        """ Thực hiện 1 nhịp xử lý:
          1. Lấy bit keystream S từ trạng thái hiện tại (R1[5] ^ R2[7] ^ R3[8]).
          2. Tìm Majority bit từ 3 clock bit (R1[2], R2[3], R3[3]).
          3. Dịch nhịp các thanh ghi khớp với Majority bit.
          4. Trả về bit keystream và log trạng thái trung gian."""
        c1, c2, c3 = self.r1[1], self.r2[3], self.r3[3] # Cú pháp gán đồng thời ba biến c1 = R1[2], c2 = R2[3], c3 = R3[3]
        maj = self._get_majority(c1, c2, c3) # Tính và lưu lại bit chiếm đa số (majority) từ ba bit c1, c2, c3 
        # Xác định các thanh ghi cần dịch ( '==' : so sánh rồi trả về True hoặc False)
        clock_r1 = (c1 == maj) 
        clock_r2 = (c2 == maj)
        clock_r3 = (c3 == maj)
        # Dịch các thanh ghi và ghi lại feedback ; nếu điều kiện đúng thì trả về clock(giá trị bit phản hồi mới tính đc 0 hoặc 1), ngược lại trả về None
        fb1 = self._clock_r1() if clock_r1 else None
        fb2 = self._clock_r2() if clock_r2 else None
        fb3 = self._clock_r3() if clock_r3 else None
        keystream_bit = self.r1[5] ^ self.r2[7] ^ self.r3[8] # bit dòng khóa đầu tiên = bit vị trí 5 của R1 XOR bit vị trí 7 của R2 XOR bit vị trí 8 của R3
        # Đóng gói thông tin log trung gian
        log_data = { # Khởi tạo từ điển (lưu trữ trạng thái của nhịp xử lí hiện tại)
            "step": step_number, # Bước, thứ nhịp hiện tại
            "clock_bits": (c1, c2, c3), # 3 clock bit trước dịch
            "majority": maj, # Bit đa số
            "clocked": (clock_r1, clock_r2, clock_r3), # Thanh ghi đã được dịch
            "feedbacks": (fb1, fb2, fb3), # Bit phản hồi của từng thanh ghi
            "r1": list(self.r1), # Trạng thái sau dịch của từng bit
            "r2": list(self.r2),
            "r3": list(self.r3),
            "keystream_bit": keystream_bit # Bit dòng khóa trước dịch
        }
        return keystream_bit, log_data # Trả về bit dòng khóa vừa dịch và thông tin chi tiết của bước hiện tại
    def generate_keystream(self, length: int) -> tuple[list[int], list[dict]]: # Khởi tạo một dòng khóa gồm length bit và sinh chuỗi dòng khóa gồm N bit và xuất lịch sử log
        if not isinstance(length, int) or length < 0: # kiểm tra giá trị có phải số nguyên hay không? Độ dài âm có hợp lệ không?
            raise ValueError("Length must be a nonnegative integer") # Thông báo lỗi nếu độ dài không hợp lệ
        keystream = [] # Tạo danh sách chứa các bit dòng khóa
        logs = [] # Tạo danh sách chứa lịch sử từng bước
        for i in range(1, length + 1): # Vòng lặp điều khiển việc lặp lại quá trình sinh từng bit dòng khóa theo số lượng length
            ks_bit, log = self.step_verbose(i) # Thực hiện một nhịp, nhận bit dòng khóa và log.
            keystream.append(ks_bit) # Thêm bit vừa sinh vào dòng khóa
            logs.append(log) # Thêm thông tin vào lịch sử
        return keystream, logs # Trả về hai danh sách vừa tính
    def process_bits(self, bit_stream: list[int]) -> tuple[list[int], list[int], list[dict]]: # Khởi tạo hàm mã hóa hoặc giải mã chuỗi bit đầu vào bằng phép toán XOR với đầu vào là dsach các bit 0,1 và đầu ra là bộ 3 dữ liệu gồm chuỗi bit kqua sau khi mã hóa/ giải mã; chuỗi bit dòng khóa và lịch sử trạng thái thanh ghi qua từng nhịp
        """ Mã hóa / Giải mã chuỗi bit bản rõ bằng phép toán XOR.
        XOR có tính chất đối xứng (P ^ S = C và C ^ S = P) nên hàm xử lý được cả 2 chiều."""
        if any(bit not in (0, 1) for bit in bit_stream): # Kiểm tra đầu vào có phải là bit 0 hoặc 1 không?
            raise ValueError("Input must contain only bits") # Báo lỗi nếu có giá trị khác
        keystream, logs = self.generate_keystream(len(bit_stream)) # khóa sinh dòng, lsu có số bit bằng đúng số bit đầu vào
        output_bits = [b ^ k for b, k in zip(bit_stream, keystream)] # Ghép (zip) từng bit đầu vào (b) với từng bit dòng khóa (k) sau đó XOR
        return output_bits, keystream, logs # Trả về chuỗi bit đầu ra, chuỗi bit dòng khóa và lịch sử chi tiết các nhịp dịch
class TinyA51(TinyA51Cipher):
    def __init__(self, key: int): # Khởi tạo hàm tạo nhận khóa số nguyên
        if not isinstance(key, int) or not 0 <= key < (1 << 32): # Kiểm tra khóa có phải là số nguyên không dấu 32 bit
            raise ValueError("TinyA51 key must be a 32-bit unsigned integer") # Báo lỗi nếu khóa không hợp lệ
        state = (key & ((1 << 23) - 1)) ^ (key >> 23) # Chuyển khóa 32 bit thành TT 23 bit (Dùng mặt nạ bit để giữ lại đúng 23 bit thấp (0-22), dịch phải 23 vị trí để lấy ra 9 bit cao còn lại (23-31), rồi trộn hai phần này lại bằng phép XOR)  
        bits = [(state >> i) & 1 for i in range(23)] # Tách số nguyên state thành danh sách 23 bit, bit thấp trước (Chạy từ 0-22 rồi dịch phải i vị trí cuối cùng lấy bit thấp nhất sau khi dịch).
        super().__init__(bits[:6], bits[6:14], bits[14:]) # Gọi hàm khởi tạo của lớp cha TinyA51Cipher, chia danh sách thành 3 phần chính: bits[:6] có chỉ số được lấy 0-5 của thanh ghi R1(6 bit); bits[6:14] có chỉ số được lấy 6-13 của thanh ghi R2(8 bit); bits[14:] có chỉ số được lấy 14-22 của thanh ghi R3(9 bit)
   
    def keystream_bytes(self, length: int) -> bytes: # Khởi tạo hàm sinh dòng khóa theo bytes
        if not isinstance(length, int) or length < 0: # Kiểm tra độ dài có phải là số nguyên âm hay không?
            raise ValueError("Length must be a nonnegative integer") # Báo lỗi và dừng hàm nếu độ dài không âm
        output = bytearray() # Tạo vùng chứa kết quả rỗng (bytearray cho phép thêm từng byte trong lúc xử lý)
        for _ in range(length): # Vòng lặp lặp length lần với mỗi lần lặp tạo ra một byte dòng khóa
            value = 0 # Khởi tạo giá trị byte đang tạo bằng 0
            for _ in range(8): # Vòng lặp lặp 8 lần (vì mỗi byte có 8 bit; dùng _ vì không cần sử dụng số thứ tự vòng lặp)
                bit, _ = self.step_verbose(0) # Gọi hàm thực hiện một nhịp Tiny A5/1  -> Hàm trả về : bit_dong_khoa, log (bit: giữ bit dòng khóa; _ : Nhận log nhưng k dùng; 0 : số thứ tự ghi vào log và không phải bit đầu vào và không reset thanh ghi)
                value = (value << 1) | bit # Ghép bit vừa sinh vào byte (dịch các bit đã có sang trái một vị trí; sau đó đưa bit mới vào vị trí cuối)  
            output.append(value) # Thêm byte (sau khi ghép đủ 8 bit) vào output (hàm nằm ngoài vòng lặp 8 bit nhưng vẫn nằm trong vòng lặp byte)
        return bytes(output) # Chuyển vùng chứa bytearray thành dữ liệu byte rồi trả về kết quả cuối
    def encrypt(self, data: bytes) -> bytes: # Khởi tạo hàm mã hóa (chuyển hàm dữ liệu dạng bytes sang bản mã dạng byte)
        return bytes(a ^ b for a, b in zip(data, self.keystream_bytes(len(data)))) # Trả về kết quả bản mã sau khi XOR bản dữ liệu và dòng khóa
    decrypt = encrypt # Hàm giải mã (Đặt tên decrypt cho cùng hàm xử lý với encrypt, vì:C = P XOR S và P = C XOR S)
#KHỐI THỰC THI THỬ NGHIỆM ĐỘC LẬP (DEMO)
if __name__ == "__main__":  # Chỉ chạy phần bên dưới khi thực thi file trực tiếp. Khi file được import, khối này không chạy.
    r1_init = [1, 0, 0, 1, 0, 1] # Ví dụ về ba thanh ghi R1,R2,R3.
    r2_init = [0, 1, 0, 0, 1, 1, 1, 0]
    r3_init = [1, 0, 0, 1, 1, 0, 0, 0, 0]
    cipher = TinyA51Cipher(r1_init, r2_init, r3_init) # Tạo bộ mã hóa từ trạng thái ba thanh ghi.
    plaintext_bits = [1, 1, 1] # Bản rõ gồm ba bit 111
    print("DEMO THUẬT TOÁN TINYA5/1") # In tiêu đề
    cipher_bits, keystream, logs = cipher.process_bits(plaintext_bits) # Mã hóa và nhận 3 kết quả: Danh sách bit bản mã, danh sách bit dòng khóa và lịch sử từng nhịp
    for log in logs: # Duyệt từng bản ghi trong lịch sử xử lý
        print(f"\n[Bước {log['step']}]") # Xuống dòng in các bước từ lịch sử hoặc dictionary
        print(f"  Clock bits (C1, C2, C3) : {log['clock_bits']}") # In ba bit điều khiển đọc trước khi dịch
        print(f"  Majority bit            : {log['majority']}") # In bit đa số
        print(f"  Thanh ghi được quay     : R1={log['clocked'][0]}, R2={log['clocked'][1]}, R3={log['clocked'][2]}") # In quyết định dịch của từng thanh ghi
        print(f"  Bit dòng khóa (S)       : {log['keystream_bit']}") # In bit dòng khóa sinh ra tại bước đó
    print("\n------------------------------------") # In đường phân cách
    print(f"Bản rõ (Plaintext) : {plaintext_bits}") # In bản rõ ban đầu
    print(f"Dòng khóa (Keystream): {keystream}") # In dữ liệu ban đầu
    print(f"Bản mã (Ciphertext)  : {cipher_bits}") # In kết quả XOR của bản rõ với dòng khóa
    # Kiểm thử giải mã khôi phục bản rõ
    decipher = TinyA51Cipher(r1_init, r2_init, r3_init) # Tạo bộ giải mã mới với trạng thái ban đầu giống bộ mã hóa
    recovered_bits, _, _ = decipher.process_bits(cipher_bits) # Xử lý bản mã bằng cùng phép XOR (Hàm trả về ba phần, nhưng chỉ giữ recovered_bits. Hai dấu _ thể hiện không cần dùng dòng khóa và log trả về.)
    print(f"Giải mã khôi phục   : {recovered_bits}") # In bản rõ khôi phục
    assert recovered_bits == plaintext_bits, "Lỗi: Giải mã không khớp bản rõ!" # Kiểm tra dữ liệu khôi phục bằng dữ liệu ban đầu báo lỗi nếu giải mã không khớp với bản rõ
    print("-> KIỂM THỬ THÀNH CÔNG: Giải mã khôi phục đúng 100% bản rõ ban đầu.") # In Thông báo
