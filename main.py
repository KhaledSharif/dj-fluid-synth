# This Python script generates a simple EDM track as a WAV file from a YAML description.
# It uses procedural audio synthesis with waveforms for instruments like kick, hi-hat, bass, and melody.
# Assumptions about YAML structure:
# - tempo: integer (BPM, e.g., 128)
# - sample_rate: integer (e.g., 44100, optional, default 44100)
# - sections: list of dicts, each with:
#   - name: string (e.g., "intro")
#   - bars: integer (number of bars)
#   - tracks: list of dicts, each with:
#     - type: string ("kick", "hihat", "bass", "melody")
#     - pattern: list of 0/1 for rhythm per beat in a bar (for drums)
#     - notes: list of note names (e.g., ["C2", "E3"]), with octave like C4
#     - durations: list of floats (in beats, for melodic tracks)
# Patterns and note sequences repeat as needed to fill the bars.
# Example YAML (song.yml):
# tempo: 128
# sections:
#   - name: intro
#     bars: 4
#     tracks:
#       - type: kick
#         pattern: [1, 0, 1, 0]
#       - type: hihat
#         pattern: [0, 1, 0, 1]
#       - type: bass
#         notes: ["C2", "C2", "C2", "C2"]
#         durations: [1, 1, 1, 1]
#       - type: melody
#         notes: ["G4", "A4", "B4", "C5"]
#         durations: [1, 1, 1, 1]
#
# Install dependencies: pip install pyyaml numpy scipy
# Run: python script.py song.yml output.wav

import sys
import yaml
import numpy as np
from scipy.io import wavfile

# Note to frequency conversion
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_freq(note):
    if note == "rest":
        return 0
    octave = int(note[-1]) if note[-1].isdigit() else 4
    note_name = note[:-1] if note[-1].isdigit() else note
    semitones = NOTES.index(note_name.upper())
    return 440 * (2 ** ((octave - 4) + (semitones - 9) / 12))


# Simple ADSR envelope (from adapted example in Medium article on generating music with Python)
def apply_envelope(
    wave, duration, fs, attack=0.01, decay=0.1, sustain=0.5, release=0.1
):
    n_samples = len(wave)
    t = np.linspace(0, duration, n_samples)
    envelope = np.ones(n_samples)
    attack_samples = min(int(attack * fs), n_samples)
    decay_samples = min(int(decay * fs), n_samples - attack_samples)
    release_samples = min(int(release * fs), n_samples)
    sustain_level = sustain

    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    if decay_samples > 0:
        start_decay = attack_samples
        end_decay = min(start_decay + decay_samples, n_samples - release_samples)
        actual_decay_samples = end_decay - start_decay
        if actual_decay_samples > 0:
            envelope[start_decay:end_decay] = np.linspace(1, sustain_level, actual_decay_samples)
    start_release = max(0, n_samples - release_samples)
    if release_samples > 0 and start_release < n_samples:
        actual_release_samples = n_samples - start_release
        envelope[start_release:] = np.linspace(sustain_level, 0, actual_release_samples)
    return wave * envelope


# Instrument generators
def generate_kick(duration, fs):
    t = np.linspace(0, duration, int(fs * duration))
    freq = 60 + 200 * np.exp(-t / 0.05)  # Pitch glide down
    wave = np.sin(2 * np.pi * np.cumsum(freq) / fs)
    wave = apply_envelope(
        wave, duration, fs, attack=0.005, decay=0.2, sustain=0.1, release=0.1
    )
    return wave * 0.8


def generate_hihat(duration, fs):
    wave = np.random.uniform(-1, 1, int(fs * duration))
    wave = apply_envelope(
        wave, duration, fs, attack=0.005, decay=0.05, sustain=0.0, release=0.01
    )
    return wave * 0.3


def generate_bass(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    wave = np.sin(2 * np.pi * freq * t)  # Simple sine for bass
    wave = apply_envelope(
        wave, duration, fs, attack=0.01, decay=0.1, sustain=0.6, release=0.1
    )
    return wave * 0.7


def generate_melody(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    # Sawtooth wave for synth lead
    wave = 2 * (freq * t - np.floor(0.5 + freq * t))
    wave = apply_envelope(
        wave, duration, fs, attack=0.05, decay=0.2, sustain=0.4, release=0.2
    )
    return wave * 0.5


def generate_snare(duration, fs):
    t = np.linspace(0, duration, int(fs * duration))
    # Mix of tone and noise for snare
    tone = np.sin(2 * np.pi * 200 * t) * 0.5
    noise = np.random.uniform(-1, 1, int(fs * duration)) * 0.5
    wave = tone + noise
    wave = apply_envelope(
        wave, duration, fs, attack=0.005, decay=0.03, sustain=0.0, release=0.02
    )
    return wave * 0.5


def generate_clap(duration, fs):
    # Multiple short bursts to simulate clap
    wave = np.zeros(int(fs * duration))
    num_claps = 3
    clap_spacing = 0.01  # seconds between mini-claps
    for i in range(num_claps):
        start = int(i * clap_spacing * fs)
        clap_len = min(int(0.01 * fs), len(wave) - start)
        if clap_len > 0:
            wave[start:start + clap_len] = np.random.uniform(-1, 1, clap_len)
    wave = apply_envelope(
        wave, duration, fs, attack=0.001, decay=0.02, sustain=0.0, release=0.03
    )
    return wave * 0.4


def generate_sub_bass(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    # Pure sine for sub bass with slight harmonic
    wave = np.sin(2 * np.pi * freq * t) * 0.8 + np.sin(2 * np.pi * freq * 2 * t) * 0.2
    wave = apply_envelope(
        wave, duration, fs, attack=0.01, decay=0.05, sustain=0.8, release=0.1
    )
    return wave * 0.8


def generate_pad(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    # Multiple detuned oscillators for rich pad sound
    wave = (np.sin(2 * np.pi * freq * t) +
            np.sin(2 * np.pi * freq * 1.01 * t) * 0.7 +
            np.sin(2 * np.pi * freq * 2 * t) * 0.3 +
            np.sin(2 * np.pi * freq * 0.5 * t) * 0.4) / 2.4
    wave = apply_envelope(
        wave, duration, fs, attack=0.3, decay=0.2, sustain=0.6, release=0.3
    )
    return wave * 0.3


def generate_sweep(duration, fs, start_freq=100, end_freq=8000, reverse=False):
    t = np.linspace(0, duration, int(fs * duration))
    if reverse:
        freq_sweep = np.linspace(end_freq, start_freq, len(t))
    else:
        freq_sweep = np.linspace(start_freq, end_freq, len(t))
    phase = 2 * np.pi * np.cumsum(freq_sweep) / fs
    wave = np.sin(phase)
    # Apply filter-like envelope
    envelope_shape = np.linspace(0, 1, len(t)) if not reverse else np.linspace(1, 0, len(t))
    wave = wave * envelope_shape
    return wave * 0.3


def generate_pluck(freq, duration, fs):
    """Generate a plucked string sound using Karplus-Strong synthesis"""
    if freq == 0:
        return np.zeros(int(fs * duration))
    
    # Calculate buffer size based on frequency
    buffer_size = int(fs / freq)
    samples = int(fs * duration)
    
    # Initialize with noise
    buffer = np.random.uniform(-1, 1, buffer_size)
    output = np.zeros(samples)
    
    # Karplus-Strong algorithm
    for i in range(samples):
        output[i] = buffer[i % buffer_size]
        # Low-pass filter (averaging)
        buffer[i % buffer_size] = 0.996 * 0.5 * (buffer[i % buffer_size] + 
                                                  buffer[(i + 1) % buffer_size])
    
    # Apply envelope for more realistic sound
    envelope = apply_envelope(output, duration, fs, attack=0.001, decay=0.1, sustain=0.3, release=0.2)
    return envelope * 0.6


def generate_arp(freq, duration, fs, pattern=[1, 1.5, 2, 1.5]):
    """Generate arpeggiated synth pattern"""
    if freq == 0:
        return np.zeros(int(fs * duration))
    
    samples = int(fs * duration)
    t = np.linspace(0, duration, samples)
    wave = np.zeros(samples)
    
    # Create arpeggio by cycling through frequency multiples
    arp_duration = duration / len(pattern)
    for i, mult in enumerate(pattern):
        start = int(i * arp_duration * fs)
        end = min(int((i + 1) * arp_duration * fs), samples)
        if end > start:
            t_seg = np.linspace(0, arp_duration, end - start)
            # Mix saw and square waves for richer sound
            saw = 2 * (mult * freq * t_seg - np.floor(0.5 + mult * freq * t_seg))
            square = np.sign(np.sin(2 * np.pi * mult * freq * t_seg))
            wave[start:end] = 0.6 * saw + 0.4 * square
    
    wave = apply_envelope(wave, duration, fs, attack=0.01, decay=0.05, sustain=0.4, release=0.1)
    return wave * 0.4


def generate_percussion(duration, fs):
    """Generate a percussion hit (like a woodblock or rim)"""
    t = np.linspace(0, duration, int(fs * duration))
    # Mix of tones for metallic/wood sound
    wave = (np.sin(2 * np.pi * 800 * t) * 0.5 +
            np.sin(2 * np.pi * 1200 * t) * 0.3 +
            np.sin(2 * np.pi * 2000 * t) * 0.2)
    # Add click transient
    transient = np.random.uniform(-1, 1, min(int(0.002 * fs), len(wave)))
    wave[:len(transient)] += transient * 0.5
    wave = apply_envelope(wave, duration, fs, attack=0.001, decay=0.02, sustain=0.0, release=0.01)
    return wave * 0.4


def apply_sidechain(audio, kick_times, fs, tempo, strength=0.7):
    """Apply sidechain compression effect triggered by kick times"""
    beat_duration = 60 / tempo
    attack_time = 0.005  # Very fast attack
    release_time = beat_duration * 0.3  # Release over 30% of beat
    
    envelope = np.ones(len(audio))
    
    for kick_time in kick_times:
        attack_start = int(kick_time * fs)
        attack_samples = int(attack_time * fs)
        release_samples = int(release_time * fs)
        
        if attack_start < len(audio):
            # Attack phase - duck down
            attack_end = min(attack_start + attack_samples, len(audio))
            if attack_end > attack_start:
                envelope[attack_start:attack_end] = np.linspace(
                    envelope[attack_start], 1 - strength, attack_end - attack_start
                )
            
            # Release phase - come back up
            release_start = attack_end
            release_end = min(release_start + release_samples, len(audio))
            if release_end > release_start:
                # Use exponential curve for smoother release
                t = np.linspace(0, 1, release_end - release_start)
                release_curve = 1 - (1 - (1 - strength)) * np.exp(-5 * t)
                envelope[release_start:release_end] = release_curve
    
    # Smooth the envelope to remove clicks
    from scipy.ndimage import gaussian_filter1d
    envelope = gaussian_filter1d(envelope, sigma=50)
    
    return audio * envelope


# Main function
def generate_edm_from_yaml(yaml_file, output_wav):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    tempo = data["tempo"]
    fs = data.get("sample_rate", 44100)
    beat_duration = 60 / tempo
    bar_duration = beat_duration * 4
    sidechain_enabled = data.get("sidechain", False)

    # Calculate total duration
    total_duration = sum(section["bars"] * bar_duration for section in data["sections"])
    audio = np.zeros(int(total_duration * fs), dtype=np.float32)
    kick_times = []  # Store kick hit times for sidechain

    current_time = 0.0
    for section in data["sections"]:
        num_bars = section["bars"]
        section_duration = num_bars * bar_duration
        for track in section["tracks"]:
            track_type = track["type"]
            volume = track.get("volume", 1.0)  # Support per-track volume
            
            if track_type in ["kick", "hihat", "snare", "clap", "percussion"]:  # Drum tracks with patterns
                pattern = track["pattern"]
                pattern_len = len(pattern)
                for bar in range(num_bars):
                    for beat in range(4):
                        # Support velocity patterns
                        if isinstance(pattern[beat % pattern_len], (int, float)):
                            velocity = pattern[beat % pattern_len]
                        else:
                            velocity = 1 if pattern[beat % pattern_len] else 0
                            
                        if velocity > 0:
                            drum_dur = beat_duration * 0.5  # Short duration for drums
                            hit_time = current_time + bar * bar_duration + beat * beat_duration
                            
                            if track_type == "kick":
                                wave = generate_kick(drum_dur, fs)
                                kick_times.append(hit_time)  # Store for sidechain
                            elif track_type == "snare":
                                wave = generate_snare(drum_dur, fs)
                            elif track_type == "clap":
                                wave = generate_clap(drum_dur, fs)
                            elif track_type == "percussion":
                                wave = generate_percussion(drum_dur, fs)
                            else:
                                wave = generate_hihat(drum_dur, fs)
                            
                            wave = wave * velocity * volume
                            start_sample = int(hit_time * fs)
                            audio[
                                start_sample : start_sample + len(wave)
                            ] += wave.astype(np.float32)
            elif track_type in [
                "bass", "sub_bass", "melody", "pad", "pluck", "arp"
            ]:  # Melodic tracks with notes and durations
                notes = track["notes"]
                durations = track["durations"]
                seq_len = len(notes)
                pos = 0.0
                idx = 0
                while pos < section_duration:
                    note = notes[idx % seq_len]
                    dur_beats = durations[idx % seq_len]
                    note_dur = dur_beats * beat_duration
                    if pos + note_dur > section_duration:
                        note_dur = section_duration - pos
                    freq = note_to_freq(note)
                    
                    if track_type == "bass":
                        wave = generate_bass(freq, note_dur, fs)
                    elif track_type == "sub_bass":
                        wave = generate_sub_bass(freq, note_dur, fs)
                    elif track_type == "pad":
                        wave = generate_pad(freq, note_dur, fs)
                    elif track_type == "pluck":
                        wave = generate_pluck(freq, note_dur, fs)
                    elif track_type == "arp":
                        wave = generate_arp(freq, note_dur, fs)
                    else:
                        wave = generate_melody(freq, note_dur, fs)
                    
                    wave = wave * volume
                    start_sample = int((current_time + pos) * fs)
                    audio[start_sample : start_sample + len(wave)] += wave.astype(
                        np.float32
                    )
                    pos += dur_beats * beat_duration
                    idx += 1
            
            elif track_type == "sweep":  # FX sweep
                sweep_dur = section_duration
                reverse = track.get("reverse", False)
                start_freq = track.get("start_freq", 100)
                end_freq = track.get("end_freq", 8000)
                wave = generate_sweep(sweep_dur, fs, start_freq, end_freq, reverse)
                wave = wave * volume
                start_sample = int(current_time * fs)
                audio[start_sample : start_sample + len(wave)] += wave.astype(np.float32)

        current_time += section_duration

    # Apply sidechain compression if enabled
    if sidechain_enabled and kick_times:
        sidechain_strength = data.get("sidechain_strength", 0.7)
        audio = apply_sidechain(audio, kick_times, fs, tempo, sidechain_strength)

    # Normalize audio
    max_amp = np.max(np.abs(audio))
    if max_amp > 0:
        audio /= max_amp
    audio = (audio * 32767).astype(np.int16)

    wavfile.write(output_wav, fs, audio)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.yml output.wav")
        sys.exit(1)
    
    generate_edm_from_yaml(sys.argv[1], sys.argv[2])
    print(f"Generated {sys.argv[2]} successfully!")
