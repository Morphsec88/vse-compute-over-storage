#!/usr/bin/env python3
import os

def apply_data_layering(input_text: str, vse_codes: list[str]) -> list[dict]:
    data_bytes = input_text.encode('utf-8')
    if len(data_bytes) > len(vse_codes):
        raise ValueError("Generated stream is too short for the payload.")

    secured_packets = []
    print("\n[VSE ENGINE] Layering data payload underneath the generated matrix:")
    print("-" * 80)
    for index, byte_value in enumerate(data_bytes):
        sequence_number = index + 1
        active_code = int(vse_codes[index])
        masked_data = active_code ^ byte_value
        print(f" Pos: {sequence_number:02d} | Byte: {byte_value:03d} ('{chr(byte_value)}') | Local VSE Code: {active_code:08d} | Out: {masked_data}")
        secured_packets.append({
            "sequence_id": sequence_number,
            "payload_layer": masked_data
        })
    print("-" * 80)
    return secured_packets

def extract_data_layer(packets: list[dict], vse_codes: list[str]) -> str:
    original_bytes = bytearray()
    for packet in packets:
        lookup_idx = packet["sequence_id"] - 1
        active_code = int(vse_codes[lookup_idx])
        masked_data = packet["payload_layer"]
        extracted_byte = masked_data ^ active_code
        original_bytes.append(extracted_byte)
    return original_bytes.decode('utf-8')