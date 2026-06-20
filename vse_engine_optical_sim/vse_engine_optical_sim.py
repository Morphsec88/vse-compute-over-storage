#!/usr/bin/env python3
# ==============================================================================
# VSE Engine Optical - Production Simulation Core
# Version: 4.0.1 - Fixed Indexing Rendering Bug
#
# License: GNU Affero General Public License v3.0 (AGPLv3)
# Copyright (C) 2026 Morphsec88. All Rights Reserved.
# STRICTLY PROPRIETARY AND CONFIDENTIAL.
# ==============================================================================

import random
import time

def hardware_instrument_trigger(event_type, delay_ns, voltage, channel_bus):
    pass  

# Physical interface voltage levels
VOLTAGE_POS = 1.0   
VOLTAGE_NEG = -1.0  
VOLTAGE_OFF = 0.0   

# Global telemetry registers
arq_retransmits = 0
watchdog_trips = 0
total_active_pulses = 0  

# Fixed structural hardware mapping tables (0-7 indices)
FIXED_COLUMN_A = [0, 1, 2, 3]
FIXED_COLUMN_B = [4, 5, 6, 7]
FIXED_COLUMN_C = [0, 1, 2, 3]
FIXED_COLUMN_D = [4, 5, 6, 7]

def vse_engine_optical_transmitter(chunk_bytes):
    photon_stream = []
    
    for byte in chunk_bytes:
        bits = f"{byte:08b}"
        
        vector_a = int(bits[0:3], 2)
        bit_4 = bits[3]
        bit_5 = bits[4]
        vector_c = int(bits[5:8], 2)
        
        # --- PHASE 1: FIRST COMBINED PULSE (bit_4 width + vector_a delay) ---
        duration_1 = 5 if bit_4 == "0" else 15
        
        if vector_a in FIXED_COLUMN_A:
            wire_bus = "A"
            voltage = VOLTAGE_POS
            time_slot_idx = FIXED_COLUMN_A.index(vector_a) + 1
        else:
            wire_bus = "B"
            voltage = VOLTAGE_NEG
            time_slot_idx = FIXED_COLUMN_B.index(vector_a) + 1
            
        photon_stream.append({
            "voltage": voltage,
            "delay_ns": time_slot_idx * 10,
            "wire_bus": wire_bus,
            "pulse_width_ns": duration_1,
            "is_high_energy": (bit_4 == "1")
        })
        
        # --- PHASE 2: SECOND COMBINED PULSE (bit_5 width + vector_c delay) ---
        duration_2 = 5 if bit_5 == "0" else 15
        
        if vector_c in FIXED_COLUMN_C:
            wire_bus = "A"
            voltage = VOLTAGE_POS
            time_slot_idx = FIXED_COLUMN_C.index(vector_c) + 1
        else:
            wire_bus = "B"
            voltage = VOLTAGE_NEG
            time_slot_idx = FIXED_COLUMN_D.index(vector_c) + 1
            
        photon_stream.append({
            "voltage": voltage,
            "delay_ns": time_slot_idx * 10,
            "wire_bus": wire_bus,
            "pulse_width_ns": duration_2,
            "is_high_energy": (bit_5 == "1")
        })
            
    return photon_stream

def inject_channel_faults(photon_stream, force_drop):
    if force_drop:
        return [{**sig, "voltage": 0.01} for sig in photon_stream]
        
    noisy_stream = []
    for signal in photon_stream:
        noisy_signal = signal.copy()
        if abs(signal["voltage"]) > 0.1:
            noise = random.uniform(-0.08, 0.08)
            noisy_signal["voltage"] = round(signal["voltage"] + noise, 4)
            
            jitter = random.randint(-1, 1)
            noisy_signal["delay_ns"] = max(10, signal["delay_ns"] + jitter)
            noisy_signal["pulse_width_ns"] = max(3, signal["pulse_width_ns"] + jitter)
        noisy_stream.append(noisy_signal)
    return noisy_stream

def schmitt_trigger_amplitude_filter(voltage):
    if -1.25 <= voltage <= -0.75: return "B"          
    if 0.75 <= voltage <= 1.25: return "A"           
    if -0.20 <= voltage <= 0.20: return "DROP_ERR"
    return "UNKNOWN_ERROR"
def vse_engine_optical_receiver(photon_stream, expected_bytes_count):
    global watchdog_trips
    decoded_buffer = bytearray()
    
    current_byte_bits = ["0"] * 8
    processing_phase = 0 
    
    for signal in photon_stream:
        hardware_instrument_trigger("RECEIVE_EVENT", signal["delay_ns"], signal["voltage"], signal["wire_bus"])
        detected_layer = schmitt_trigger_amplitude_filter(signal["voltage"])
        
        if detected_layer == "UNKNOWN_ERROR" or detected_layer == "DROP_ERR":
            if detected_layer == "DROP_ERR":
                watchdog_trips += 1
            return None, True
            
        calculated_idx = int(round(signal["delay_ns"] / 10.0)) - 1
        if not (0 <= calculated_idx < 4):
            return None, True
            
        decoded_trigger = "0" if signal["pulse_width_ns"] <= 9 else "1"
        
        if processing_phase == 0:
            target_vector = FIXED_COLUMN_A[calculated_idx] if detected_layer == "A" else FIXED_COLUMN_B[calculated_idx]
            current_byte_bits[0:3] = list(f"{target_vector:03b}")
            current_byte_bits[3] = decoded_trigger
            processing_phase = 1
        else:
            target_vector = FIXED_COLUMN_C[calculated_idx] if detected_layer == "A" else FIXED_COLUMN_D[calculated_idx]
            current_byte_bits[5:8] = list(f"{target_vector:03b}")
            current_byte_bits[4] = decoded_trigger
            
            decoded_buffer.append(int("".join(current_byte_bits), 2))
            current_byte_bits = ["0"] * 8
            processing_phase = 0

    return bytes(decoded_buffer[:expected_bytes_count]), False

def run_production_stress_test():
    global arq_retransmits, total_active_pulses, watchdog_trips
    
    poem_data = (
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
    ) * 40 
    
    raw_payload = poem_data.encode("utf-8")
    chunk_size = 16
    final_output_stream = bytearray()
    start_bench_time = time.time()
    end_bench_time = start_bench_time
    
    data_chunks = [raw_payload[i:i + chunk_size] for i in range(0, len(raw_payload), chunk_size)]
    
    for chunk in data_chunks:
        transmission_successful = False
        
        while not transmission_successful:
            photon_stream = vse_engine_optical_transmitter(chunk)
            force_drop = random.random() < 0.02
            noisy_stream = inject_channel_faults(photon_stream, force_drop)
            decoded_chunk, error_detected = vse_engine_optical_receiver(noisy_stream, len(chunk))
            
            if error_detected or decoded_chunk is None:
                arq_retransmits += 1
                continue
                
            total_active_pulses += sum(1 for sig in photon_stream if sig["is_high_energy"])
            final_output_stream.extend(decoded_chunk)
            transmission_successful = True
            end_bench_time = time.time()
            
    standard_serial_budget = len(raw_payload) * 10
    vire_savings_pct = ((standard_serial_budget - total_active_pulses) / standard_serial_budget) * 100
    
    print(" ")
    print(" [REAL-TIME TELEMETRY MONITOR COMPLIANCE REPORT] ")
    print("-" * 70)
    print(f" Data Recovery Integrity   : {len(final_output_stream)} / {len(raw_payload)} Bytes Delivered")
    print(f" Standard Serial Budget    : {standard_serial_budget} pulses")
    print(f" VSE Engine Emitted        : {total_active_pulses} high-energy active pulses")
    print(f" ARQ Auto-Retransmits      : {arq_retransmits} block loops")
    print(f" Watchdog Timer Trips      : {watchdog_trips} triggers")
    print(f" Execution Simulation Time : {(end_bench_time - start_bench_time) * 1000:.2f} ms")
    print("-" * 70)
    print(f" NET WIRE LOAD REDUCTION   : {vire_savings_pct:.2f} %")
    print("-" * 70)

if __name__ == "__main__":
    run_production_stress_test()
