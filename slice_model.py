import os
import sys
import numpy as np
from gguf import GGUFReader, GGUFWriter

def physical_slice(input_path, output_path, start_layer, end_layer):
    """
    Creates a new GGUF file containing only the metadata and the 
    tensors required for the specified layer range.
    """
    print(f"🔪 [Physical Slicer] Processing: {input_path}")
    print(f"🎯 Target Range: Layers {start_layer} to {end_layer}")

    if not os.path.exists(input_path):
        print(f"❌ Error: Input file {input_path} not found.")
        return

    reader = GGUFReader(input_path)
    
    # We use the same architecture from the reader
    arch = "unknown"
    for field in reader.fields.values():
        if field.name == "general.architecture":
            arch = str(field.parts[-1].tobytes().decode('utf-8')).strip('\x00')
            break

    writer = GGUFWriter(output_path, arch=arch)

    # 1. Copy ALL Metadata
    # This ensures the LLM engine knows the total layer count, head count, etc.
    print("📝 Syncing Metadata...")
    for field in reader.fields.values():
        writer.add_key_value(field.name, field.parts[-1], field.types[0])

    # 2. Filter Tensors
    print("🧠 Extracting Tensors...")
    count = 0
    for tensor in reader.tensors:
        keep = False
        
        # Keep non-block tensors (embeddings, final norms, etc.)
        if "blk." not in tensor.name:
            keep = True
        else:
            # Extract layer index from 'blk.N.weight'
            try:
                parts = tensor.name.split(".")
                layer_idx = int(parts[1])
                if start_layer <= layer_idx <= end_layer:
                    keep = True
            except (ValueError, IndexError):
                pass
        
        if keep:
            # We add the tensor with its ORIGINAL data, shape, and type
            # This bypasses the gguf library's type-checking for quantized formats
            writer.add_tensor(tensor.name, tensor.data, raw_shape=tensor.shape, raw_dtype=tensor.tensor_type)
            count += 1

    print(f"💾 Writing {output_path}...")
    writer.write_config_file(output_path)
    print(f"✅ Success! Created slice with {count} tensors.")
    print(f"📏 New File Size: ~{os.path.getsize(output_path) / 1024 / 1024 / 1024:.2f} GB")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python slice_model.py <input.gguf> <output.gguf> <start> <end>")
    else:
        physical_slice(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
