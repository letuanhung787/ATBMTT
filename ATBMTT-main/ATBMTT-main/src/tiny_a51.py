class TinyA51Cipher:
    """
    Lớp cài đặt core thuật toán TinyA5/1.
    Cấu trúc 3 thanh ghi LFSR:
      - R1: 6 bits  (Clock bit: R1[2], Taps feedback: R1[2] ^ R1[5]) 
      - R2: 8 bits  (Clock bit: R2[3], Taps feedback: R2[4] ^ R2[7])
      - R3: 9 bits  (Clock bit: R3[3], Taps feedback: R3[5] ^ R3[8])
    """
    def __init__(self, r1_init: list[int], r2_init: list[int], r3_init: list[int]): #Khởi tạo trạng thái ban đầu cho 3 thanh ghi dạng mảng bit 0/1
        for bits, length in ((r1_init, 6), (r2_init, 8), (r3_init, 9)): # Vòng lặp kiểm tra lần lượt 3 thanh ghi bits = r1 số nguyên độ dài 6 còn lại tg tự
            if len(bits) != length or any(bit not in (0, 1) for bit in bits): # Kiểm tra hai điều kiện số lượng bit dúng khoogn ? Có ít nhất một giá trị 0 hoặc 1 không?
                raise ValueError(f"Register must contain exactly {length} bits") # Nếu phát hiện lỗi chương trình báo lỗi 
        self.r1 = list(r1_init)
        self.r2 = list(r2_init)
        self.r3 = list(r3_init) # Ba dòng này sao chép trạng thái ban đầu vào các thuộc tính của đối tượng.
        
    def _get_majority(self, c1: int, c2: int, c3: int) -> int: # Hàm tính bit đa số trả về một bit chiếm đa số
        return 1 if (c1 + c2 + c3) >= 2 else 0 # Nếu tổng ba bit từ 2 trở lên trả về 1 còn lại trả về 0
    def _clock_r1(self) -> int: # Khởi tạo hàm dịch thanh ghi r1 một lần (R1 có 6 bit)
        feedback = self.r1[2] ^ self.r1[5]  # Bit phản hồi : Lấy bit ở vị trí 2 XOR với bit ở vị trí 5   
        self.r1 = [feedback] + self.r1[:-1] # bit của r1 mới sẽ là : bit đầu : bit phản hồi vừa tính ; những bit còn lại sẽ bỏ bit cuối, dịch tất cả các bit sang phải 1 vị trí
         return feedback # Trả về bit phản hồi để ghi vào log
    def _clock_r2(self) -> int: # Tương tự R1 nhưng bit phản hồi sử dụng bit ở vị trí 4 và 7 (R2 có 8 bit)
        feedback = self.r2[4] ^ self.r2[7] 
        self.r2 = [feedback] + self.r2[:-1]
        return feedback
    def _clock_r3(self) -> int: # Tương tự R1 nhưng bit phản hồi sử dụng bit ở vị trí 5 và 8 (R3 có 9 bit)
        feedback = self.r3[5] ^ self.r3[8]
        self.r3 = [feedback] + self.r3[:-1]
        return feedback
    def step_verbose(self, step_number: int) -> tuple[int, dict]: # Khởi tạo hàm sinh dòng khóa dùng để khai báo một phương thức thực hiện 1 nhịp và xuất ra thông tin chi tiết (verbose) về trạng thái bên trong của nhịp đó
        """ Thực hiện 1 nhịp xử lý:
          1. Lấy bit keystream S từ trạng thái hiện tại (R1[5] ^ R2[7] ^ R3[8]).
          2. Tìm Majority bit từ 3 clock bit (R1[2], R2[3], R3[3]).
          3. Dịch nhịp các thanh ghi khớp với Majority bit.
          4. Trả về bit keystream và log trạng thái trung gian."""
        keystream_bit = self.r1[5] ^ self.r2[7] ^ self.r3[8] # bit dòng khóa đầu tiên = bit vị trí 5 của R1 XOR bit vị trí 7 của R2 XOR bit vị trí 8 của R3
        c1, c2, c3 = self.r1[2], self.r2[3], self.r3[3] # Cú pháp gán đồng thời ba biến c1 = R1[2], c2 = R2[3], c3 = R3[3]
        maj = self._get_majority(c1, c2, c3) # Tính và lưu lại bit chiếm đa số (majority) từ ba bit c1, c2, c3 
        # Xác định các thanh ghi cần dịch ( '==' : so sánh rồi trả về True hoặc False)
        clock_r1 = (c1 == maj) 
        clock_r2 = (c2 == maj)
        clock_r3 = (c3 == maj)
        # Dịch các thanh ghi và ghi lại feedback ; nếu điều kiện đúng thì trả về clock(giá trị bit phản hồi mới tính đc 0 hoặc 1), ngược lại trả về None
        fb1 = self._clock_r1() if clock_r1 else None
        fb2 = self._clock_r2() if clock_r2 else None
        fb3 = self._clock_r3() if clock_r3 else None
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
            ks_bit, log = self.step_verbose(i)
            keystream.append(ks_bit)
            logs.append(log)
        return keystream, logs
    def process_bits(self, bit_stream: list[int]) -> tuple[list[int], list[int], list[dict]]:
        """
        Mã hóa / Giải mã chuỗi bit bản rõ bằng phép toán XOR.
        XOR có tính chất đối xứng (P ^ S = C và C ^ S = P) nên hàm xử lý được cả 2 chiều.
        """
        if any(bit not in (0, 1) for bit in bit_stream):
            raise ValueError("Input must contain only bits")
        keystream, logs = self.generate_keystream(len(bit_stream))
        output_bits = [b ^ k for b, k in zip(bit_stream, keystream)]
        return output_bits, keystream, logs
class TinyA51(TinyA51Cipher):
    """Byte interface using the same 6/8/9-bit teaching cipher.
    Map an unsigned 32-bit key to a 23-bit state by XOR-folding its high
    nine bits into its low bits. This is a teaching convention, not a KDF.
    Register lists are stored with index 0 at the feedback input.
    """
    def __init__(self, key: int):
        if not isinstance(key, int) or not 0 <= key < (1 << 32):
            raise ValueError("TinyA51 key must be a 32-bit unsigned integer")
        state = (key & ((1 << 23) - 1)) ^ (key >> 23)
        bits = [(state >> i) & 1 for i in range(23)]
        super().__init__(bits[:6], bits[6:14], bits[14:])
    def keystream_bytes(self, length: int) -> bytes:
        if not isinstance(length, int) or length < 0:
            raise ValueError("Length must be a nonnegative integer")
        output = bytearray()
        for _ in range(length):
            value = 0
            for _ in range(8):
                bit, _ = self.step_verbose(0)
                value = (value << 1) | bit
            output.append(value)
        return bytes(output)
    def encrypt(self, data: bytes) -> bytes:
        return bytes(a ^ b for a, b in zip(data, self.keystream_bytes(len(data))))
    decrypt = encrypt
# --- KHỐI THỰC THI THỬ NGHIỆM ĐỘC LẬP ---
if __name__ == "__main__":
    # Trạng thái ban đầu mẫu để tái hiện bài tập trên lớp
    r1_init = [1, 0, 1, 1, 0, 0]
    r2_init = [0, 1, 0, 1, 0, 1, 1, 0]
    r3_init = [1, 1, 0, 0, 1, 0, 1, 0, 1]
    cipher = TinyA51Cipher(r1_init, r2_init, r3_init)
    plaintext_bits = [1, 0, 1, 1]
    print("=== DEMO THUẬT TOÁN TINYA5/1 ===")
    cipher_bits, keystream, logs = cipher.process_bits(plaintext_bits)
    for log in logs:
        print(f"\n[Bước {log['step']}]")
        print(f"  Clock bits (C1, C2, C3) : {log['clock_bits']}")
        print(f"  Majority bit            : {log['majority']}")
        print(f"  Thanh ghi được quay     : R1={log['clocked'][0]}, R2={log['clocked'][1]}, R3={log['clocked'][2]}")
        print(f"  Bit dòng khóa (S)       : {log['keystream_bit']}")
    print("\n------------------------------------")
    print(f"Bản rõ (Plaintext) : {plaintext_bits}")
    print(f"Dòng khóa (Keystream): {keystream}")
    print(f"Bản mã (Ciphertext)  : {cipher_bits}")
    # Kiểm thử giải mã khôi phục bản rõ
    decipher = TinyA51Cipher(r1_init, r2_init, r3_init)
    recovered_bits, _, _ = decipher.process_bits(cipher_bits)
    print(f"Giải mã khôi phục   : {recovered_bits}")
    assert recovered_bits == plaintext_bits, "Lỗi: Giải mã không khớp bản rõ!"
    print("-> KIỂM THỬ THÀNH CÔNG: Giải mã khôi phục đúng 100% bản rõ ban đầu.")
