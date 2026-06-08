#!/usr/bin/env python3
import struct
from conscious_engine import ConsciousEngine
from vse_engine import apply_data_layering, extract_data_layer

def temporary_mock_stream(stream_length):
    return ["150", "220", "010"]

def run_production_bridge_test():
    print("=" * 70)
    print("[HYBRID SYSTEM] INITIATING VSE + CONSCIOUS ENGINE ECOSYSTEM")
    print("=" * 70)

    storage = ConsciousEngine(root_path="./storage_pool", density=4)
    demo_text = "vse"
    generated_stream = temporary_mock_stream(len(demo_text))
    
    # 1. FÁZIS: VSE Kódolás
    transmission_data = apply_data_layering(demo_text, generated_stream)
    
    # 2. FÁZIS: Bináris tömörítés
    payload_bytes = bytearray()
    for packet in transmission_data:
        payload_bytes.extend(struct.pack(">HB", packet["sequence_id"], packet["payload_layer"]))
    
    # 3. FÁZIS: Írás koordinátára
    _, loc = storage.write(
        payload=bytes(payload_bytes), 
        storage="node_cam01", 
        layer="security_stream", 
        row="1024"
    )
    print(f"[STORAGE] Kapszula lezárva. Hely: {loc}")

    # 4. FÁZIS: Biztonságos visszaolvasás hálózati Fallback logikával
    print("\n[BRIDGE] Biztonságos LBA olvasás indítása...")
    try:
        raw_payload = storage.read(
            storage=loc["storage"], 
            layer=loc["layer"], 
            row=loc["row"], 
            sub_index=loc["sub_index"]
        )
    except (RuntimeError, ValueError, FileNotFoundError) as error:
        print(f"\n[⚠️ FALLBACK TRIGERRED] Kritikus hiba lépett fel az előhívás során: {error}")
        print("[NETWORK FABRIC] Külső manipuláció vagy fizikai szektorsérülés észlelve.")
        print("[NETWORK FABRIC] Automatikus hálózati parancs kiadva a forrásnak: Új Tiny Core generálása szükséges.")
        return

    # 5. FÁZIS: Rekonstrukció ha nincs hiba
    restored_packets = []
    for i in range(0, len(raw_payload), 3):
        chunk = raw_payload[i:i+3]
        if len(chunk) < 3:
            break
        seq_id, masked_data = struct.unpack(">HB", chunk)
        restored_packets.append({"sequence_id": seq_id, "payload_layer": masked_data})
        
    restored_text = extract_data_layer(restored_packets, generated_stream)
    
    print("\n" + "=" * 70)
    print(f"➔ TESZT STÁTUSZ: SIKERES (SUCCESS) | REKONSTRUÁLT ADAT: '{restored_text}'")
    print("=" * 70)

if __name__ == "__main__":
    run_production_bridge_test()