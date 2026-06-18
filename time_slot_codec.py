#!/usr/bin/env python3
# Copyright (C) 2026 Morphsec88. All Rights Reserved.
# STRICTLY PROPRIETARY AND CONFIDENTIAL.
# VSE Engine Core Physical Evaluation Engine (Full Poem Expanded Mode)
# This software is protected under the terms of the GNU AGPLv3.
# SPDX-License-Identifier: AGPL-3.0-or-later

# VSE Engine internal transformation table
STATE_TRANSFORM_MAP = [40, 10, 70, 30, 80, 20, 60, 50]

def evaluate_and_encode_vse_engine(data_bytes: bytes) -> tuple:
    """
    Simulates the physical transmitter based on 0V/+1V logic.
    """
    vse_engine_pulses = 0
    telemetry_stream = []

    for byte in data_bytes:
        bits = f"{byte:08b}"
        
        vector_a = int(bits[0:3], 2)
        trigger_a = bits[3]
        
        trigger_b = bits[4]
        vector_c = int(bits[5:8], 2)
        
        # Rule execution: Active +1V pulse on '1', 0V passive on '0'
        sig_a_voltage = "+1V" if trigger_a == "1" else "0V"
        sig_b_voltage = "+1V" if trigger_b == "1" else "0V"
        
        if trigger_a == "1":
            vse_engine_pulses += 1
        if trigger_b == "1":
            vse_engine_pulses += 1
            
        t_idx_a = STATE_TRANSFORM_MAP[vector_a]
        t_idx_b = STATE_TRANSFORM_MAP[vector_c]
        
        telemetry_stream.append((sig_a_voltage, t_idx_a, sig_b_voltage, t_idx_b))

    return vse_engine_pulses, telemetry_stream

def decode_vse_engine(telemetry_stream: list) -> bytes:
    """
    Simulates the receiver and reconstructs the data.
    """
    decoded_buffer = bytearray()

    for sig_a, idx_a, sig_b, idx_b in telemetry_stream:
        vector_a = STATE_TRANSFORM_MAP.index(idx_a)
        vector_c = STATE_TRANSFORM_MAP.index(idx_b)
        
        trigger_a = "1" if sig_a == "+1V" else "0"
        trigger_b = "1" if sig_b == "+1V" else "0"
        
        bin_nibble_1 = f"{vector_a:03b}" + trigger_a
        bin_nibble_2 = trigger_b + f"{vector_c:03b}"
        
        decoded_buffer.append(int(bin_nibble_1 + bin_nibble_2, 2))

    return bytes(decoded_buffer)

def main():
    # Robert Frost: The Road Not Taken (Complete 4 Stanzas)
    full_poem = (
        "Two roads diverged in a yellow wood,\n"
        "And sorry I could not travel both\n"
        "And be one traveler, long I stood\n"
        "And looked down one as far as I could\n"
        "To where it bent in the undergrowth;\n\n"
        "Then took the other, as just as fair,\n"
        "And having perhaps the better claim,\n"
        "Because it was grassy and wanted wear;\n"
        "Though as for that the passing there\n"
        "Had worn them really about the same,\n\n"
        "And both that morning equally lay\n"
        "In leaves no step had trodden black.\n"
        "Oh, I kept the first for another day!\n"
        "Yet knowing how way leads on to way,\n"
        "I doubted if I should ever come back.\n\n"
        "I shall be telling this with a sigh\n"
        "Somewhere ages and ages hence:\n"
        "Two roads diverged in a wood, and I—\n"
        "I took the one less traveled by,\n"
        "And that has made all the difference."
    )

    # Multiplying the complete poem by exactly 5 times
    expanded_text = "\n\n=== REPEAT SEPARATOR ===\n\n".join([full_poem] * 5)
    raw_data = expanded_text.encode("utf-8")
    
    input_size = len(raw_data)
    traditional_signals = input_size * 10

    # Process communication chain
    vse_engine_pulses, telemetry = evaluate_and_encode_vse_engine(raw_data)
    decoded_bytes = decode_vse_engine(telemetry)
    
    # Text recovery
    recovered_text = decoded_bytes.decode("utf-8", errors="replace")
    
    if traditional_signals > 0:
        wire_savings_pct = ((traditional_signals - vse_engine_pulses) / traditional_signals) * 100
    else:
        wire_savings_pct = 0.0

    print("--------------------------------------------------")
    print(f"Processed Payload Size : {input_size} bytes")
    print(f"Standard Serial Budget : {traditional_signals} pulses")
    print(f"VSE Engine Emitted     : {vse_engine_pulses} (+1V triggers)")
    print("--------------------------------------------------")
    print(f"NET WIRE LOAD REDUCTION: {wire_savings_pct:.2f}%")
    print("--------------------------------------------------")
    print("RECOVERED TEXT OUTPUT FROM RECEIVER:")
    print("--------------------------------------------------")
    print(recovered_text)
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()
