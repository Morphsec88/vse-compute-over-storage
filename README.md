
# VSE Engine (Velocity & Structure Encoding)

### Experimental Multi-Parameter Signal Encoding — Prototype 1

VSE Engine is an early-stage proof-of-concept exploring a simple question:

**Can multiple properties of a physical transmission event represent several bits of information simultaneously?**

Instead of representing an 8-bit symbol as a conventional sequence of individual binary events, the current VSE prototype maps information into a combination of bipolar signal polarity and deterministic timing/index positions.

The objective of this repository is not to claim a finished communications protocol. It provides an inspectable and reproducible software model for experimenting with multi-parameter physical encoding.

---

## Core Encoding Model

Each 8-bit input symbol is divided into two 4-bit structures:

- Bits 1–3 select one of eight deterministic timing/index states.
- Bit 4 determines the polarity/state of the first signal.
- Bit 5 determines the polarity/state of the second signal.
- Bits 6–8 select another one of eight deterministic timing/index states.

Conceptually:

**8-bit symbol → two multi-parameter data events**

Each data event therefore carries information through more than one physical parameter:

1. its polarity/state, and
2. its timing/index position.

The current FEC-oriented simulation additionally transmits a parity event used for basic error detection and heuristic recovery.

With parity enabled, the prototype can therefore be described as:

**8 data bits → 2 multi-parameter data events + 1 parity event**

This mapping is the central concept being investigated.

---

## Deterministic State Mapping

The current prototype uses a fixed state table:

`STATE_TRANSFORM_MAP`

The mapping assigns each 3-bit vector to a deterministic physical/index state.

The receiver performs the inverse mapping to reconstruct the original vector.

This implementation is intentionally simple. The table should be understood as an experimental state-mapping mechanism rather than an optimized production lookup architecture.

---

## Receiver and Tolerance Window

The experimental receiver reconstructs each symbol from:

- detected signal polarity,
- recovered index position,
- and parity state.

The current simulation also implements a fixed index tolerance window.

Small simulated index offsets can therefore be normalized back to their expected deterministic state before decoding.

The prototype additionally includes parity-assisted heuristic error handling.

This is an experimental error-recovery mechanism and should not be interpreted as a complete production-grade Forward Error Correction (FEC) implementation.

---

## Transmission Event Reduction

The current simulation compares the VSE representation against a configurable serial baseline.

With the FEC/parity mode enabled, each 8-bit input symbol produces:

- 2 multi-parameter data events
- 1 parity event

For a baseline defined as 10 discrete serial events per byte, this corresponds to a **nominal 70% reduction in discrete transmission-event count**:

`10 baseline events → 3 VSE events`

This percentage describes event count inside the current architectural model.

It does **not** by itself establish equivalent bandwidth, power, thermal, latency, or throughput improvement on physical hardware.

Those properties require hardware measurement.

---

## Noise and Fault Simulation

The current prototype can simulate:

- bipolar voltage degradation,
- deterministic timing/index displacement,
- polarity inversion,
- tolerance-window recovery,
- parity mismatch detection.

These tests are intended to evaluate the behavior of the encoding model under controlled fault conditions.

Future versions should extend this testing to randomized noise distributions, out-of-window errors, burst errors, retransmission overhead, and measured bit-error rates.

---

## Current Status

VSE Engine is an experimental prototype.

It is not a production-ready networking protocol and has not yet been validated as a physical communications system.

The repository exists so that the encoding concept can be:

- inspected,
- reproduced,
- challenged,
- benchmarked,
- and eventually evaluated on real transmission hardware.

A major next step would be implementation on a physical electrical or optical test platform and comparison against an explicitly defined baseline.

---

## Relationship to VSE Engine Optical

The electrical/bipolar simulation and VSE Engine Optical explore the same general idea from different physical perspectives:

**information can be represented jointly across multiple measurable properties of a transmission event rather than treating every event as carrying only one binary state.**

The two implementations remain experimental and should be benchmarked independently.

---

## Licensing

This software is publicly available under the GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later).

Copyright (C) 2026 Morphsec88.

See the repository LICENSE file for the complete license terms.

---

## Commercial Licensing & Research Collaboration

Organizations interested in proprietary deployment, hardware validation, research collaboration, commercial licensing, or alternative licensing arrangements may contact:

**pakszable@gmail.com**

Additional non-public technology related to the broader research program is not included in this repository. Any disclosure of such material is subject to a separate agreement where applicable.

