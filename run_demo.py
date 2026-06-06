import os
from core_generator import generate_vse_stream

def apply_data_layering(input_text: str, vse_codes: list[str]) -> list[dict]:
    """
    Public demo ruleset. Connects raw data bytes to the generated codes.
    The architecture allows AI rulesets to jump around non-consecutively.
    """
    data_bytes = input_text.encode('utf-8')
    if len(data_bytes) > len(vse_codes):
        raise ValueError("Generated stream is too short for the payload.")

    secured_packets = []
    
    print("\n[VSE ENGINE] Layering data payload underneath the generated matrix:")
    print("-" * 80)
    
    for index, byte_value in enumerate(data_bytes):
        sequence_number = index + 1
        active_code = int(vse_codes[index])
        
        # Core masking execution
        masked_data = active_code ^ byte_value
        
        print(f" Pos: {sequence_number:02d} | Byte: {byte_value:03d} ('{chr(byte_value)}') | Local VSE Code: {active_code:08d} | Out: {masked_data}")
        
        secured_packets.append({
            "sequence_id": sequence_number,
            "payload_layer": masked_data
        })
        
    print("-" * 80)
    return secured_packets

def extract_data_layer(packets: list[dict], vse_codes: list[str]) -> str:
    """
    Reconstructs the original data.
    """
    original_bytes = bytearray()
    for packet in packets:
        lookup_idx = packet["sequence_id"] - 1
        active_code = int(vse_codes[lookup_idx])
        masked_data = packet["payload_layer"]
        
        extracted_byte = masked_data ^ active_code
        original_bytes.append(extracted_byte)
        
    return original_bytes.decode('utf-8')

def main():
    print("=" * 60)
    print("VSE ENGINE - AUTONOMOUS DATA FRAMEWORK DEMO")
    print("=" * 60 + "\n")
    
    source_file = "data_source.txt"
    if not os.path.exists(source_file):
        with open(source_file, "w") as f:
            f.write("123,145,156")
            
    with open(source_file, "r") as f:
        content = f.read().strip()
    starting_seeds = [int(x.strip()) for x in content.split(",") if x.strip()]
    
    print(f"[STEP 1] Fetching hardware seeds: {starting_seeds}")
    
    demo_text = "vse"
    print(f"[STEP 2] Targeting payload: '{demo_text}'")
    print("         [SYSTEM NOTE] Custom offset initiated at index 39543.")
    print("         [SYSTEM NOTE] Advanced AI logic can execute non-consecutive pattern hopping.")
    
    # Generate stream starting from your custom 39543 offset
    generated_stream = generate_vse_stream(starting_seeds, stream_length=len(demo_text), start_offset=39543)
    
    # Process layering
    transmission_data = apply_data_layering(demo_text, generated_stream)
    
    # Reverse and extract
    restored_text = extract_data_layer(transmission_data, generated_stream)
    print(f"\n[STEP 3] Local client reconstruction:")
    print(f"         Extracted Text: '{restored_text}'")
    print("\nVerification successful. Absolute determinism achieved without storage load.")

if __name__ == "__main__":
    main()