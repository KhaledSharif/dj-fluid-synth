# Enhanced EDM Generator with Professional Festival-Ready Features
# Adds pitch bends, filter automation, better synths, and modern production techniques

import sys
import yaml
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, savgol_filter
from scipy.ndimage import gaussian_filter1d

# Note to frequency conversion
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def note_to_freq(note):
    if note == "rest" or note == "":
        return 0
    octave = int(note[-1]) if note[-1].isdigit() else 4
    note_name = note[:-1] if note[-1].isdigit() else note
    
    # Handle flat notes (e.g., Bb becomes A#)
    # Check for flat only if note_name has more than one character and second char is 'b'
    if len(note_name) > 1 and note_name[1].lower() == 'b':
        base_note = note_name[0].upper()
        base_idx = NOTES.index(base_note)
        # Flat means one semitone down
        semitones = (base_idx - 1) % 12
    else:
        semitones = NOTES.index(note_name.upper())
    
    return 440 * (2 ** ((octave - 4) + (semitones - 9) / 12))


# Enhanced ADSR envelope with curve control
def apply_envelope(
    wave, duration, fs, attack=0.01, decay=0.1, sustain=0.5, release=0.1, curve=1.0
):
    n_samples = len(wave)
    if n_samples == 0:
        return wave

    t = np.linspace(0, duration, n_samples)
    envelope = np.ones(n_samples)
    attack_samples = min(int(attack * fs), n_samples)
    decay_samples = min(int(decay * fs), n_samples - attack_samples)
    release_samples = min(int(release * fs), n_samples)
    sustain_level = sustain

    if attack_samples > 0:
        attack_curve = np.linspace(0, 1, attack_samples) ** curve
        envelope[:attack_samples] = attack_curve

    if decay_samples > 0:
        start_decay = attack_samples
        end_decay = min(start_decay + decay_samples, n_samples - release_samples)
        actual_decay_samples = end_decay - start_decay
        if actual_decay_samples > 0:
            decay_curve = 1 - (np.linspace(0, 1, actual_decay_samples) ** curve) * (
                1 - sustain_level
            )
            envelope[start_decay:end_decay] = decay_curve

    start_release = max(0, n_samples - release_samples)
    if release_samples > 0 and start_release < n_samples:
        actual_release_samples = n_samples - start_release
        release_curve = sustain_level * (
            1 - np.linspace(0, 1, actual_release_samples) ** curve
        )
        envelope[start_release:] = release_curve

    return wave * envelope


# Filter functions
def apply_lowpass(wave, cutoff, fs, resonance=1):
    nyquist = fs / 2
    
    # Handle both scalar and array cutoff values
    if np.isscalar(cutoff):
        normalized_cutoff = min(cutoff / nyquist, 0.99)
        b, a = butter(2, normalized_cutoff, btype="low")
        filtered = lfilter(b, a, wave)
        # Add resonance by mixing with bandpass
        if resonance > 1:
            bp_b, bp_a = butter(
                2,
                [normalized_cutoff * 0.9, min(normalized_cutoff * 1.1, 0.99)],
                btype="band",
            )
            resonant = lfilter(bp_b, bp_a, wave)
            filtered = filtered + resonant * (resonance - 1) * 0.3
    else:
        # For time-varying cutoff, use the median cutoff value as a compromise
        # This is a simplified approach that avoids sample-by-sample processing
        median_cutoff = np.median(cutoff)
        normalized_cutoff = min(median_cutoff / nyquist, 0.99)
        b, a = butter(2, normalized_cutoff, btype="low")
        filtered = lfilter(b, a, wave)
        
        # Apply amplitude envelope based on cutoff sweep
        envelope = np.interp(np.arange(len(wave)), 
                            np.linspace(0, len(wave)-1, len(cutoff)), 
                            cutoff / np.max(cutoff))
        filtered = filtered * envelope
    
    return filtered


def apply_highpass(wave, cutoff, fs):
    nyquist = fs / 2
    normalized_cutoff = min(cutoff / nyquist, 0.99)
    b, a = butter(2, normalized_cutoff, btype="high")
    return lfilter(b, a, wave)


# Enhanced instrument generators
def generate_kick(duration, fs, punch=1.0):
    t = np.linspace(0, duration, int(fs * duration))
    # Enhanced kick with sub harmonics
    freq = 60 + 200 * punch * np.exp(-t / 0.05)
    wave = np.sin(2 * np.pi * np.cumsum(freq) / fs)
    # Add click for punch
    click = np.sin(2 * np.pi * 150 * t) * np.exp(-t / 0.002)
    wave = wave + click * 0.3
    # Add sub bass tail
    sub = np.sin(2 * np.pi * 50 * t) * np.exp(-t / 0.15)
    wave = wave * 0.7 + sub * 0.3
    wave = apply_envelope(
        wave, duration, fs, attack=0.002, decay=0.2, sustain=0.1, release=0.1, curve=2
    )
    return np.tanh(wave * 1.2) * 0.9  # Soft saturation


def generate_hihat(duration, fs, tone=0.5):
    samples = int(fs * duration)
    # Mix noise with metallic tone
    wave = np.random.uniform(-1, 1, samples)
    # Add metallic resonance
    t = np.linspace(0, duration, samples)
    metallic = np.sin(2 * np.pi * 8000 * t) * tone
    wave = wave * (1 - tone) + metallic
    wave = apply_highpass(wave, 4000, fs)
    wave = apply_envelope(
        wave, duration, fs, attack=0.002, decay=0.03, sustain=0.0, release=0.02
    )
    return wave * 0.3


def generate_snare(duration, fs, tone=0.5):
    t = np.linspace(0, duration, int(fs * duration))
    # Enhanced snare with multiple tones
    tone1 = np.sin(2 * np.pi * 200 * t)
    tone2 = np.sin(2 * np.pi * 300 * t)
    tones = (tone1 + tone2 * 0.7) * tone
    noise = np.random.uniform(-1, 1, int(fs * duration))
    noise = apply_highpass(noise, 200, fs)
    wave = tones * 0.4 + noise * 0.6
    wave = apply_envelope(
        wave, duration, fs, attack=0.002, decay=0.03, sustain=0.0, release=0.05
    )
    return np.tanh(wave) * 0.6


def generate_clap(duration, fs):
    wave = np.zeros(int(fs * duration))
    num_claps = 4
    clap_spacing = 0.008
    for i in range(num_claps):
        start = int(i * clap_spacing * fs)
        clap_len = min(int(0.008 * fs), len(wave) - start)
        if clap_len > 0:
            clap_hit = np.random.uniform(-1, 1, clap_len)
            wave[start : start + clap_len] = clap_hit * (0.7 + i * 0.1)
    wave = apply_highpass(wave, 1000, fs)
    wave = apply_envelope(
        wave, duration, fs, attack=0.001, decay=0.02, sustain=0.0, release=0.04
    )
    return wave * 0.5


def generate_supersaw(freq, duration, fs, detune=0.03, voices=7):
    """Generate supersaw lead sound (signature of progressive house)"""
    if freq == 0:
        return np.zeros(int(fs * duration))

    t = np.linspace(0, duration, int(fs * duration))
    wave = np.zeros(len(t))

    for i in range(voices):
        detune_factor = 1 + (i - voices // 2) * detune / voices
        # Saw wave
        voice = 2 * (
            freq * detune_factor * t - np.floor(0.5 + freq * detune_factor * t)
        )
        # Add slight phase randomization
        phase_shift = np.random.random() * 2 * np.pi
        voice = np.roll(voice, int(phase_shift * fs / (2 * np.pi * freq)))
        wave += voice / voices

    # Add subtle pulse width modulation
    lfo = np.sin(2 * np.pi * 3 * t) * 0.02
    wave = wave * (1 + lfo)

    # Filter for warmth
    wave = apply_lowpass(
        wave, 4000 + 2000 * np.sin(2 * np.pi * 0.5 * t), fs, resonance=1.5
    )
    wave = apply_envelope(
        wave, duration, fs, attack=0.02, decay=0.1, sustain=0.7, release=0.2
    )
    return wave * 0.4


def generate_future_bass(freq, duration, fs):
    """Generate future bass sound with characteristic wobble"""
    if freq == 0:
        return np.zeros(int(fs * duration))

    t = np.linspace(0, duration, int(fs * duration))

    # Multiple detuned saw oscillators
    wave1 = 2 * (freq * t - np.floor(0.5 + freq * t))
    wave2 = 2 * (freq * 1.01 * t - np.floor(0.5 + freq * 1.01 * t))
    wave3 = np.sin(2 * np.pi * freq * 0.5 * t)  # Sub octave

    wave = (wave1 + wave2 * 0.8) * 0.4 + wave3 * 0.3

    # Characteristic filter wobble
    wobble_rate = 4  # Hz
    filter_env = 1000 + 3000 * (1 + np.sin(2 * np.pi * wobble_rate * t))
    wave = apply_lowpass(wave, filter_env, fs, resonance=2)

    wave = apply_envelope(
        wave, duration, fs, attack=0.01, decay=0.05, sustain=0.6, release=0.1
    )
    return wave * 0.5


def generate_reese_bass(freq, duration, fs):
    """Generate Reese bass with characteristic phasing"""
    if freq == 0:
        return np.zeros(int(fs * duration))

    t = np.linspace(0, duration, int(fs * duration))

    # Two slightly detuned saw waves
    wave1 = 2 * (freq * t - np.floor(0.5 + freq * t))
    wave2 = 2 * (freq * 1.007 * t - np.floor(0.5 + freq * 1.007 * t))

    # Mix creates phasing effect
    wave = (wave1 + wave2) * 0.5

    # Add sub sine for weight
    sub = np.sin(2 * np.pi * freq * 0.5 * t) * 0.3
    wave = wave * 0.7 + sub

    # Low pass for warmth
    wave = apply_lowpass(wave, 400, fs, resonance=1.2)
    wave = apply_envelope(
        wave, duration, fs, attack=0.01, decay=0.1, sustain=0.8, release=0.1
    )
    return wave * 0.7


def generate_pluck_bass(freq, duration, fs):
    """Generate plucky bass sound common in progressive house"""
    if freq == 0:
        return np.zeros(int(fs * duration))

    t = np.linspace(0, duration, int(fs * duration))

    # Start with saw and square mix
    saw = 2 * (freq * t - np.floor(0.5 + freq * t))
    square = np.sign(np.sin(2 * np.pi * freq * t))
    wave = saw * 0.6 + square * 0.4

    # Add sub
    sub = np.sin(2 * np.pi * freq * 0.5 * t)
    wave = wave * 0.7 + sub * 0.3

    # Plucky envelope with fast decay
    wave = apply_envelope(
        wave, duration, fs, attack=0.001, decay=0.15, sustain=0.2, release=0.1
    )

    # Filter sweep down
    cutoff_env = 3000 * np.exp(-t / 0.1) + 200
    wave = apply_lowpass(wave, cutoff_env, fs, resonance=1.5)

    return wave * 0.8


def generate_dubstep_bass(freq, duration, fs, wobble_rate=2):
    """Generate dubstep wobble bass"""
    if freq == 0:
        return np.zeros(int(fs * duration))

    t = np.linspace(0, duration, int(fs * duration))

    # Heavy sub sine
    wave = np.sin(2 * np.pi * freq * t)

    # Add harmonics for grit
    wave += np.sin(2 * np.pi * freq * 2 * t) * 0.3
    wave += np.sin(2 * np.pi * freq * 3 * t) * 0.15

    # LFO for wobble
    lfo = (1 + np.sin(2 * np.pi * wobble_rate * t)) * 0.5

    # Apply filter wobble
    cutoff = 100 + 500 * lfo
    wave = apply_lowpass(wave, cutoff, fs, resonance=2)

    # Volume wobble
    wave = wave * (0.3 + 0.7 * lfo)

    wave = apply_envelope(
        wave, duration, fs, attack=0.01, decay=0.05, sustain=0.9, release=0.05
    )
    return wave * 0.8


def generate_white_noise_riser(duration, fs):
    """Generate white noise riser for transitions"""
    t = np.linspace(0, duration, int(fs * duration))
    wave = np.random.uniform(-1, 1, int(fs * duration))

    # Filter sweep up
    cutoff_env = 200 + 8000 * (t / duration) ** 2
    wave = apply_lowpass(wave, cutoff_env, fs)

    # Volume envelope
    envelope = (t / duration) ** 2
    wave = wave * envelope

    return wave * 0.3


def generate_impact(duration, fs):
    """Generate impact/crash sound for drop emphasis"""
    t = np.linspace(0, duration, int(fs * duration))

    # Mix of low boom and white noise
    boom = np.sin(2 * np.pi * 40 * t) * np.exp(-t / 0.3)
    crash = np.random.uniform(-1, 1, int(fs * duration))
    crash = apply_highpass(crash, 2000, fs)

    wave = boom * 0.6 + crash * 0.4
    wave = apply_envelope(
        wave, duration, fs, attack=0.001, decay=0.5, sustain=0.3, release=0.5
    )

    return wave * 0.7


def generate_pitch_bend_bass(start_note, end_note, duration, fs, bass_type="pluck"):
    """Generate bass with pitch bend between notes"""
    start_freq = note_to_freq(start_note)
    end_freq = note_to_freq(end_note)

    if start_freq == 0 and end_freq == 0:
        return np.zeros(int(fs * duration))

    t = np.linspace(0, duration, int(fs * duration))

    # Create pitch bend curve (exponential for musical pitch bend)
    if start_freq > 0 and end_freq > 0:
        freq_curve = start_freq * (end_freq / start_freq) ** (t / duration)
    elif start_freq > 0:
        freq_curve = start_freq * np.ones_like(t)
    else:
        freq_curve = end_freq * np.ones_like(t)

    # Generate the appropriate bass type with pitch bend
    phase = 2 * np.pi * np.cumsum(freq_curve) / fs

    if bass_type == "pluck":
        wave = np.sin(phase) * 0.5 + 0.5 * np.sign(np.sin(phase))
        wave = apply_envelope(
            wave, duration, fs, attack=0.001, decay=0.15, sustain=0.2, release=0.1
        )
    elif bass_type == "reese":
        wave1 = 2 * (phase / (2 * np.pi) - np.floor(0.5 + phase / (2 * np.pi)))
        phase2 = 2 * np.pi * np.cumsum(freq_curve * 1.007) / fs
        wave2 = 2 * (phase2 / (2 * np.pi) - np.floor(0.5 + phase2 / (2 * np.pi)))
        wave = (wave1 + wave2) * 0.5
        wave = apply_lowpass(wave, 400, fs)
        wave = apply_envelope(
            wave, duration, fs, attack=0.01, decay=0.1, sustain=0.8, release=0.1
        )
    else:
        wave = np.sin(phase)
        wave = apply_envelope(
            wave, duration, fs, attack=0.01, decay=0.1, sustain=0.7, release=0.1
        )

    return wave * 0.7


def apply_sidechain(audio, kick_times, fs, tempo, strength=0.7, style="pump"):
    """Enhanced sidechain with different styles"""
    beat_duration = 60 / tempo

    if style == "pump":
        attack_time = 0.005
        release_time = beat_duration * 0.25
    elif style == "duck":
        attack_time = 0.01
        release_time = beat_duration * 0.4
    else:  # subtle
        attack_time = 0.02
        release_time = beat_duration * 0.15
        strength = strength * 0.5

    envelope = np.ones(len(audio))

    for kick_time in kick_times:
        attack_start = int(kick_time * fs)
        attack_samples = int(attack_time * fs)
        release_samples = int(release_time * fs)

        if attack_start < len(audio):
            attack_end = min(attack_start + attack_samples, len(audio))
            if attack_end > attack_start:
                envelope[attack_start:attack_end] = np.linspace(
                    envelope[attack_start] if attack_start > 0 else 1,
                    1 - strength,
                    attack_end - attack_start,
                )

            release_start = attack_end
            release_end = min(release_start + release_samples, len(audio))
            if release_end > release_start:
                t = np.linspace(0, 1, release_end - release_start)
                release_curve = 1 - (1 - (1 - strength)) * np.exp(-5 * t)
                envelope[release_start:release_end] = release_curve

    # Smooth the envelope
    envelope = gaussian_filter1d(envelope, sigma=30)

    return audio * envelope


def apply_automation(wave, automation_type, duration, fs, amount=1.0):
    """Apply various automation curves to audio"""
    t = np.linspace(0, duration, len(wave))

    if automation_type == "fade_in":
        curve = t / duration
    elif automation_type == "fade_out":
        curve = 1 - (t / duration)
    elif automation_type == "swell":
        curve = np.sin(np.pi * t / duration)
    elif automation_type == "pulse":
        curve = 0.5 + 0.5 * np.sin(2 * np.pi * 4 * t)  # 4 Hz pulse
    else:
        curve = np.ones_like(t)

    return wave * (1 - amount + amount * curve)


# Keep all original generators for backward compatibility
def generate_bass(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    wave = np.sin(2 * np.pi * freq * t)
    wave = apply_envelope(
        wave, duration, fs, attack=0.01, decay=0.1, sustain=0.6, release=0.1
    )
    return wave * 0.7


def generate_sub_bass(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    wave = np.sin(2 * np.pi * freq * t) * 0.8 + np.sin(2 * np.pi * freq * 2 * t) * 0.2
    wave = apply_envelope(
        wave, duration, fs, attack=0.01, decay=0.05, sustain=0.8, release=0.1
    )
    return wave * 0.8


def generate_melody(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    wave = 2 * (freq * t - np.floor(0.5 + freq * t))
    wave = apply_envelope(
        wave, duration, fs, attack=0.05, decay=0.2, sustain=0.4, release=0.2
    )
    return wave * 0.5


def generate_pad(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    wave = (
        np.sin(2 * np.pi * freq * t)
        + np.sin(2 * np.pi * freq * 1.01 * t) * 0.7
        + np.sin(2 * np.pi * freq * 2 * t) * 0.3
        + np.sin(2 * np.pi * freq * 0.5 * t) * 0.4
    ) / 2.4
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
    envelope_shape = (
        np.linspace(0, 1, len(t)) if not reverse else np.linspace(1, 0, len(t))
    )
    wave = wave * envelope_shape
    return wave * 0.3


def generate_pluck(freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))

    buffer_size = int(fs / freq)
    samples = int(fs * duration)
    buffer = np.random.uniform(-1, 1, buffer_size)
    output = np.zeros(samples)

    for i in range(samples):
        output[i] = buffer[i % buffer_size]
        buffer[i % buffer_size] = (
            0.996 * 0.5 * (buffer[i % buffer_size] + buffer[(i + 1) % buffer_size])
        )

    envelope = apply_envelope(
        output, duration, fs, attack=0.001, decay=0.1, sustain=0.3, release=0.2
    )
    return envelope * 0.6


def generate_arp(freq, duration, fs, pattern=[1, 1.5, 2, 1.5]):
    if freq == 0:
        return np.zeros(int(fs * duration))

    samples = int(fs * duration)
    t = np.linspace(0, duration, samples)
    wave = np.zeros(samples)

    arp_duration = duration / len(pattern)
    for i, mult in enumerate(pattern):
        start = int(i * arp_duration * fs)
        end = min(int((i + 1) * arp_duration * fs), samples)
        if end > start:
            t_seg = np.linspace(0, arp_duration, end - start)
            saw = 2 * (mult * freq * t_seg - np.floor(0.5 + mult * freq * t_seg))
            square = np.sign(np.sin(2 * np.pi * mult * freq * t_seg))
            wave[start:end] = 0.6 * saw + 0.4 * square

    wave = apply_envelope(
        wave, duration, fs, attack=0.01, decay=0.05, sustain=0.4, release=0.1
    )
    return wave * 0.4


def generate_percussion(duration, fs):
    t = np.linspace(0, duration, int(fs * duration))
    wave = (
        np.sin(2 * np.pi * 800 * t) * 0.5
        + np.sin(2 * np.pi * 1200 * t) * 0.3
        + np.sin(2 * np.pi * 2000 * t) * 0.2
    )
    transient = np.random.uniform(-1, 1, min(int(0.002 * fs), len(wave)))
    wave[: len(transient)] += transient * 0.5
    wave = apply_envelope(
        wave, duration, fs, attack=0.001, decay=0.02, sustain=0.0, release=0.01
    )
    return wave * 0.4


# Main function with enhanced features
def generate_edm_from_yaml(yaml_file, output_wav):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)

    tempo = data["tempo"]
    fs = data.get("sample_rate", 44100)
    beat_duration = 60 / tempo
    bar_duration = beat_duration * 4
    sidechain_enabled = data.get("sidechain", False)
    sidechain_style = data.get("sidechain_style", "pump")

    # Calculate total duration
    total_duration = sum(section["bars"] * bar_duration for section in data["sections"])
    audio = np.zeros(int(total_duration * fs), dtype=np.float32)
    kick_times = []

    current_time = 0.0
    for section in data["sections"]:
        num_bars = section["bars"]
        section_duration = num_bars * bar_duration

        for track in section["tracks"]:
            track_type = track["type"]
            volume = track.get("volume", 1.0)

            # Drum tracks
            if track_type in ["kick", "hihat", "snare", "clap", "percussion"]:
                pattern = track["pattern"]
                pattern_len = len(pattern)
                for bar in range(num_bars):
                    for beat in range(4):
                        if isinstance(pattern[beat % pattern_len], (int, float)):
                            velocity = pattern[beat % pattern_len]
                        else:
                            velocity = 1 if pattern[beat % pattern_len] else 0

                        if velocity > 0:
                            drum_dur = beat_duration * 0.5
                            hit_time = (
                                current_time + bar * bar_duration + beat * beat_duration
                            )

                            if track_type == "kick":
                                punch = track.get("punch", 1.0)
                                wave = generate_kick(drum_dur, fs, punch)
                                kick_times.append(hit_time)
                            elif track_type == "snare":
                                tone = track.get("tone", 0.5)
                                wave = generate_snare(drum_dur, fs, tone)
                            elif track_type == "clap":
                                wave = generate_clap(drum_dur, fs)
                            elif track_type == "percussion":
                                wave = generate_percussion(drum_dur, fs)
                            else:
                                tone = track.get("tone", 0.5)
                                wave = generate_hihat(drum_dur, fs, tone)

                            wave = wave * velocity * volume
                            start_sample = int(hit_time * fs)
                            audio[
                                start_sample : start_sample + len(wave)
                            ] += wave.astype(np.float32)

            # Enhanced melodic tracks
            elif track_type in [
                "bass",
                "sub_bass",
                "melody",
                "pad",
                "pluck",
                "arp",
                "supersaw",
                "future_bass",
                "reese_bass",
                "pluck_bass",
                "dubstep_bass",
                "pitch_bend_bass",
            ]:
                notes = track.get("notes", [])
                durations = track.get("durations", [])

                if track_type == "pitch_bend_bass":
                    # Handle pitch bend bass specially
                    bend_notes = track.get("bend_notes", [])
                    bass_style = track.get("bass_style", "pluck")
                    seq_len = len(notes)
                    pos = 0.0
                    idx = 0

                    while pos < section_duration:
                        start_note = notes[idx % seq_len]
                        end_note = (
                            bend_notes[idx % len(bend_notes)]
                            if bend_notes
                            else start_note
                        )
                        dur_beats = durations[idx % len(durations)]
                        note_dur = dur_beats * beat_duration

                        if pos + note_dur > section_duration:
                            note_dur = section_duration - pos

                        wave = generate_pitch_bend_bass(
                            start_note, end_note, note_dur, fs, bass_style
                        )
                        wave = wave * volume
                        start_sample = int((current_time + pos) * fs)
                        audio[start_sample : start_sample + len(wave)] += wave.astype(
                            np.float32
                        )

                        pos += dur_beats * beat_duration
                        idx += 1
                else:
                    # Regular melodic tracks
                    seq_len = len(notes)
                    pos = 0.0
                    idx = 0

                    while pos < section_duration:
                        note = notes[idx % seq_len]
                        dur_beats = durations[idx % len(durations)]
                        note_dur = dur_beats * beat_duration

                        if pos + note_dur > section_duration:
                            note_dur = section_duration - pos

                        freq = note_to_freq(note)

                        # Generate appropriate waveform
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
                        elif track_type == "supersaw":
                            detune = track.get("detune", 0.03)
                            voices = track.get("voices", 7)
                            wave = generate_supersaw(freq, note_dur, fs, detune, voices)
                        elif track_type == "future_bass":
                            wave = generate_future_bass(freq, note_dur, fs)
                        elif track_type == "reese_bass":
                            wave = generate_reese_bass(freq, note_dur, fs)
                        elif track_type == "pluck_bass":
                            wave = generate_pluck_bass(freq, note_dur, fs)
                        elif track_type == "dubstep_bass":
                            wobble_rate = track.get("wobble_rate", 2)
                            wave = generate_dubstep_bass(
                                freq, note_dur, fs, wobble_rate
                            )
                        else:
                            wave = generate_melody(freq, note_dur, fs)

                        # Apply automation if specified
                        automation = track.get("automation", None)
                        if automation:
                            wave = apply_automation(wave, automation, note_dur, fs)

                        wave = wave * volume
                        start_sample = int((current_time + pos) * fs)
                        audio[start_sample : start_sample + len(wave)] += wave.astype(
                            np.float32
                        )

                        pos += dur_beats * beat_duration
                        idx += 1

            # FX tracks
            elif track_type == "sweep":
                sweep_dur = section_duration
                reverse = track.get("reverse", False)
                start_freq = track.get("start_freq", 100)
                end_freq = track.get("end_freq", 8000)
                wave = generate_sweep(sweep_dur, fs, start_freq, end_freq, reverse)
                wave = wave * volume
                start_sample = int(current_time * fs)
                audio[start_sample : start_sample + len(wave)] += wave.astype(
                    np.float32
                )

            elif track_type == "white_noise_riser":
                riser_dur = section_duration
                wave = generate_white_noise_riser(riser_dur, fs)
                wave = wave * volume
                start_sample = int(current_time * fs)
                audio[start_sample : start_sample + len(wave)] += wave.astype(
                    np.float32
                )

            elif track_type == "impact":
                impact_dur = beat_duration * 2
                wave = generate_impact(impact_dur, fs)
                wave = wave * volume
                start_sample = int(current_time * fs)
                audio[start_sample : start_sample + len(wave)] += wave.astype(
                    np.float32
                )

        current_time += section_duration

    # Apply sidechain compression
    if sidechain_enabled and kick_times:
        sidechain_strength = data.get("sidechain_strength", 0.7)
        audio = apply_sidechain(
            audio, kick_times, fs, tempo, sidechain_strength, sidechain_style
        )

    # Final mastering
    # Soft clipping for loudness
    audio = np.tanh(audio * 0.7) * 1.2

    # Normalize
    max_amp = np.max(np.abs(audio))
    if max_amp > 0:
        audio = audio / max_amp * 0.95  # Leave small headroom

    audio = (audio * 32767).astype(np.int16)
    wavfile.write(output_wav, fs, audio)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py input.yml output.wav")
        sys.exit(1)

    generate_edm_from_yaml(sys.argv[1], sys.argv[2])
    print(f"Generated {sys.argv[2]} successfully!")
