import numpy as np
from PIL import Image
import os
import io

class LossyLogic:
    
    @staticmethod
    def make_nonuniform_table(bit_size, data, full_scale=256, epsilon=1.0):
        # Flatten and clip data
        x = np.array(data, dtype=float).flatten()
        x = np.clip(x, 0, full_scale - 1)

        L = 2 ** bit_size  # number of levels

        # 1) Start with one centroid = global average
        centroids = np.array([x.mean()], dtype=float)

        # 2) Splitting until we reach L centroids
        while len(centroids) < L:
            new_centroids = []
            for c in centroids:
                new_centroids.append(c - epsilon)
                new_centroids.append(c + epsilon)

            centroids = np.array(new_centroids, dtype=float)

            try:
                distances = np.abs(x[:, None] - centroids[None, :])
                labels = np.argmin(distances, axis=1)
            except MemoryError:
                print("Image too large for vectorized clustering.")
                return {} 

            for k in range(len(centroids)):
                cluster_points = x[labels == k]
                if len(cluster_points) > 0:
                    centroids[k] = cluster_points.mean()

        centroids = np.sort(centroids)
        L = len(centroids)

        boundaries = np.zeros(L + 1, dtype=float)
        boundaries[0] = 0.0
        boundaries[-1] = float(full_scale)

        for i in range(1, L):
            boundaries[i] = 0.5 * (centroids[i - 1] + centroids[i])
# i as index = q
# low and high are the boundaries for quantization level q
# centroid_val is the quantized value for that level q inverse 
        table = {}
        for i in range(L):
            low = int(np.floor(boundaries[i]))
            high = int(np.floor(boundaries[i + 1])) if i < L - 1 else int(full_scale)
            centroid_val = int(np.round(centroids[i]))
            table[(low, high)] = (i, centroid_val)

        return table

    @staticmethod
    def quantization_mse(original, reconstructed):
        """Compute Mean Squared Error."""
        original = np.array(original, dtype=float)
        reconstructed = np.array(reconstructed, dtype=float)
        return np.mean((original - reconstructed) ** 2)

    @staticmethod
    def run_quantization(original_image_pil, bit_size, file_path_on_disk):
        """
        Calculates CR based on ACTUAL FILE SIZES (Disk vs Buffer).
        """
        # 1. Prepare Data
        img_gray = original_image_pil.convert("L")
        img_np = np.array(img_gray)
        original_shape = img_np.shape
        flat_pixels = img_np.flatten()
        
        # --- ACTUAL ORIGINAL FILE SIZE (From Disk) ---
        if file_path_on_disk and os.path.exists(file_path_on_disk):
            original_size_bytes = os.path.getsize(file_path_on_disk)
        else:
            # Fallback if path is missing: Raw grayscale size
            original_size_bytes = flat_pixels.nbytes

        # 2. Generate Table
        table = LossyLogic.make_nonuniform_table(bit_size, flat_pixels, full_scale=256)
        
        # 3. Encode (Quantize)
        reconstructed_flat = np.zeros_like(flat_pixels)
        for (low, high), (index, centroid) in table.items():
            mask = (flat_pixels >= low) & (flat_pixels < high)
            reconstructed_flat[mask] = centroid
            
        # 4. Calculate MSE
        mse = LossyLogic.quantization_mse(flat_pixels, reconstructed_flat)
        
        # 5. Reconstruct Image Object
        img_reconstructed_np = reconstructed_flat.reshape(original_shape).astype(np.uint8)
        reconstructed_image_pil = Image.fromarray(img_reconstructed_np, mode="L")

        # the file would be if we saved it to disk right now (as PNG).
        buffer = io.BytesIO()
        reconstructed_image_pil.save(buffer, format="PNG", optimize=True)
        compressed_size_bytes = buffer.tell() # Get the size of the buffer
        
        # --- COMPRESSION RATIO ---
        if compressed_size_bytes > 0:
            cr = original_size_bytes / compressed_size_bytes
        else:
            cr = 0.0
        
        return reconstructed_image_pil, mse, cr