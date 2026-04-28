import sys
import os
from gguf import GGUFReader, GGUFWriter

def slice_gguf(input_path, output_path, layer_start, layer_end):
    """
    Experimental GGUF Slicer.
    Extracts only the tensors required for layers [layer_start, layer_end].
    Note: Always includes embedding and output layers (0 and last) for the entry/exit nodes.
    """
    print(f"Slicing {input_path} -> {output_path} (Layers {layer_start}-{layer_end})")
    
    reader = GGUFReader(input_path)
    writer = GGUFWriter(output_path, "llama") # Assuming Llama/Qwen architecture

    # Copy metadata
    for key in reader.fields:
        writer.add_header(reader.fields[key])

    # Filter tensors
    count = 0
    for tensor in reader.tensors:
        name = tensor.name
        # Keep non-layer specific tensors (embeddings, norms, etc.)
        # and tensors within the requested layer range
        keep = False
        if "blk." in name:
            try:
                # tensor names usually look like 'blk.N.attn_q.weight'
                layer_num = int(name.split('.')[1])
                if layer_start <= layer_num <= layer_end:
                    keep = True
            except (ValueError, IndexError):
                keep = True # Keep if we can't parse (safety)
        else:
            keep = True # Keep embeddings, output, etc.

        if keep:
            writer.add_tensor(name, tensor.data)
            count += 1

    writer.write_config_file()
    print(f"Done! Kept {count} tensors.")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python slice_model.py <input_gguf> <output_gguf> <layer_start> <layer_end>")
    else:
        slice_gguf(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
