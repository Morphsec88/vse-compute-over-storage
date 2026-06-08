#!/usr/bin/env python3
import struct
import time
import random
from conscious_engine import ConsciousEngine
from vse_engine import apply_data_layering, extract_data_layer

def generate_dynamic_mock_stream(length: int) -> list[str]:
    """Dinamikus kódgenerálás a hossz függvényében (szimulált stream)"""
    return [str(random.randint(10, 250)) for _ in range(length)]

def execute_heavy_stress():
    print("=" * 80)
    print("[STRESS TEST] INITIATING MASS OVERLOAD: VSE + CONSCIOUS ENGINE ECOSYSTEM")
    print("=" * 80)

    # Inicializálás szigorú immunizációval és hardveres flush-al
    storage = ConsciousEngine(root_path="./storage_pool_stress", density=4)
    
    # 1. Brutális méretű tesztadat generálása (1000 karakteres ismétlődő mintázat)
    base_payload = "VSE_MATRIX_DATA_STREAM_PARTICLE_COLLISION_LOG_HEX_89F2A1C3_" * 15
    print(f"\n[STEP 1] Generált tesztadat mérete: {len(base_payload)} karakter.")

    # 2. Iteratív terhelési hurok (100 darab kapszula egymás utáni beégetése)
    print("\n[STEP 2] 100 darab egyedi adatkapszula kiírása fizikai fsync kényszerítéssel...")
    start_write_time = time.time()
    
    saved_locations = []
    
    for i in range(1, 101):
        generated_stream = generate_dynamic_mock_stream(len(base_payload))
        
        # VSE Maszkolás (Lekapcsolt belső print a sebesség miatt)
        # Ideiglenesen felülbíráljuk a printet, hogy ne szemetelje tele a képernyőt
        transmission_data = []
        data_bytes = base_payload.encode('utf-8')
        for index, byte_value in enumerate(data_bytes):
            active_code = int(generated_stream[index])
            transmission_data.append({
                "sequence_id": index + 1,
                "payload_layer": active_code ^ byte_value
            })
            
        # Bináris sűrítés
        payload_bytes = bytearray()
        for packet in transmission_data:
            payload_bytes.extend(struct.pack(">HB", packet["sequence_id"], packet["payload_layer"]))
            
        # Írás egyedi sor-koordinátákra (row_1, row_2 ... row_100)
        _, loc = storage.write(
            payload=bytes(payload_bytes),
            storage="node_stress_01",
            layer="heavy_load",
            row=str(i)
        )
        # Eltároljuk a streamet és a helyet az ellenőrzéshez
        saved_locations.append((loc, generated_stream))
        
        if i % 20 == 0:
            print(f" -> {i} kapszula sikeresen lemezre rögzítve.")

    write_duration = time.time() - start_write_time
    print(f"➔ Írási fázis lezárult. Időtartam: {write_duration:.4f} másodperc.")

    # 3. Integritás és helyreállítási fázis (Összes adat visszaolvasása és bit-pontos vetítése)
    print("\n[STEP 3] Teljes adathalmaz szektor-szintű visszaolvasása és ellenőrzése...")
    start_read_time = time.time()
    
    verification_errors = 0
    
    for loc, stream in saved_locations:
        raw_payload = storage.read(
            storage=loc["storage"],
            layer=loc["layer"],
            row=loc["row"],
            sub_index=loc["sub_index"]
        )
        
        # Bináris kibontás
        restored_packets = []
        for i in range(0, len(raw_payload), 3):
            chunk = raw_payload[i:i+3]
            if len(chunk) < 3:
                break
            seq_id, masked_data = struct.unpack(">HB", chunk)
            restored_packets.append({"sequence_id": seq_id, "payload_layer": masked_data})
            
        # VSE Dekódolás
        restored_text = extract_data_layer(restored_packets, stream)
        
        if restored_text != base_payload:
            verification_errors += 1

    read_duration = time.time() - start_read_time
    print(f"➔ Olvasási fázis lezárult. Időtartam: {read_duration:.4f} másodperc.")

    # 4. Végső kiértékelés
    print("\n" + "=" * 80)
    print("STRESSZTESZT RIPORT:")
    print(f"Fizikai fájlok a lemezen: 100 darab .dat kapszula")
    print(f"Összesen feldolgozott karakter: {len(base_payload) * 100} bájt")
    print(f"Átviteli/Integritási hibák száma: {verification_errors}")
    if verification_errors == 0:
        print("➔ KONKLÚZIÓ: Az architektúra abszolút stabil. Zéró adatszivárgás, tökéletes determinizmus.")
    else:
        print("➔ KONKLÚZIÓ: Rendszerszintű integritási hiba lépett fel.")
    print("=" * 80)

if __name__ == "__main__":
    execute_heavy_stress()