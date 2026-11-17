"""Vietnamese desktop interface. Launch from the project root: python run_gui.py."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from src.a51 import A51Cipher
from src.tiny_a51 import TinyA51Cipher
from ui.binary import process_binary, format_trace


def parse_unsigned(value: str, bits: int, label: str) -> int:
    try:
        text = value.strip()
        number = int(text, 16 if text.lower().startswith('0x') else 10)
    except ValueError as exc:
        raise ValueError(f'{label} phải là số thập phân hoặc hex bắt đầu bằng 0x.') from exc
    if not 0 <= number < (1 << bits):
        raise ValueError(f'{label} phải nằm trong khoảng 0 đến {hex((1 << bits) - 1)}.')
    return number


def make_cipher(algorithm: str, key: str, frame: str):
    if algorithm == 'TinyA5/1':
        bits = key.strip()
        if len(bits) != 23 or any(bit not in '01' for bit in bits):
            raise ValueError('Khóa TinyA5/1 phải có đúng 23 bit 0/1.')
        state = [int(bit) for bit in bits]
        cipher = TinyA51Cipher(state[:6], state[6:14], state[14:])
        def process(data):
            output = bytearray()
            for byte in data:
                mask = 0
                for _ in range(8):
                    bit, _ = cipher.step_verbose(0)
                    mask = (mask << 1) | bit
                output.append(byte ^ mask)
            return bytes(output)
        return process
    if algorithm != 'A5/1':
        raise ValueError('Thuật toán không hợp lệ.')
    number = parse_unsigned(key, 64, 'Khóa A5/1')
    # Display the key as eight big-endian bytes, load each byte LSB first.
    key_bits = [(byte >> bit) & 1 for byte in number.to_bytes(8, 'big') for bit in range(8)]
    cipher = A51Cipher(key_bits, parse_unsigned(frame, 22, 'Số khung'))
    return cipher.process_bytes


def process_text(algorithm: str, key: str, frame: str, text: str, decrypt: bool) -> str:
    operation = make_cipher(algorithm, key, frame)
    if decrypt:
        try:
            data = bytes.fromhex(text)
        except ValueError as exc:
            raise ValueError('Bản mã phải là chuỗi hex hợp lệ, ví dụ: 0a12ff.') from exc
        try:
            return operation(data).decode('utf-8')
        except UnicodeDecodeError as exc:
            raise ValueError('Không đọc được UTF-8. Kiểm tra khóa, thuật toán, số khung và bản mã; '
                             'với dữ liệu nhị phân hãy dùng mục File.') from exc
    return operation(text.encode('utf-8')).hex()


def process_file(algorithm: str, key: str, frame: str, source: str, target: str) -> int:
    operation = make_cipher(algorithm, key, frame)
    first, second = Path(source), Path(target)
    if first.resolve() == second.resolve() or (second.exists() and first.samefile(second)):
        raise ValueError('File đầu vào và đầu ra phải khác nhau.')
    # Exclusive creation avoids overwriting user data, including a race after the dialog.
    with first.open('rb') as input_file:
        with second.open('xb') as output_file:
            total = 0
            while chunk := input_file.read(65536):
                output_file.write(operation(chunk))
                total += len(chunk)
    return total


class CipherApp:
    def __init__(self, root):
        self.root = root
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None
        self.pending_kind = None
        self.buttons = []
        root.title('Nhóm 9 — TinyA5/1 và A5/1')
        root.geometry('1100x820')
        root.minsize(740, 600)
        root.protocol('WM_DELETE_WINDOW', self.close)
        self.algorithm = tk.StringVar(value='TinyA5/1')
        self.key = tk.StringVar(value='10010101001110100110000')
        self.frame = tk.StringVar(value='0x134')
        self.hint = tk.StringVar()
        self.status = tk.StringVar(value='Sẵn sàng.')
        self.binary_algorithm = self.algorithm
        self.binary_key = self.key
        self.binary_frame = self.frame
        self.binary_result = ''
        panel = ttk.Frame(root, padding=16)
        panel.pack(fill='both', expand=True)
        ttk.Label(panel, text='HỆ MÃ DÒNG — NHÓM 9',
                  font=('Segoe UI', 18, 'bold')).pack(anchor='w')
        row = ttk.Frame(panel)
        row.pack(fill='x', pady=10)
        self.selector = ttk.Combobox(row, textvariable=self.algorithm,
                                    values=('TinyA5/1', 'A5/1'), state='readonly', width=13)
        self.selector.pack(side='left')
        self.selector.bind('<<ComboboxSelected>>', self.example)
        ttk.Label(row, text=' Khóa: ').pack(side='left')
        ttk.Entry(row, textvariable=self.key, width=34).pack(side='left')
        ttk.Label(row, text=' Frame: ').pack(side='left')
        self.frame_entry = ttk.Entry(row, textvariable=self.frame, width=12)
        self.frame_entry.pack(side='left')
        self.binary_frame_entry = self.frame_entry
        self.button(row, 'Nạp ví dụ', self.example).pack(side='left', padx=8)
        ttk.Label(panel, textvariable=self.hint, wraplength=1050).pack(anchor='w')
        self.tabs = ttk.Notebook(panel)
        self.tabs.pack(fill='both', expand=True, pady=10)
        self.inputs, self.outputs = {}, {}
        for mode, title in [('bit', 'Nhị phân / Tính tay'), ('text', 'Văn bản / File')]:
            tab = ttk.Frame(self.tabs, padding=10)
            self.tabs.add(tab, text=title)
            ttk.Label(tab, text='Đầu vào: chuỗi 0/1 (tối đa 4096 bit)' if mode == 'bit'
                      else 'Đầu vào: văn bản UTF-8 / bản mã hex').pack(anchor='w')
            entry = ScrolledText(tab, height=4, wrap='word', font=('Consolas', 10))
            entry.pack(fill='both', expand=True, pady=5)
            self.inputs[mode] = entry
            actions = ttk.Frame(tab)
            actions.pack(fill='x')
            self.button(actions, 'Mã hóa', lambda m=mode: self.run(m, False)).pack(side='left', padx=(0, 8))
            self.button(actions, 'Giải mã', lambda m=mode: self.run(m, True)).pack(side='left', padx=(0, 8))
            self.button(actions, 'Đưa kết quả lên đầu vào', lambda m=mode: self.reuse(m)).pack(side='left')
            ttk.Label(tab, text='Kết quả').pack(anchor='w', pady=(8, 0))
            output = ScrolledText(tab, height=4, wrap='word', font=('Consolas', 10), state='disabled')
            output.pack(fill='both', expand=True, pady=5)
            self.outputs[mode] = output
            if mode == 'bit':
                ttk.Label(tab, text='Các bước: thanh ghi trước → sau; clock; majority; dòng khóa S').pack(anchor='w')
                self.binary_trace = ScrolledText(tab, height=7, wrap='none',
                                                font=('Consolas', 10), state='disabled')
                self.binary_trace.pack(fill='both', expand=True)
            else:
                row = ttk.Frame(tab)
                row.pack(fill='x', pady=8)
                self.button(row, 'Mã hóa file...', lambda: self.run_file(False)).pack(side='left', padx=(0, 8))
                self.button(row, 'Giải mã file...', lambda: self.run_file(True)).pack(side='left')
        self.input, self.output = self.inputs['text'], self.outputs['text']
        self.binary_input, self.binary_output = self.inputs['bit'], self.outputs['bit']
        ttk.Label(panel, textvariable=self.status, wraplength=1050).pack(anchor='w')
        self.example()
        self.tabs.select(1)

    @staticmethod
    def set_output(widget, value):
        widget.configure(state='normal')
        widget.delete('1.0', 'end')
        widget.insert('1.0', value)
        widget.configure(state='disabled')

    def example(self, event=None):
        if self.future is not None:
            return
        tiny = self.algorithm.get() == 'TinyA5/1'
        self.key.set('10010101001110100110000' if tiny else '0x1223456789ABCDEF')
        self.frame.set('0x134')
        self.update_algorithm()
        for mode, value in [('bit', '111' if tiny else '0' * 114), ('text', 'Xin chào Việt Nam!')]:
            self.inputs[mode].delete('1.0', 'end')
            self.inputs[mode].insert('1.0', value)
            self.set_output(self.outputs[mode], '')
        self.set_output(self.binary_trace, '')
        self.binary_result = ''
        self.status.set('Đã nạp ví dụ. Tiny: 111 → 011 → 111; A5/1: vector chuẩn với bản rõ toàn 0.')

    def load_binary_example(self):
        self.example()

    def update_binary_algorithm(self, event=None):
        self.update_algorithm(event)

    def run(self, mode, decrypt):
        if mode == 'bit':
            self.run_binary(decrypt)
        else:
            self.run_text(decrypt)

    def run_binary(self, decrypt):
        algorithm, key, frame = self.algorithm.get(), self.key.get(), self.frame.get()
        try:
            if algorithm == 'A5/1':
                key = format(parse_unsigned(key, 64, 'Khóa A5/1'), '064b')
                frame = format(parse_unsigned(frame, 22, 'Số khung'), '022b')
        except ValueError as exc:
            messagebox.showerror('Lỗi dữ liệu / khóa', str(exc), parent=self.root)
            return
        self.binary_direction = 'Bản rõ' if decrypt else 'Bản mã'
        self.submit('binary', process_binary, algorithm, key, frame,
                    self.binary_input.get('1.0', 'end-1c'))

    def reuse(self, mode):
        if mode == 'bit':
            self.reuse_binary()
        else:
            self.reuse_result()

    def reuse_binary(self):
        if self.binary_result:
            self.binary_input.delete('1.0', 'end')
            self.binary_input.insert('1.0', self.binary_result)

    def button(self, parent, label, command):
        button = ttk.Button(parent, text=label, command=command)
        self.buttons.append(button)
        return button

    def update_algorithm(self, event=None):
        full = self.algorithm.get() == 'A5/1'
        self.frame_entry.configure(state='normal' if full else 'disabled')
        self.hint.set('A5/1 19/22/23 bit: khóa 64 bit (thập phân hoặc 0x...), frame 22 bit; S lấy sau khi quay.'
                      if full else 'Tiny 6/8/9 bit: khóa 23 bit = R1 || R2 || R3; clock 1/3/3; S lấy sau khi quay.')

    def submit(self, kind, function, *args):
        if self.future is not None:
            return
        self.pending_kind = kind
        self.future = self.executor.submit(function, *args)
        for button in self.buttons:
            button.configure(state='disabled')
        self.status.set('Đang xử lý…')
        self.root.after(50, self.poll)

    def poll(self):
        if not self.future.done():
            self.root.after(50, self.poll)
            return
        try:
            result = self.future.result()
            if self.pending_kind == 'binary':
                output, stream, rows = result
                self.binary_result = output
                for widget, content in ((self.binary_output, f'{self.binary_direction}: {output}\nDòng khóa S: {stream}'),
                                        (self.binary_trace, format_trace(rows))):
                    widget.configure(state='normal')
                    widget.delete('1.0', 'end')
                    widget.insert('1.0', content)
                    widget.configure(state='disabled')
                self.status.set(f'Hoàn tất {len(output)} bit. Dùng cùng khóa để giải mã.')
            elif self.pending_kind == 'text':
                self.output.configure(state='normal')
                self.output.delete('1.0', 'end')
                self.output.insert('1.0', result)
                self.output.configure(state='disabled')
                self.status.set('Hoàn tất. Có thể đưa kết quả lên đầu vào để thử chiều ngược lại.')
            else:
                self.status.set(f'Đã lưu file: {result} byte. Dùng đúng khóa để khôi phục dữ liệu.')
        except Exception as exc:
            self.status.set('Xử lý thất bại. Kiểm tra dữ liệu và thiết lập khóa.')
            messagebox.showerror('Không thể xử lý', str(exc), parent=self.root)
        finally:
            self.future = None
            for button in self.buttons:
                button.configure(state='normal')

    def run_text(self, decrypt):
        self.submit('text', process_text, self.algorithm.get(), self.key.get(), self.frame.get(),
                    self.input.get('1.0', 'end-1c'), decrypt)

    def run_file(self, decrypt):
        if self.future is not None:
            return
        source = filedialog.askopenfilename(parent=self.root, title='Chọn file để giải mã' if decrypt else 'Chọn file để mã hóa')
        if not source:
            return
        name = Path(source).name
        if decrypt:
            name = name[:-4] if name.lower().endswith('.a51') else name + '.restored'
            name = 'khoi_phuc_' + name
        else:
            name += '.a51'
        target = filedialog.asksaveasfilename(parent=self.root, title='Chọn tên file đầu ra mới',
                                             initialfile=name, confirmoverwrite=False)
        if not target:
            return
        self.submit('file', process_file, self.algorithm.get(), self.key.get(), self.frame.get(), source, target)

    def reuse_result(self):
        self.input.delete('1.0', 'end')
        self.input.insert('1.0', self.output.get('1.0', 'end-1c'))

    def copy_result(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output.get('1.0', 'end-1c'))
        self.status.set('Đã sao chép kết quả.')

    def close(self):
        if self.future is not None:
            messagebox.showinfo('Đang xử lý', 'Vui lòng chờ xử lý xong trước khi đóng.', parent=self.root)
            return
        self.executor.shutdown(wait=False)
        self.root.destroy()


def main():
    root = tk.Tk()
    CipherApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
