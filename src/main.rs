use rand::Rng;
use std::sync::Mutex;
use std::time::Instant;

// Physical interface voltage levels
pub const VOLTAGE_POS: f64 = 1.0;
pub const VOLTAGE_NEG: f64 = -1.0;
pub const VOLTAGE_OFF: f64 = 0.0;

struct Telemetry {
    arq_retransmits: usize,
    watchdog_trips: usize,
    total_active_pulses: usize,
}

static TELEMETRY: Mutex<Telemetry> = Mutex::new(Telemetry {
    arq_retransmits: 0,
    watchdog_trips: 0,
    total_active_pulses: 0,
});

// Fixed structural hardware mapping tables (0-7 indices)
const FIXED_COLUMN_A: [u8; 4] =;
const FIXED_COLUMN_B: [u8; 4] =;
const FIXED_COLUMN_C: [u8; 4] =;
const FIXED_COLUMN_D: [u8; 4] =;

#[derive(Clone, Debug)]
pub struct PhotonSignal {
    pub voltage: f64,
    pub delay_ns: i64,
    pub wire_bus: String,
    pub pulse_width_ns: i64,
    pub is_high_energy: bool,
}

pub fn hardware_instrument_trigger(_event_type: &str, _delay_ns: i64, _voltage: f64, _channel_bus: &str) {}

pub fn vse_engine_optical_transmitter(chunk_bytes: &[u8]) -> Vec<PhotonSignal> {
    let mut photon_stream = Vec::with_capacity(chunk_bytes.len() * 2);

    for &byte in chunk_bytes {
        let vector_a = (byte >> 5) & 0x07;
        let bit_4 = (byte >> 4) & 0x01;
        let bit_5 = (byte >> 3) & 0x01;
        let vector_c = byte & 0x07;

        // --- PHASE 1: FIRST COMBINED PULSE ---
        let duration_1 = if bit_4 == 0 { 5 } else { 15 };
        let (wire_bus_1, voltage_1, time_slot_idx_1) = if FIXED_COLUMN_A.contains(&vector_a) {
            let idx = FIXED_COLUMN_A.iter().position(|&x| x == vector_a).unwrap();
            ("A".to_string(), VOLTAGE_POS, idx + 1)
        } else {
            let idx = FIXED_COLUMN_B.iter().position(|&x| x == vector_a).unwrap();
            ("B".to_string(), VOLTAGE_NEG, idx + 1)
        };

        photon_stream.push(PhotonSignal {
            voltage: voltage_1,
            delay_ns: (time_slot_idx_1 as i64) * 10,
            wire_bus: wire_bus_1,
            pulse_width_ns: duration_1,
            is_high_energy: bit_4 == 1,
        });

        // --- PHASE 2: SECOND COMBINED PULSE ---
        let duration_2 = if bit_5 == 0 { 5 } else { 15 };
        let (wire_bus_2, voltage_2, time_slot_idx_2) = if FIXED_COLUMN_C.contains(&vector_c) {
            let idx = FIXED_COLUMN_C.iter().position(|&x| x == vector_c).unwrap();
            ("A".to_string(), VOLTAGE_POS, idx + 1)
        } else {
            let idx = FIXED_COLUMN_D.iter().position(|&x| x == vector_c).unwrap();
            ("B".to_string(), VOLTAGE_NEG, idx + 1)
        };

        photon_stream.push(PhotonSignal {
            voltage: voltage_2,
            delay_ns: (time_slot_idx_2 as i64) * 10,
            wire_bus: wire_bus_2,
            pulse_width_ns: duration_2,
            is_high_energy: bit_5 == 1,
        });
    }

    photon_stream
}

pub fn inject_channel_faults(photon_stream: &[PhotonSignal], force_drop: bool) -> Vec<PhotonSignal> {
    let mut rng = rand::thread_rng();
    if force_drop {
        return photon_stream
            .iter()
            .map(|sig| PhotonSignal {
                voltage: 0.01,
                ..sig.clone()
            })
            .collect();
    }

    let mut noisy_stream = Vec::with_capacity(photon_stream.len());
    for signal in photon_stream {
        let mut noisy_signal = signal.clone();
        if signal.voltage.abs() > 0.1 {
            let noise = rng.gen_range(-0.08..0.08);
            noisy_signal.voltage = ((signal.voltage + noise) * 10000.0).round() / 10000.0;

            let jitter = rng.gen_range(-1..=1);
            noisy_signal.delay_ns = std::cmp::max(10, signal.delay_ns + jitter);
            noisy_signal.pulse_width_ns = std::cmp::max(3, signal.pulse_width_ns + jitter);
        }
        noisy_stream.push(noisy_signal);
    }
    noisy_stream
}

fn schmitt_trigger_amplitude_filter(voltage: f64) -> &'static str {
    if (-1.25..=-0.75).contains(&voltage) { return "B"; }
    if (0.75..=1.25).contains(&voltage) { return "A"; }
    if (-0.20..=0.20).contains(&voltage) { return "DROP_ERR"; }
    "UNKNOWN_ERROR"
}

pub fn vse_engine_optical_receiver(photon_stream: &[PhotonSignal], expected_bytes_count: usize) -> (Option<Vec<u8>>, bool) {
    let mut decoded_buffer = Vec::new();
    let mut current_byte: u8 = 0;
    let mut processing_phase = 0;

    for signal in photon_stream {
        hardware_instrument_trigger("RECEIVE_EVENT", signal.delay_ns, signal.voltage, &signal.wire_bus);
        let detected_layer = schmitt_trigger_amplitude_filter(signal.voltage);

        if detected_layer == "UNKNOWN_ERROR" || detected_layer == "DROP_ERR" {
            if detected_layer == "DROP_ERR" {
                if let Ok(mut tel) = TELEMETRY.lock() {
                    tel.watchdog_trips += 1;
                }
            }
            return (None, true);
        }

        let calculated_idx = (((signal.delay_ns as f64) / 10.0).round() as i64) - 1;
        if !(0..4).contains(&calculated_idx) {
            return (None, true);
        }
        let calculated_idx = calculated_idx as usize;

        let decoded_trigger = if signal.pulse_width_ns <= 9 { 0 } else { 1 };

        if processing_phase == 0 {
            let target_vector = if detected_layer == "A" { FIXED_COLUMN_A[calculated_idx] } else { FIXED_COLUMN_B[calculated_idx] };
            current_byte = (target_vector << 5) | (decoded_trigger << 4);
            processing_phase = 1;
        } else {
            let target_vector = if detected_layer == "A" { FIXED_COLUMN_C[calculated_idx] } else { FIXED_COLUMN_D[calculated_idx] };
            current_byte |= (decoded_trigger << 3) | target_vector;

            decoded_buffer.push(current_byte);
            current_byte = 0;
            processing_phase = 0;
        }
    }

    if decoded_buffer.len() > expected_bytes_count {
        decoded_buffer.truncate(expected_bytes_count);
    }
    (Some(decoded_buffer), false)
}

pub fn run_production_stress_test() -> (usize, f64) {
    let poem_data = "Two roads diverged in a yellow wood,\n\
                     And sorry I could not travel both\n\
                     And be one traveler, long I stood\n\
                     And looked down one as far as I could\n\
                     To where it bent in the undergrowth;\n\n\
                     Then took the other, as just as fair,\n\
                     And having perhaps the better claim,\n\
                     Because it was grassy and wanted wear;\n\
                     Though as for that the passing there\n\
                     Had worn them really about the same,\n\n\
                     And both that morning equally lay\n\
                     In leaves no step had trodden black.\n\
                     Oh, I kept the first for another day!\n\
                     Yet knowing how way leads on to way,\n\
                     I doubted if I should ever come back.\n\n\
                     I shall be telling this with a sigh\n\
                     Somewhere ages and ages hence:\n\
                     Two roads diverged in a wood, and I—\n\
                     I took the one less traveled by,\n\
                     And that has made all the difference."
        .repeat(40);

    let raw_payload = poem_data.as_bytes();
    let chunk_size = 16;
    let mut final_output_stream = Vec::new();
    let start_bench_time = Instant::now();

    let chunks: Vec<&[u8]> = raw_payload.chunks(chunk_size).collect();
    let mut rng = rand::thread_rng();

    for chunk in chunks {
        let mut transmission_successful = false;

        while !transmission_successful {
            let photon_stream = vse_engine_optical_transmitter(chunk);
            let force_drop = rng.gen_bool(0.02);
            let noisy_stream = inject_channel_faults(&photon_stream, force_drop);
            let (decoded_chunk, error_detected) = vse_engine_optical_receiver(&noisy_stream, chunk.len());

            if error_detected || decoded_chunk.is_none() {
                if let Ok(mut tel) = TELEMETRY.lock() {
                    tel.arq_retransmits += 1;
                }
                continue;
            }

            if let Some(decoded) = decoded_chunk {
                if let Ok(mut tel) = TELEMETRY.lock() {
                    tel.total_active_pulses += photon_stream.iter().filter(|sig| sig.is_high_energy).count();
                }
                final_output_stream.extend(decoded);
                transmission_successful = true;
            }
        }
    }

    let duration = start_bench_time.elapsed().as_secs_f64();
    (final_output_stream.len(), duration)
}

fn main() {
    println!("VSE Engine Optical Production Stress Test indítása...");
    let (bytes_count, duration) = run_production_stress_test();
    
    if let Ok(tel) = TELEMETRY.lock() {
        println!("--- TESZT EREDMÉNYEK ---");
        println!("Feldolgozott adatmennyiség: {} bájt", bytes_count);
        println!("Futásidő: {:.4} másodperc", duration);
        println!("ARQ Újraküldések száma: {}", tel.arq_retransmits);
        println!("Watchdog lekapcsolások (Trips): {}", tel.watchdog_trips);
        println!("Összes aktív nagy energiájú impulzus: {}", tel.total_active_pulses);
    }
}
