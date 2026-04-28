import os
import sys
from gguf import GGUFReader, GGUFWriter

def slice_model(input_path, output_path, start_layer, end_layer):
    print(f"🔪 Slicing {input_path}...")
    print(f"🎯 Target Layers: {start_layer} to {end_layer}")
    
    if not os.path.exists(input_path):
        print(f"❌ Error: Input file {input_path} not found.")
        return

    reader = GGUFReader(input_path)
    writer = GGUFWriter(output_path, arch="llama")

    # 1. Copy essential metadata
    print("📝 Copying metadata...")
    for field in reader.fields.values():
        # Using the correct method for adding key-values from the reader
        writer.add_key_value(field.name, field.parts[-1], field.types[0])

    # 2. Filter and copy tensors
    print("🧠 Copying tensors for selected layers...")
    tensor_count = 0
    for tensor in reader.tensors:
        # GGUF layers are usually named 'blk.N.weight' or similar
        # We keep embeddings (token_embd), output weights, and our specific blocks
        keep = False
        if "blk." in tensor.name:
            parts = tensor.name.split(".")
            try:
                # tensor name usually looks like blk.0.attn_q.weight
                layer_idx = int(parts[1])
                if start_layer <= layer_idx <= end_layer:
                    keep = True
            except (ValueError, IndexError):
                pass
        else:
            # Keep non-block tensors (embeddings, final norms, etc.)
            keep = True
            
        if keep:
            writer.add_tensor(tensor.name, tensor.data)
            tensor_count += 1

    print(f"💾 Saving sliced model to {output_path} ({tensor_count} tensors)...")
    writer.write_config_file(output_path)
    print("✅ Slicing complete!")

if __name__ == "__main__":
    # For your leader node: Layers 0-10
    slice_model("Qwen_Qwen3.5-27B-Q4_K_M.gguf", "Qwen-Leader-Slice.gguf", 0, 10)
