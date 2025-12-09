"""Simple Lossless Compression Algorithms with Embedded Metadata"""
import math
from collections import Counter
import heapq
import ast
import re

class LosslessLogic:
    
    SEPARATOR = "::::" 
    SUB_SEPARATOR = "$$$"

    # ===================== RLE (Run-Length Encoding) =====================
    @staticmethod
    def rle_compress(text):
        if not text: return ""
        
        result = []
        counts = [] 
        
        count = 1
        for i in range(1, len(text)):
            if text[i] == text[i-1]:
                count += 1
            else:
                result.append(f"{text[i-1]}{count}|")
                counts.append(count)
                count = 1
        result.append(f"{text[-1]}{count}|")
        counts.append(count)
        
        encoded_body = "".join(result)
        
        max_count = max(counts) if counts else 0
        count_bits = max_count.bit_length() 
        if count_bits == 0: count_bits = 1 

        return f"RLE{LosslessLogic.SEPARATOR}{count_bits}{LosslessLogic.SEPARATOR}{encoded_body}"
    
    @staticmethod
    def rle_decompress(compressed_package):
        try:
            algo, meta, data = compressed_package.split(LosslessLogic.SEPARATOR, 2)
            if algo != "RLE": raise ValueError("Not RLE")
        except ValueError: data = compressed_package

        result = []
        pairs = data.split('|')
        for pair in pairs:
            if not pair: continue 
            char = pair[0]
            count_str = pair[1:]
            if count_str.isdigit():
                result.append(char * int(count_str))
        return "".join(result)
    
    # ===================== Huffman Coding (Unchanged) =====================
    @staticmethod
    def huffman_compress(text):
        if not text: return None, ""
        freq = Counter(text)
        heap = [[weight, [char, ""]] for char, weight in freq.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            smallest = heapq.heappop(heap)
            secsmallest = heapq.heappop(heap)
            for pair in smallest[1:]: pair[1] = "0" + pair[1]
            for pair in secsmallest[1:]: pair[1] = "1" + pair[1]
            heapq.heappush(heap, [smallest[0] + secsmallest[0]] + smallest[1:] + secsmallest[1:])
        codes = dict(heap[0][1:]) if heap[0][1:] else {text[0]: "0"}
        encoded_body = "".join(codes[ch] for ch in text)
        return f"Huffman{LosslessLogic.SEPARATOR}{codes}{LosslessLogic.SEPARATOR}{encoded_body}"
    
    @staticmethod
    def huffman_decompress(compressed_package, _ignored=None):
        try:
            algo, meta, encoded_body = compressed_package.split(LosslessLogic.SEPARATOR, 2)
            codes = ast.literal_eval(meta)
        except Exception: return "Error parsing Huffman"
        if not codes or not encoded_body: return ""
        reverse_codes = {v: k for k, v in codes.items()}
        result = []
        current = ""
        for bit in encoded_body:
            current += bit
            if current in reverse_codes:
                result.append(reverse_codes[current])
                current = ""
        return "".join(result)
    
    # ===================== Golomb Coding (Updated Mapping) =====================
    @staticmethod
    def golomb_compress(text):
        """
        Compress using Golomb.
        Mapping Logic:
        - If char is digit '0'-'9': Use int(char) [Values 0-9]
        - Else: Use ord(char) + 10 [Values >= 10]
        """
        if not text: return {}, 0, ""
        
        # --- Helper: Value Mapping ---
        def get_mapped_value(char):
            if char.isdigit():
                return int(char)
            else:
                return ord(char) + 10

        # --- Helper: Encoding Logic ---
        def get_golomb_code(n, m):
            q = n // m
            r = n % m
            
            # Unary Quotient
            quotient_code = "1" * q + "0"
            
            # Binary Remainder
            if (m & (m - 1)) == 0:
                k = int(math.log2(m))
                remainder_code = format(r, f'0{k}b')
            else:
                b = math.ceil(math.log2(m))
                T = 2**b - m
                if r < T:
                    remainder_code = format(r, f'0{b-1}b')
                else:
                    remainder_code = format(r + T, f'0{b}b')
            
            return quotient_code + remainder_code

        # --- Grid Search for Optimal M ---
        freq = Counter(text)
        best_m = 1
        min_total_bits = float('inf')
        
        for candidate_m in range(1, 257):
            current_total_bits = 0
            for char, count in freq.items():
                x = get_mapped_value(char) # Use new mapping
                code_len = len(get_golomb_code(x, candidate_m))
                current_total_bits += count * code_len
            
            if current_total_bits < min_total_bits:
                min_total_bits = current_total_bits
                best_m = candidate_m
        
        # --- Final Compression ---
        m = best_m
        encoded_list = []
        for char in text:
            val = get_mapped_value(char) # Use new mapping
            encoded_list.append(get_golomb_code(val, m))
            
        encoded_body = "".join(encoded_list)
        
        return f"Golomb{LosslessLogic.SEPARATOR}{m}{LosslessLogic.SEPARATOR}{encoded_body}"
    
    @staticmethod
    def golomb_decompress(compressed_package, _ignored_m=None, _ignored_map=None):
        try:
            algo, meta, encoded_body = compressed_package.split(LosslessLogic.SEPARATOR, 2)
            if algo != "Golomb": return "Error"
            m = int(meta)
        except Exception: return "Error"

        if not encoded_body or m == 0: return ""
        
        result = []
        i = 0
        n_len = len(encoded_body)
        
        is_power_of_2 = (m & (m - 1)) == 0
        if is_power_of_2:
            k = int(math.log2(m))
        else:
            b = math.ceil(math.log2(m))
            T = 2**b - m

        while i < n_len:
            # 1. Quotient
            q = 0
            while i < n_len and encoded_body[i] == "1":
                q += 1
                i += 1
            if i < n_len and encoded_body[i] == "0":
                i += 1
            
            # 2. Remainder
            r = 0
            if is_power_of_2:
                if i + k <= n_len:
                    r = int(encoded_body[i:i+k], 2)
                    i += k
            else:
                len_short = b - 1
                if i + len_short <= n_len:
                    temp_val = int(encoded_body[i:i+len_short], 2)
                    i += len_short
                    if temp_val < T:
                        r = temp_val
                    else:
                        if i < n_len:
                            next_bit = int(encoded_body[i])
                            i += 1
                            val = (temp_val << 1) + next_bit
                            r = val - T
            
            # 3. Reconstruct (Reverse Mapping)
            num = q * m + r
            
            # Logic: If < 10, it's a digit. If >= 10, it's a shifted ASCII char.
            if num < 10:
                result.append(str(num))
            else:
                try:
                    result.append(chr(num - 10))
                except:
                    result.append("?")
            
        return "".join(result)
    
    # ===================== LZW Coding =====================
    @staticmethod
    def lzw_compress(text):
        if not text: return ""
        dictionary = {chr(i): i for i in range(256)}
        next_code = 256; current = ""; result = []
        for next_char in text:
            combined = current + next_char
            if combined in dictionary: current = combined
            else:
                result.append(str(dictionary[current]))
                dictionary[combined] = next_code
                next_code += 1
                current = next_char
        if current: result.append(str(dictionary[current]))
        max_code = next_code
        bit_width = max_code.bit_length()
        if bit_width < 8: bit_width = 8
        encoded_body = "|".join(result)
        return f"LZW{LosslessLogic.SEPARATOR}{bit_width}{LosslessLogic.SEPARATOR}{encoded_body}"
    
    @staticmethod
    def lzw_decompress(compressed_package):
        try: algo, meta, encoded_body = compressed_package.split(LosslessLogic.SEPARATOR, 2)
        except ValueError: encoded_body = compressed_package
        if not encoded_body: return ""
        codes_list = [int(x) for x in encoded_body.split("|")] if "|" in encoded_body else []
        if not codes_list: return ""
        dictionary = {i: chr(i) for i in range(256)}
        next_code = 256; result = []; current = dictionary[codes_list[0]]
        result.append(current)
        for code in codes_list[1:]:
            if code in dictionary: entry = dictionary[code]
            elif code == next_code: entry = current + current[0]
            else: entry = ""
            result.append(entry)
            dictionary[next_code] = current + entry[0]
            next_code += 1
            current = entry
        return "".join(result)

    # ===================== Sizing & Ratio =====================
    @staticmethod
    def calculate_theoretical_size(compressed_package):
        if not compressed_package: return 0.0
        try:
            if LosslessLogic.SEPARATOR in compressed_package:
                parts = compressed_package.split(LosslessLogic.SEPARATOR)
                algo = parts[0]
                meta = parts[1]
                encoded_body = parts[2]
                header_overhead = len((algo + LosslessLogic.SEPARATOR + meta + LosslessLogic.SEPARATOR).encode('utf-8'))
            else:
                return 0.0

            body_bits = 0
            if algo == "RLE":
                count_bits = int(meta)
                pairs = [p for p in encoded_body.split('|') if p]
                num_pairs = len(pairs)
                bits_per_pair = 8 + count_bits
                body_bits = num_pairs * bits_per_pair
            elif algo == "LZW":
                bit_width = int(meta)
                codes = [c for c in encoded_body.split('|') if c]
                body_bits = len(codes) * bit_width
            else:
                body_bits = len(encoded_body)

            body_bytes = math.ceil(body_bits / 8)
            return header_overhead + body_bytes
        except Exception:
            return 0.0

    @staticmethod
    def get_compression_ratio(original_size_bytes, compressed_package):
        theoretical_size = LosslessLogic.calculate_theoretical_size(compressed_package)
        if theoretical_size == 0: return 0.0
        return original_size_bytes / theoretical_size