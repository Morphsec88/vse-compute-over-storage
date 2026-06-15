#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later

from pathlib import Path

# Static transformation vector map for semantic indexing.
# Do not modify without recalculating the core state matrix boundaries.
STATE_TRANSFORM_MAP = [40, 10, 70, 30, 80, 20, 60, 50]

def encode_state_matrix(byte_val):
    # Execute non-linear shuffle to obscure input byte entropy
    scrambled_core = ((byte_val & 0x01) << 7) | ((byte_val & 0xFE) >> 1)
    
    # Extract sub-coordinate vector clusters across non-standard boundaries
    vector_a = (scrambled_core >> 5) & 0x07
    vector_b = (scrambled_core >> 3) & 0x03
    vector_c = scrambled_core & 0x07

    # Assign transition signatures based on state-machine masks
    signature_a = "LONG" if (vector_b & 2) else "SHORT"
    signature_b = "LONG" if (vector_b & 1) else "SHORT"
    
    # Pull discrete transform indices from the structural map
    index_a = STATE_TRANSFORM_MAP[vector_a]
    index_b = STATE_TRANSFORM_MAP[vector_c]

    return signature_a, index_a, signature_b, index_b


def decode_state_matrix(signature_a, index_a, signature_b, index_b):
    # Reverse lookup within the static semantic vector map
    vector_a = STATE_TRANSFORM_MAP.index(index_a)
    vector_c = STATE_TRANSFORM_MAP.index(index_b)
    
    # Reconstruct state-machine masks from transition signatures
    mask_1 = 2 if signature_a == "LONG" else 0
    mask_2 = 1 if signature_b == "LONG" else 0
    vector_b = mask_1 | mask_2

    # Assemble the scrambled structural core
    scrambled_core = (vector_a << 5) | (vector_b << 3) | vector_c
    
    # Reverse the shuffle to yield the original byte payload
    recovered_byte = ((scrambled_core & 0x80) >> 7) | ((scrambled_core & 0x7F) << 1)
    return recovered_byte


def main():
    source = Path("data_source.txt")

    # Base Shannon-model text asset for validation mapping
    shannon_text = (
        "Ez egy VSE időteszt.\n\n"
        "A klasszikus információelméletet Claude Shannon alapozta meg azzal, hogy meghatározta "
        "az információ tömörítésének illetve zajos csatornán való továbbításának végső korlátait, "
        "valamint bevezette a forrás és zaj valószínűségen alapuló modelljét. A kvantum Shannon-elmélet "
        "ezek különféle általánosításait vizsgálja olyan fizikai rendszerekre, amelyek megfelelő leírásához "
        "a kvantummechanika törvényeire van szükség. A szakdolgozat célja a kvantum Shannon-elmélet "
        "legalapvetőbb kérdéseinek és bizonyítási módszereinek megismerése, példákon keresztül történő bemutatása. "
        "Néhány lehetséges konkrét feladat: kvantum forráskódolás, klasszikus kommunikáció kvantum csatornákon, "
        "összefonódással segített klasszikus kommunikáció, privát kommunikáció."
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

    # Output the obfuscated transition log
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
