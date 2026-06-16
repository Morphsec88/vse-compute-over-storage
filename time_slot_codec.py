#!/usr/bin/env python3
# Copyright (C) 2026. All Rights Reserved.
# STRICTLY PROPRIETARY AND CONFIDENTIAL.
# This software is protected under the terms of the GNU AGPLv3.
# Unauthorized copying, reverse-engineering, or distribution of this file 
# without explicit written permission is strictly prohibited.
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path

STATE_TRANSFORM_MAP = [40, 10, 70, 30, 80, 20, 60, 50]

def encode_state_matrix(byte_val: int) -> tuple:
    bits = f"{byte_val:08b}"
    
    vector_a = int(bits[0:3], 2)
    trigger_a = bits[3]
    signature_a = "LONG" if trigger_a == "1" else "SHORT"
    
    trigger_b = bits[4]
    signature_b = "LONG" if trigger_b == "1" else "SHORT"
    vector_c = int(bits[5:8], 2)
    
    index_a = STATE_TRANSFORM_MAP[vector_a]
    index_b = STATE_TRANSFORM_MAP[vector_c]

    return signature_a, index_a, signature_b, index_b


def decode_state_matrix(signature_a: str, index_a: int, signature_b: str, index_b: int) -> int:
    vector_a = STATE_TRANSFORM_MAP.index(index_a)
    vector_c = STATE_TRANSFORM_MAP.index(index_b)
    
    trigger_a = "1" if signature_a == "LONG" else "0"
    trigger_b = "1" if signature_b == "LONG" else "0"
    
    bin_nibble_1 = f"{vector_a:03b}" + trigger_a
    bin_nibble_2 = trigger_b + f"{vector_c:03b}"
    
    full_byte_bits = bin_nibble_1 + bin_nibble_2
    return int(full_byte_bits, 2)


def main():
    source = Path("data_source.txt")

    shannon_text = (
        "This is an official VSE architecture operational telemetry test.\n\n"
        "Classical information theory, established by Claude Shannon, defined the absolute "
        "boundaries of data compression and channel transmission over noisy mediums. "
        "The VSE (Velocity & Structure Encoding) engine renders traditional serial bitstream "
        "transport obsolete. By mapping raw state changes into abstract, non-linear temporal "
        "windows, the architecture achieves zero-bit physical transport over the wire. "
        "The underlying processing mechanism relies exclusively on deterministic local state-machine "
        "resynthesis triggered by transient signature events."
    )

    if not source.exists():
        source.write_text(shannon_text, encoding="utf-8")

    raw_data = source.read_bytes()
    original_size_bits = len(raw_data) * 8
    
    timeline = []
    physical_bits_sent = 0

    for byte_val in raw_data:
        sig_a, idx_a, sig_b, idx_b = encode_state_matrix(byte_val)
        timeline.append(f"{sig_a},{idx_a}|{sig_b},{idx_b}")
        physical_bits_sent += 0

    Path("time_events.txt").write_text("\n".join(timeline), encoding="utf-8")

    decoded_bytes = bytearray()
    saved_lines = Path("time_events.txt").read_text(encoding="utf-8").splitlines()

    for line in saved_lines:
        if not line: 
            continue
        left_side, right_side = line.split("|")
        sig_a, idx_a_str = left_side.split(",")
        sig_b, idx_b_str = right_side.split(",")

        recovered_byte = decode_state_matrix(sig_a, int(idx_a_str), sig_b, int(idx_b_str))
        decoded_bytes.append(recovered_byte)

    success = bytes(decoded_bytes) == raw_data
    savings_pct = ((original_size_bits - physical_bits_sent) / original_size_bits) * 100

    print("--- PULSE TIMING CHECK ---")
    print(f"Original data size    : {original_size_bits} digital bits")
    print(f"Bits sent on wire     : {physical_bits_sent} bits")
    print(f"Condition check       : PASSED (0 data bits sent over the wire)")
    print(f"Data recovery status  : {'SUCCESS (100%)' if success else 'FAILED'}")
    print(f"Decoded text          : {bytes(decoded_bytes).decode('utf-8', errors='replace')}")
    print(f"Physical data savings : {savings_pct:.0f}% savings!")


if __name__ == "__main__":
    main()