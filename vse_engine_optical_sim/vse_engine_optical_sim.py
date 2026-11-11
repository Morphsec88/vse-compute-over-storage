# VSE Engine Optical Simulation

Experimental multi-parameter pulse encoding for deterministic data transmission.

## Overview

VSE Engine Optical is an early-stage proof-of-concept exploring whether multiple physical properties of a pulse can be used simultaneously to represent digital information.

In the current simulation, each 8-bit input symbol is mapped into two pulse events. Information is encoded across multiple parameters, including:

- channel / polarity
- timing position
- pulse width

The receiver independently interprets these parameters and reconstructs the original 8-bit symbol.

This repository is not intended to represent a finished optical communications system. It is a software simulation designed to make the encoding concept reproducible, inspectable and testable.

## Fault Simulation

The simulator includes a basic noisy-channel model with:

- amplitude noise
- timing jitter
- pulse-width jitter
- forced channel-drop events
- automatic retransmission (ARQ)
- watchdog-triggered error detection

The purpose of these mechanisms is to test whether the encoded state can still be reconstructed deterministically under imperfect simulated channel conditions.

## What the PoC Demonstrates

At its core, the experiment evaluates the following mapping:

8-bit input symbol
→
2 multi-parameter pulse events
→
noisy simulated channel
→
deterministic reconstruction

The current implementation is intentionally simple and still needs refinement.

It should not be interpreted as proof of equivalent efficiency on physical optical hardware.

Instead, the project is intended as a reproducible starting point for evaluating the architecture on actual photonic or optical transmission hardware.

## Efficiency

Early simulations indicate that multi-parameter pulse encoding may substantially reduce the number of discrete transmission events required relative to the serial baseline used by the simulator.

Previous versions reported "wire load reduction" based primarily on high-energy pulse counts. This metric did not represent the total physical transmission cost and should therefore not be interpreted as a measured optical bandwidth reduction.

Future benchmarks will separately account for:

- total pulse count
- pulse duration
- retransmission overhead
- estimated optical energy
- reconstruction integrity
- throughput and latency

A particularly interesting experimental target would be to determine whether transmission-load reductions in the 70%+ range remain achievable once the architecture is implemented and measured on real optical hardware.

This remains a research target, not a claimed physical result.

## Current Status

This is an early experimental project, not a production-ready communications protocol.

There is still plenty to improve.

The simulator is published so that the underlying idea can be inspected, reproduced, challenged and independently tested.

The next meaningful step is physical validation.

## License

GNU Affero General Public License v3.0 (AGPLv3)

Copyright (C) 2026 Morphsec88.

