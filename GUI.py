import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os

# Import logic modules
from lossless_algorithms import LosslessLogic
from lossy_algorithms import LossyLogic


class DataCompressionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Compression Project")
        self.root.geometry("1000x800")
        
        # State variables
        self.file_path = None
        self.file_content = None
        self.decomp_file_content = None
        self.decompressed_text = None
        
        self.image_path = None
        self.original_image = None
        self.compressed_image = None
        
        # Checkbox variables (Compression)
        self.chk_rle_var = tk.BooleanVar()
        self.chk_huff_var = tk.BooleanVar()
        self.chk_golomb_var = tk.BooleanVar()
        self.chk_lzw_var = tk.BooleanVar()
        
        # Radio variable (Decompression)
        self.decomp_algo_var = tk.StringVar(value="")

        # Styles
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 24, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))
        
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)
        
        self.show_home()

    def clear_frame(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- SCREEN: HOME ---
    def show_home(self):
        self.clear_frame()
        
        # Center Content
        frame = tk.Frame(self.container)
        frame.place(relx=0.5, rely=0.45, anchor="center")
        
        lbl_title = ttk.Label(frame, text="Data Compression", style="Title.TLabel")
        lbl_title.pack(pady=40)
        
        # Buttons Container
        btn_frame = tk.Frame(frame)
        btn_frame.pack()
        
        btn_lossless = tk.Button(btn_frame, text="Lossless Compression", font=("Arial", 12), 
                                 width=25, height=2, bg="#e1f5fe",
                                 command=self.show_lossless)
        btn_lossless.grid(row=0, column=0, padx=10, pady=10)
        
        btn_decomp = tk.Button(btn_frame, text="Lossless Decompression", font=("Arial", 12),
                               width=25, height=2, bg="#e0f2f1",
                               command=self.show_decompression)
        btn_decomp.grid(row=0, column=1, padx=10, pady=10)
        
        btn_lossy = tk.Button(frame, text="Lossy Compression", font=("Arial", 12), 
                              width=25, height=2, bg="#ffebee",
                              command=self.show_lossy)
        btn_lossy.pack(pady=10)

        # --- NEW SECTION: CREDITS ---
        credits_frame = tk.Frame(self.container)
        credits_frame.place(relx=0.5, rely=0.9, anchor="center")
        
        tk.Label(credits_frame, text="Made By", font=("Arial", 12, "bold"), fg="#555").pack()
        tk.Label(credits_frame, text="Al-Husain Yaser", font=("Arial", 11), fg="#777").pack()
        tk.Label(credits_frame, text="Ahmed Mohamady", font=("Arial", 11), fg="#777").pack()
        tk.Label(credits_frame, text="Abdullah Atef", font=("Arial", 11), fg="#777").pack()

    # --- SCREEN: LOSSLESS COMPRESSION ---
    def show_lossless(self):
        self.clear_frame()
        self.file_path = None
        self.file_content = None
        
        top_frame = tk.Frame(self.container)
        top_frame.pack(side="top", fill="x", padx=10, pady=10)
        tk.Button(top_frame, text="< Back", command=self.show_home).pack(side="left")
        ttk.Label(top_frame, text="Lossless Compression", style="Header.TLabel").pack(side="left", padx=20)

        main_frame = tk.Frame(self.container)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left: Algorithms
        left_frame = ttk.LabelFrame(main_frame, text="1. Select Algorithms")
        left_frame.place(relx=0.0, rely=0.0, relwidth=0.4, relheight=0.3)
        
        tk.Checkbutton(left_frame, text="Run-Length Encoding (RLE)", variable=self.chk_rle_var, font=("Arial", 11), command=self.check_lossless_ready).pack(anchor="w", padx=10, pady=5)
        tk.Checkbutton(left_frame, text="Huffman Coding", variable=self.chk_huff_var, font=("Arial", 11), command=self.check_lossless_ready).pack(anchor="w", padx=10, pady=5)
        tk.Checkbutton(left_frame, text="Golomb Coding", variable=self.chk_golomb_var, font=("Arial", 11), command=self.check_lossless_ready).pack(anchor="w", padx=10, pady=5)
        tk.Checkbutton(left_frame, text="LZW Coding", variable=self.chk_lzw_var, font=("Arial", 11), command=self.check_lossless_ready).pack(anchor="w", padx=10, pady=5)

        # Right: Upload
        right_frame = ttk.LabelFrame(main_frame, text="2. Upload Text File")
        right_frame.place(relx=0.45, rely=0.0, relwidth=0.55, relheight=0.3)
        
        self.lbl_file_status = tk.Label(right_frame, text="No file selected", fg="gray")
        self.lbl_file_status.pack(pady=20)
        tk.Button(right_frame, text="Browse File", bg="#cfb940", fg="white", command=self.upload_text_file).pack(pady=5)

        # Bottom: Action & Results
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.place(relx=0.0, rely=0.35, relwidth=1.0, relheight=0.65)
        
        self.btn_compress_lossless = tk.Button(bottom_frame, text="COMPRESS", 
                                               font=("Arial", 12, "bold"), bg="#2196f3", fg="white",
                                               state=tk.DISABLED, command=self.perform_lossless_compression)
        self.btn_compress_lossless.pack(pady=10)
        
        # Results frame with scroll
        results_container = ttk.Frame(bottom_frame)
        results_container.pack(fill="both", expand=True, pady=10)
        
        self.results_area = tk.Frame(results_container)
        self.results_area.pack(fill="both", expand=True)

    def upload_text_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            self.file_path = path
            self.lbl_file_status.config(text=os.path.basename(path), fg="black")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.file_content = f.read()
                self.check_lossless_ready()
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def check_lossless_ready(self):
        any_algo = (self.chk_rle_var.get() or self.chk_huff_var.get() or 
                    self.chk_golomb_var.get() or self.chk_lzw_var.get())
        if any_algo and self.file_path:
            self.btn_compress_lossless.config(state=tk.NORMAL)
        else:
            self.btn_compress_lossless.config(state=tk.DISABLED)

    def perform_lossless_compression(self):
        # Use rstrip() to remove the invisible trailing newline
        data = self.file_content.rstrip()
        
        original_size_bytes = len(data.encode('utf-8'))
        
        if original_size_bytes == 0:
            return
        
        # Clear previous results
        for widget in self.results_area.winfo_children():
            widget.destroy()

        # Create the Notebook (Tabs)
        notebook = ttk.Notebook(self.results_area)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Helper Function to Create Tabs ---
        def create_tab(algo_name, encoded_package):
            theoretical_size = LosslessLogic.calculate_theoretical_size(encoded_package)
            
            if theoretical_size > 0:
                cr = original_size_bytes / theoretical_size
            else:
                cr = 0.0
            
            physical_size = len(encoded_package.encode('utf-8'))

            # Tab Frame
            tab_frame = tk.Frame(notebook, bg="#f5f5f5")
            notebook.add(tab_frame, text=algo_name)
            
            # Info Bar
            info_frame = tk.Frame(tab_frame, bg="#e0e0e0", pady=5, relief="groove", borderwidth=1)
            info_frame.pack(fill="x", side="top")
            
            tk.Label(info_frame, text=f"Original: {original_size_bytes} B", bg="#e0e0e0").pack(side="left", padx=5)
            tk.Label(info_frame, text=f"Theo. Size: {theoretical_size} B", bg="#e0e0e0", fg="#004d40", font=("Arial", 9, "bold")).pack(side="left", padx=5)
            tk.Label(info_frame, text=f"(File: {physical_size} B)", bg="#e0e0e0", fg="gray", font=("Arial", 8)).pack(side="left", padx=5)
            tk.Label(info_frame, text=f"CR: {cr:.2f}", font=("Arial", 10, "bold"), fg="#d32f2f", bg="#e0e0e0").pack(side="left", padx=10)

            # Text Display Area
            txt_scroll = scrolledtext.ScrolledText(tab_frame, wrap=tk.WORD, height=10, font=("Consolas", 10))
            txt_scroll.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Truncate Preview
            lines = encoded_package.splitlines()
            if len(lines) > 100:
                display_text = "\n".join(lines[:100]) + "\n\n... [Preview Truncated to 100 lines] ..."
            else:
                display_text = encoded_package

            txt_scroll.insert(tk.END, display_text)
            txt_scroll.config(state=tk.DISABLED) 
            
            # Download Button
            def download_output():
                f_path = filedialog.asksaveasfilename(
                    defaultextension=".txt", 
                    filetypes=[("Text File", "*.txt")],
                    initialfile=f"{algo_name}_compressed.txt"
                )
                if f_path:
                    try:
                        with open(f_path, 'w', encoding='utf-8') as f:
                            f.write(encoded_package)
                        messagebox.showinfo("Success", f"Saved {algo_name} output.")
                    except Exception as e:
                        messagebox.showerror("Error", str(e))

            btn_dl = tk.Button(tab_frame, text=f"Download {algo_name} Result", bg="#4caf50", fg="white", command=download_output)
            btn_dl.pack(pady=10)

        # 3. Run Algorithms
        if self.chk_rle_var.get():
            encoded = LosslessLogic.rle_compress(data)
            create_tab("RLE", encoded)

        if self.chk_huff_var.get():
            encoded = LosslessLogic.huffman_compress(data)
            create_tab("Huffman", encoded)

        if self.chk_golomb_var.get():
            encoded = LosslessLogic.golomb_compress(data)
            create_tab("Golomb", encoded)

        if self.chk_lzw_var.get():
            encoded = LosslessLogic.lzw_compress(data)
            create_tab("LZW", encoded)

    # --- SCREEN: LOSSLESS DECOMPRESSION ---
    def show_decompression(self):
        self.clear_frame()
        self.file_path = None
        self.decomp_file_content = None
        self.decompressed_text = None
        self.decomp_algo_var.set("")

        top_frame = tk.Frame(self.container)
        top_frame.pack(side="top", fill="x", padx=10, pady=10)
        tk.Button(top_frame, text="< Back", command=self.show_home).pack(side="left")
        ttk.Label(top_frame, text="Lossless Decompression", style="Header.TLabel").pack(side="left", padx=20)

        main_frame = tk.Frame(self.container)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Left: Algorithm Selection (Radio)
        left_frame = ttk.LabelFrame(main_frame, text="1. Select Algorithm")
        left_frame.place(relx=0.0, rely=0.0, relwidth=0.4, relheight=0.35)
        
        tk.Radiobutton(left_frame, text="Run-Length Encoding (RLE)", variable=self.decomp_algo_var, value="RLE", font=("Arial", 11), command=self.check_decomp_ready).pack(anchor="w", padx=10, pady=5)
        tk.Radiobutton(left_frame, text="Huffman Coding", variable=self.decomp_algo_var, value="Huffman", font=("Arial", 11), command=self.check_decomp_ready).pack(anchor="w", padx=10, pady=5)
        tk.Radiobutton(left_frame, text="Golomb Coding", variable=self.decomp_algo_var, value="Golomb", font=("Arial", 11), command=self.check_decomp_ready).pack(anchor="w", padx=10, pady=5)
        tk.Radiobutton(left_frame, text="LZW Coding", variable=self.decomp_algo_var, value="LZW", font=("Arial", 11), command=self.check_decomp_ready).pack(anchor="w", padx=10, pady=5)

        # Right: Upload
        right_frame = ttk.LabelFrame(main_frame, text="2. Upload Text File")
        right_frame.place(relx=0.45, rely=0.0, relwidth=0.55, relheight=0.35)
        
        self.lbl_decomp_file = tk.Label(right_frame, text="No file selected", fg="gray")
        self.lbl_decomp_file.pack(pady=20)
        tk.Button(right_frame, text="Browse File", bg="#cfb940", fg="white", command=self.upload_compressed_file).pack(pady=5)

        # Bottom: Action & Preview
        bottom_frame = tk.Frame(main_frame)
        bottom_frame.place(relx=0.0, rely=0.4, relwidth=1.0, relheight=0.6)

        self.btn_decompress = tk.Button(bottom_frame, text="DECOMPRESS", 
                                        font=("Arial", 12, "bold"), bg="#f44336", fg="white",
                                        state=tk.DISABLED, command=self.perform_decompression)
        self.btn_decompress.pack(pady=10)

        # Preview Area
        preview_frame = ttk.LabelFrame(bottom_frame, text="Preview - Decoded Output")
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.txt_preview = scrolledtext.ScrolledText(preview_frame, height=10, state=tk.DISABLED)
        self.txt_preview.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.btn_download_decomp = tk.Button(preview_frame, text="Download Decompressed Text", bg="#4caf50", fg="white",
                                             state=tk.DISABLED, command=self.save_decompressed_text)
        self.btn_download_decomp.pack(pady=5)

    def upload_compressed_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if path:
            self.file_path = path
            self.lbl_decomp_file.config(text=os.path.basename(path), fg="black")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.decomp_file_content = f.read()
                self.check_decomp_ready()
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")
                self.file_path = None

    def check_decomp_ready(self):
        if self.decomp_algo_var.get() and self.file_path:
            self.btn_decompress.config(state=tk.NORMAL)
        else:
            self.btn_decompress.config(state=tk.DISABLED)

    def perform_decompression(self):
        algo = self.decomp_algo_var.get()
        data = self.decomp_file_content
        text = ""
        
        try:
            if algo == "RLE":
                text = LosslessLogic.rle_decompress(data)
            elif algo == "Huffman":
                text = LosslessLogic.huffman_decompress(data, {})
            elif algo == "Golomb":
                text = LosslessLogic.golomb_decompress(data, 8, {})
            elif algo == "LZW":
                text = LosslessLogic.lzw_decompress(data)
            
            self.decompressed_text = text
            
            # Show Preview
            self.txt_preview.config(state=tk.NORMAL)
            self.txt_preview.delete(1.0, tk.END)
            self.txt_preview.insert(tk.END, text[:2000] + ("\n...[Truncated]" if len(text) > 2000 else ""))
            self.txt_preview.config(state=tk.DISABLED)
            
            self.btn_download_decomp.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Decompression Error", f"Failed to decompress: {e}")

    def save_decompressed_text(self):
        if self.decompressed_text:
            f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text File", "*.txt")])
            if f:
                with open(f, 'w', encoding='utf-8') as outfile:
                    outfile.write(self.decompressed_text)
                messagebox.showinfo("Success", f"Saved to {os.path.basename(f)}")

    # --- SCREEN: LOSSY COMPRESSION ---
    def show_lossy(self):
        self.clear_frame()
        self.image_path = None
        self.original_image = None
        self.compressed_image = None
        
        top_frame = tk.Frame(self.container)
        top_frame.pack(side="top", fill="x", padx=10, pady=10)
        tk.Button(top_frame, text="< Back", command=self.show_home).pack(side="left")
        ttk.Label(top_frame, text="Lossy Compression (Non-Uniform)", style="Header.TLabel").pack(side="left", padx=20)

        content_frame = tk.Frame(self.container)
        content_frame.pack(fill="both", expand=True, padx=20)

        # Upload and Options
        options_frame = tk.Frame(content_frame)
        options_frame.pack(pady=10, fill="x")
        
        # Upload
        tk.Button(options_frame, text="Upload Image", bg="#cfb940", fg="white", command=self.upload_image).pack(side="left", padx=10)
        self.lbl_img_name = tk.Label(options_frame, text="No image selected", fg="gray")
        self.lbl_img_name.pack(side="left", padx=10)

        # Dropdown for Compression Level
        tk.Label(options_frame, text="Compression Level:").pack(side="left", padx=(40, 5))
        
        self.combo_level = ttk.Combobox(options_frame, state="readonly", width=30)
        self.combo_level['values'] = [
            "Low Compression (3 bits)",
            "Medium Compression (2 bits)",
            "High Compression (1 bit)"
        ]
        self.combo_level.current(1) # Default to Low (3 bits)
        self.combo_level.pack(side="left", padx=5)

        self.btn_compress_lossy = tk.Button(options_frame, text="RUN COMPRESSION", 
                                             bg="#2196f3", fg="white", font=("Arial", 10, "bold"),
                                             state=tk.DISABLED, command=self.perform_lossy_compression)
        self.btn_compress_lossy.pack(side="left", padx=20)

        # Stats Display
        self.stats_frame = tk.Frame(content_frame, bg="#e3f2fd", relief="groove", borderwidth=1)
        self.stats_frame.pack(fill="x", pady=5)
        self.lbl_stats = tk.Label(self.stats_frame, text="MSE: N/A  |  CR: N/A", bg="#e3f2fd", font=("Arial", 11, "bold"))
        self.lbl_stats.pack(pady=5)

        # Visuals
        self.vis_frame = tk.Frame(content_frame)
        self.vis_frame.pack(fill="both", expand=True, pady=10)
        
        self.panel_orig = tk.Label(self.vis_frame, text="Original Image", bg="#eee")
        self.panel_orig.place(relx=0.0, rely=0.0, relwidth=0.48, relheight=0.9)
        
        self.panel_comp = tk.Label(self.vis_frame, text="Compressed (Quantized) Image", bg="#eee")
        self.panel_comp.place(relx=0.52, rely=0.0, relwidth=0.48, relheight=0.9)
        
        # Download
        self.btn_dl_lossy = tk.Button(content_frame, text="Download Result Image", bg="#4caf50", fg="white", 
                                      state=tk.DISABLED, command=self.save_lossy)
        self.btn_dl_lossy.pack(pady=10)

    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.webp")])
        if path:
            self.image_path = path
            self.lbl_img_name.config(text=os.path.basename(path), fg="black")
            
            img = Image.open(path)
            display_img = img.copy()
            display_img.thumbnail((400, 350))
            self.tk_orig = ImageTk.PhotoImage(display_img)
            self.panel_orig.config(image=self.tk_orig, text="")
            self.original_image = img 
            
            self.btn_compress_lossy.config(state=tk.NORMAL)
            self.panel_comp.config(image="", text="Compressed (Quantized) Image")
            self.btn_dl_lossy.config(state=tk.DISABLED)
            self.lbl_stats.config(text="MSE: N/A  |  CR: N/A")

    def perform_lossy_compression(self):
        if not self.original_image:
            return
        
        # Get bit size from dropdown
        selection = self.combo_level.get()
        bit_depth = 3 # Default
        if "4 bits" in selection: bit_depth = 4
        elif "3 bits" in selection: bit_depth = 3
        elif "2 bits" in selection: bit_depth = 2
        elif "1 bit" in selection: bit_depth = 1
        
        # Run Logic
        try:
            # We now pass 'self.image_path' to get actual file size from disk
            self.compressed_image, mse, cr = LossyLogic.run_quantization(
                self.original_image, 
                bit_depth, 
                self.image_path
            )
            
            # Update Stats
            self.lbl_stats.config(text=f"MSE: {mse:.4f}  |  CR: {cr:.2f}")
            
            # Display Result
            display_img = self.compressed_image.copy()
            display_img.thumbnail((400, 350))
            self.tk_comp = ImageTk.PhotoImage(display_img)
            self.panel_comp.config(image=self.tk_comp, text="")
            
            self.btn_dl_lossy.config(state=tk.NORMAL)
            
        except Exception as e:
            messagebox.showerror("Compression Error", str(e))

    def save_lossy(self):
        if self.compressed_image:
            f = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg")])
            if f:
                self.compressed_image.save(f)
                messagebox.showinfo("Success", f"Saved to {os.path.basename(f)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCompressionApp(root)
    root.mainloop()