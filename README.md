# DJ Fluid Synth - Custom EDM Generator

A Python-based EDM music generator that creates festival-ready electronic dance music from YAML configuration files. This synthesizer generates professional-quality tracks with modern production techniques including sidechain compression, filter automation, and authentic EDM instruments.

## How It Works

The system converts YAML configuration files into WAV audio files using custom synthesis algorithms. Each YAML file defines the song structure, tempo, instruments, melodies, and effects. The Python synthesizer (`main.py`) interprets these configurations and generates audio using mathematical waveform generation and DSP techniques.

## Usage

```bash
python main.py input.yml output.wav
```

## YAML Structure

### Global Configuration

```yaml
tempo: 128              # BPM (beats per minute)
sample_rate: 44100      # Audio sample rate in Hz
sidechain: true         # Enable sidechain compression
sidechain_style: pump   # Style: pump, duck, or subtle
sidechain_strength: 0.7 # Compression strength (0.0-1.0)
```

### Song Structure

Music is organized into sections, each containing multiple tracks:

```yaml
sections:
  - name: intro
    bars: 16           # Duration in 4/4 bars
    tracks:
      - type: kick
        pattern: [1, 0, 0, 0]  # 1 = hit, 0 = rest
        volume: 0.8
```

## Instrument Types

### Drum Instruments

#### **kick**

Bass drum with punchy low-end impact

- `pattern`: Beat pattern array (1 = hit, 0-1 = velocity)
- `punch`: Attack intensity (0.5-2.0, default: 1.0)
- `volume`: Overall volume (0.0-1.0)

#### **snare**

Snare drum with tonal and noise components

- `pattern`: Beat pattern array
- `tone`: Tonal vs noise balance (0.0-1.0, default: 0.5)
- `volume`: Overall volume

#### **hihat**

Hi-hat cymbal with metallic tone

- `pattern`: Beat pattern array
- `tone`: Metallic tone amount (0.0-1.0, default: 0.5)
- `volume`: Overall volume

#### **clap**

Layered clap sound (multiple quick hits)

- `pattern`: Beat pattern array
- `volume`: Overall volume

#### **percussion**

General percussion hit with multiple frequency components

- `pattern`: Beat pattern array
- `volume`: Overall volume

### Bass Instruments

#### **bass**

Basic sine wave bass

- `notes`: Note array (e.g., ["A2", "F2", "C3"])
- `durations`: Duration array in beats
- `volume`: Overall volume

#### **sub_bass**

Deep sub bass with harmonics for club systems

- `notes`: Note array (typically very low octaves)
- `durations`: Duration array in beats
- `volume`: Overall volume

#### **reese_bass**

Classic Reese bass with phasing (drum & bass signature)

- Two detuned saw waves creating movement
- `notes`: Note array
- `durations`: Duration array
- `volume`: Overall volume

#### **pluck_bass**

Plucky bass common in progressive house

- Fast attack, quick decay
- Filter envelope for punch
- `notes`: Note array
- `durations`: Duration array
- `volume`: Overall volume

#### **future_bass**

Future bass with characteristic filter wobble

- Multiple detuned oscillators
- Built-in LFO modulation
- `notes`: Note array
- `durations`: Duration array
- `volume`: Overall volume

#### **dubstep_bass**

Wobble bass for dubstep/trap

- Heavy sub with LFO modulation
- `wobble_rate`: LFO speed in Hz (default: 2)
- `notes`: Note array
- `durations`: Duration array
- `volume`: Overall volume

#### **pitch_bend_bass**

Bass with smooth pitch bending between notes

- `notes`: Starting notes array
- `bend_notes`: Target notes for bending
- `bass_style`: "pluck" or "reese"
- `durations`: Duration array
- `volume`: Overall volume

### Lead/Melody Instruments

#### **melody**

Basic saw wave lead

- `notes`: Note array
- `durations`: Duration array
- `volume`: Overall volume

#### **supersaw**

Massive detuned saw lead (progressive/trance signature)

- `detune`: Detuning amount (0.01-0.1, default: 0.03)
- `voices`: Number of voices (3-9, default: 7)
- `notes`: Note array
- `durations`: Duration array
- `volume`: Overall volume
- `automation`: Optional automation curve

#### **pluck**

Karplus-Strong plucked string synthesis

- Natural decay characteristics
- `notes`: Note array
- `durations`: Duration array
- `volume`: Overall volume

#### **arp**

Arpeggiator with customizable pattern

- `pattern`: Frequency multiplier pattern (default: [1, 1.5, 2, 1.5])
- `notes`: Root note array
- `durations`: Duration array
- `volume`: Overall volume

### Harmonic Instruments

#### **pad**

Ambient pad with multiple harmonics

- Rich, evolving texture
- Long attack/release
- `notes`: Chord note array
- `durations`: Duration array
- `volume`: Overall volume
- `automation`: "swell" works well for builds

### FX/Transition Instruments

#### **sweep**

Frequency sweep for transitions

- `start_freq`: Starting frequency (Hz)
- `end_freq`: Ending frequency (Hz)
- `reverse`: Reverse sweep direction (true/false)
- `volume`: Overall volume

#### **white_noise_riser**

Rising white noise for pre-drop tension

- Automatic filter and volume automation
- `volume`: Overall volume

#### **impact**

Crash/impact sound for drop emphasis

- Combination of low boom and high crash
- `volume`: Overall volume

## Note Format

- Standard notation: "C4", "A#3", "Bb2"
- Octave range: 0-8 (C4 = middle C)
- Flat notes: Use 'b' (e.g., "Bb3" for B-flat)
- Sharp notes: Use '#' (e.g., "F#4" for F-sharp)
- Rest: Use "rest" for silence

## Automation Types

Apply to any melodic track:

- `fade_in`: Linear fade in
- `fade_out`: Linear fade out
- `swell`: Sine curve (quiet-loud-quiet)
- `pulse`: 4Hz amplitude modulation

## Tips for Creating Great EDM

### Song Structure Best Practices

1. **Intro (8-16 bars)**
   - Start minimal with atmosphere
   - Introduce one element at a time
   - Use pads and sparse kicks
   - Add pluck melodies for interest

2. **Buildup (8 bars)**
   - Increase kick frequency
   - Add snare rolls in last 2 bars
   - Use rising sweeps or white noise
   - Introduce main melody hints

3. **Pre-Drop (4-8 bars)**
   - Maximum tension
   - Four-on-the-floor kick
   - Supersaw leads with automation
   - White noise riser essential

4. **Drop (16-32 bars)**
   - Full energy release
   - Layer multiple bass types
   - Strong sidechain compression
   - Add impact on first beat
   - Use pitch bend bass for movement

5. **Breakdown (16 bars)**
   - Remove drums partially
   - Focus on melody and emotion
   - Reintroduce elements gradually

### Production Tips

#### Rhythm & Groove

- Layer kick patterns: `[1, 0, 0.8, 0]` for syncopation
- Combine hihat patterns for complexity
- Use claps on beats 2 & 4 for house feel
- Add percussion for texture

#### Bass Design

- Layer sub_bass (50-100Hz) with pluck_bass (100-500Hz)
- Use pitch_bend_bass for interesting movement
- Reese bass great for dark/heavy sections
- Future bass for modern drops

#### Melody & Harmony

- Supersaw with 7-9 voices for big leads
- Detune 0.03-0.05 for thickness
- Layer plucks with pads for depth
- Use call-and-response patterns

#### Sidechain Settings

- `pump` style: Classic EDM pumping
- `duck` style: Subtle compression
- Strength 0.6-0.8 for most genres
- Essential for professional sound

#### Transitions

- Always use white_noise_riser before drops
- Reverse sweeps to exit sections
- Impact on drop for maximum effect
- Automate pad swells in buildups

### Genre-Specific Settings

#### Progressive House

- Tempo: 124-128 BPM
- Focus: Pluck bass, supersaw leads
- Long breakdowns with emotion
- Subtle sidechain (0.5-0.6)

#### Future Bass

- Tempo: 140-160 BPM
- Focus: Future bass, pitch bends
- Short, punchy drops
- Heavy sidechain (0.7-0.9)

#### Dubstep/Trap

- Tempo: 140-150 BPM (half-time feel)
- Focus: Dubstep bass with wobbles
- Sparse drums, heavy bass
- Wobble rate: 1-4 Hz

#### Trance

- Tempo: 130-140 BPM
- Focus: Supersaw, arps, long pads
- Epic breakdowns
- Rolling basslines

### Common Patterns

#### Drum Patterns

```yaml
# Four-on-the-floor
kick: [1, 1, 1, 1]

# Syncopated house
kick: [1, 0, 0.8, 0, 1, 0, 0.8, 0]

# Trap/Dubstep
kick: [1, 0, 0, 0, 0, 0, 1, 0]
snare: [0, 0, 0, 1, 0, 0, 0, 0]
```

#### Chord Progressions

```yaml
# Classic I-V-vi-IV
notes: ["C3", "G3", "A3", "F3"]

# Minor progression
notes: ["Am2", "F2", "C3", "G2"]

# Epic trance
notes: ["D3", "Bb2", "F3", "C3"]
```

## Example Configuration

```yaml
tempo: 128
sample_rate: 44100
sidechain: true
sidechain_style: pump
sidechain_strength: 0.7

sections:
  - name: intro
    bars: 8
    tracks:
      - type: kick
        pattern: [1, 0, 0, 0]
        volume: 0.6
      - type: pad
        notes: ["Am2", "F2", "C3", "G2"]
        durations: [4, 4, 4, 4]
        volume: 0.5
        automation: swell
      
  - name: drop
    bars: 16
    tracks:
      - type: kick
        pattern: [1, 0, 0.8, 0]
        volume: 1.0
        punch: 1.2
      - type: supersaw
        notes: ["A4", "C5", "E5", "G5"]
        durations: [1, 1, 1, 1]
        volume: 0.9
        detune: 0.04
        voices: 7
      - type: pitch_bend_bass
        notes: ["A1", "A1", "F1", "C2"]
        bend_notes: ["G1", "F1", "E1", "G1"]
        durations: [1, 1, 1, 1]
        bass_style: pluck
        volume: 0.8
```

## Testing

### Running Unit Tests

The project includes comprehensive unit tests organized into three modules:

- `test_core.py` - Tests for core functionality (note conversion, envelopes, filters, sidechain)
- `test_instruments.py` - Tests for all instrument generators and synths
- `test_yaml_generation.py` - Tests for YAML file processing and track generation

#### Run All Tests

```bash
# Run all tests with verbose output
python -m unittest discover tests -v

# Run a specific test module
python -m unittest tests.test_core -v

# Run a specific test class
python -m unittest tests.test_core.TestNoteConversion -v

# Run a specific test method
python -m unittest tests.test_core.TestNoteConversion.test_note_to_freq_basic
```

### Code Coverage

To measure code coverage, first install the coverage tool:

```bash
pip install coverage
```

Then run tests with coverage analysis:

```bash
# Run tests and generate coverage report
coverage run -m unittest discover tests
coverage report -m

# Generate HTML coverage report
coverage html
# Open htmlcov/index.html in your browser

# Single command for coverage with report
coverage run -m unittest discover tests && coverage report -m
```

The project currently maintains approximately 90% code coverage.
