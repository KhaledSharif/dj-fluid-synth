# Claude Assistant Guidelines for DJ Fluid Synth

## Project Overview

DJ Fluid Synth is a Python-based EDM music generator that creates professional electronic dance music from YAML configuration files. The system uses mathematical synthesis, DSP techniques, and modern production methods to generate festival-ready tracks.

## Core Components

### main.py

- Main synthesizer engine
- Converts YAML to WAV audio files
- Contains 20+ instrument generators
- Implements sidechain compression, filter automation, and effects

### YAML Files

- Define song structure, tempo, instruments, melodies
- Section-based composition (intro, buildup, drop, breakdown)
- Support for complex arrangements and automation

## Key Technical Concepts

### Synthesis Methods

1. **Subtractive Synthesis**: Start with harmonically rich waveforms (saw, square) and filter
2. **Additive Synthesis**: Combine multiple sine waves for pads and complex tones
3. **Karplus-Strong**: Physical modeling for plucked string sounds
4. **FM Synthesis**: Frequency modulation for metallic and bell-like tones

### DSP Techniques

- **ADSR Envelopes**: Attack, Decay, Sustain, Release for shaping amplitude
- **Low-pass/High-pass Filters**: Butterworth filters for frequency shaping
- **Sidechain Compression**: Duck audio in response to kick drum hits
- **LFO Modulation**: Low-frequency oscillators for wobbles and movement

### Signal Processing

- Sample rate: 44100 Hz (CD quality)
- 16-bit integer output with soft clipping
- Numpy arrays for efficient computation
- Real-time phase accumulation for pitch bending

## Common Tasks and Solutions

### Adding New Instruments

When asked to add a new instrument type:

1. Create a generator function in main.py following the pattern:

```python
def generate_[instrument_name](freq, duration, fs):
    if freq == 0:
        return np.zeros(int(fs * duration))
    t = np.linspace(0, duration, int(fs * duration))
    # Generate waveform
    wave = [synthesis_algorithm]
    # Apply envelope
    wave = apply_envelope(wave, duration, fs, ...)
    return wave * volume
```

2. Add to the track processing logic in `generate_edm_from_yaml()`
3. Document in README.md with parameters and usage

### Improving Sound Quality

Common improvements requested:

- **Add warmth**: Apply low-pass filter with slight resonance
- **Add punch**: Increase attack transients, add click layer to kicks
- **Add width**: Use multiple detuned voices (supersaw technique)
- **Add movement**: Apply LFO to filter cutoff or amplitude
- **Reduce harshness**: Soft saturation with np.tanh(), reduce high frequencies

### Creating New Genres

Genre characteristics to implement:

- **House**: 4/4 kick, offbeat hihats, pluck bass, 124-128 BPM
- **Dubstep**: Half-time drums, wobble bass (LFO rate 1-4 Hz), 140 BPM
- **Trance**: Rolling bass, long breakdowns, supersaw leads, 130-140 BPM
- **Future Bass**: Pitch bends, chord stabs, heavy sidechain, 140-160 BPM
- **Drum & Bass**: Fast breaks, Reese bass, 170-180 BPM

### Debugging Audio Issues

Common problems and solutions:

- **Clipping/Distortion**: Check amplitude scaling, ensure normalization
- **Clicks/Pops**: Verify envelope attack times, check array boundaries
- **Phase Issues**: Ensure proper phase accumulation in pitch bends
- **Silent Output**: Check note_to_freq() conversion, verify frequency > 0
- **Timing Issues**: Verify beat_duration calculations, check sample indices

## YAML Configuration Best Practices

### Essential Structure

```yaml
tempo: 128
sample_rate: 44100
sidechain: true
sidechain_style: pump
sidechain_strength: 0.7

sections:
  - name: [section_name]
    bars: [number]
    tracks: [array_of_tracks]
```

### Track Patterns

- Drums use `pattern` arrays: [1, 0, 0.8, 0] (velocity 0-1)
- Melodic use `notes` and `durations` arrays
- Durations are in beats (quarter notes)
- Use "rest" for silence in note arrays

### Layering Guidelines

- Never exceed 3-4 simultaneous bass frequencies
- Layer drums at different frequency ranges
- Use volume automation for dynamic interest
- Apply sidechain to non-drum elements

## Performance Optimization

### Efficient Processing

- Pre-calculate constant values outside loops
- Use numpy vectorized operations
- Avoid sample-by-sample processing where possible
- Cache frequently used waveforms

### Memory Management

- Process sections sequentially
- Clear large arrays when done
- Use dtype=np.float32 for audio arrays
- Normalize at the end, not during processing

## Testing and Validation

### Before Delivery

1. Generate test file: `python main.py test.yml test.wav`
2. Verify file playback without errors
3. Check for clipping (max amplitude < 1.0 before int16 conversion)
4. Ensure all sections have correct duration
5. Verify sidechain effect is audible

### Quality Checks

- Bass frequencies present (50-200 Hz)
- No DC offset in output
- Smooth transitions between sections
- Proper stereo image (currently mono, future enhancement)

## Common User Requests

### "Make it sound more professional"

- Add sidechain compression
- Layer multiple bass types
- Use supersaw for leads
- Add white noise risers before drops
- Include impact sounds on drops
- Apply soft saturation for loudness

### "Make it more energetic"

- Increase tempo slightly
- Add more high-frequency content
- Use shorter note durations
- Increase sidechain strength
- Add percussion layers
- Use automation curves

### "Fix timing issues"

- Check `durations` arrays sum correctly
- Verify `bars` count matches content
- Ensure pattern lengths are powers of 2
- Check `start_bar` parameters

## Code Style Guidelines

- Use descriptive function names (generate_[instrument])
- Keep generator functions under 50 lines
- Document non-obvious DSP algorithms
- Use numpy operations over Python loops
- Maintain consistent parameter ordering (freq, duration, fs)

## Future Enhancements to Consider

When users ask about features not yet implemented:

- Stereo processing (currently mono)
- MIDI import/export
- Real-time parameter modulation
- Reverb and delay effects
- Multiband compression
- Spectrum analysis tools
- GUI for visual editing

## Error Handling

Common errors and responses:

- "Invalid note name": Check note format (C4, A#3, Bb2)
- "Division by zero": Verify frequency > 0 before synthesis
- "Index out of bounds": Check pattern/note array cycling
- "File not found": Ensure YAML path is correct
- "Invalid YAML": Verify proper indentation and syntax

## Resource Management

- Maximum recommended song length: 5 minutes
- Maximum concurrent tracks: 20-30
- CPU usage scales with voice count in supersaw
- Memory usage approximately: samples * 4 bytes

## Testing Guidelines

### Running Unit Tests

The test suite is organized into three modules in the `tests/` directory:

1. **test_core.py**: Core functionality tests
   - Note conversion (including flats and sharps)
   - ADSR envelope application
   - Filter functions (lowpass/highpass)
   - Sidechain compression
   - Automation curves

2. **test_instruments.py**: Instrument generator tests
   - All basic instruments (kick, snare, hihat, etc.)
   - Melodic instruments (melody, pad, arp, pluck)
   - Advanced synths (supersaw, future bass, reese bass, etc.)
   - Special effects (sweep, riser, impact)

3. **test_yaml_generation.py**: YAML processing tests
   - Simple track generation
   - Multi-track compositions
   - Sidechain integration
   - Velocity patterns
   - Enhanced features (pitch bends, flat notes)

### Running Tests

```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test module
python -m unittest tests.test_core -v

# Run specific test class
python -m unittest tests.test_instruments.TestNewSynths -v

# Run specific test method
python -m unittest tests.test_core.TestNoteConversion.test_note_to_freq_flats
```

### Code Coverage

Always check code coverage after making changes:

```bash
# Install coverage tool (if not installed)
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests
coverage report -m

# Generate HTML report for detailed view
coverage html
# View htmlcov/index.html in browser

# Quick coverage check
coverage run -m unittest discover tests && coverage report -m
```

Target: Maintain >85% code coverage. Current: ~90%

### Before Committing

1. Run all tests: `python -m unittest discover tests`
2. Check coverage: `coverage run -m unittest discover tests && coverage report -m`
3. Run pyright: `pyright main.py`
4. Verify no broken imports or syntax errors

### Common Test Patterns

When adding new features:

1. **New Instrument**: Add test in `test_instruments.py`
   - Test correct length
   - Test amplitude bounds (≤1.0)
   - Test rest/zero frequency handling
   - Test with edge frequencies

2. **New YAML Feature**: Add test in `test_yaml_generation.py`
   - Create minimal YAML config
   - Generate WAV file
   - Verify file exists and has correct properties

3. **New DSP Function**: Add test in `test_core.py`
   - Test with known inputs/outputs
   - Test edge cases (zero, negative, very large values)
   - Test array vs scalar inputs if applicable

Remember: The goal is creating music that sounds professional and emotionally engaging while maintaining code clarity and performance.
