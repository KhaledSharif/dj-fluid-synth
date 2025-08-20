"""Test core functionality like note conversion, envelopes, filters, and sidechain."""

import unittest
import numpy as np
from main import (
    note_to_freq,
    apply_envelope,
    apply_sidechain,
    apply_lowpass,
    apply_highpass,
    apply_automation
)


class TestNoteConversion(unittest.TestCase):
    def test_note_to_freq_basic(self):
        # Test A4 = 440 Hz
        self.assertAlmostEqual(note_to_freq("A4"), 440.0, places=1)
        
    def test_note_to_freq_octaves(self):
        # Test octave relationships
        self.assertAlmostEqual(note_to_freq("A3"), 220.0, places=1)
        self.assertAlmostEqual(note_to_freq("A5"), 880.0, places=1)
        
    def test_note_to_freq_rest(self):
        # Test rest returns 0
        self.assertEqual(note_to_freq("rest"), 0)
        
    def test_note_to_freq_sharps(self):
        # Test sharp notes
        freq = note_to_freq("C#4")
        self.assertGreater(freq, note_to_freq("C4"))
        self.assertLess(freq, note_to_freq("D4"))
        
    def test_note_to_freq_all_notes(self):
        # Test all notes in an octave (chromatic scale)
        notes = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]
        freqs = [note_to_freq(note) for note in notes]
        # Check that frequencies are in ascending order
        for i in range(1, len(freqs)):
            self.assertGreater(freqs[i], freqs[i-1], f"{notes[i]} should be higher than {notes[i-1]}")
    
    def test_note_to_freq_flats(self):
        # Test flat notes
        self.assertAlmostEqual(note_to_freq("Bb4"), note_to_freq("A#4"), places=5)
        self.assertAlmostEqual(note_to_freq("Db4"), note_to_freq("C#4"), places=5)
        self.assertAlmostEqual(note_to_freq("Eb4"), note_to_freq("D#4"), places=5)
        self.assertAlmostEqual(note_to_freq("Gb4"), note_to_freq("F#4"), places=5)
        self.assertAlmostEqual(note_to_freq("Ab4"), note_to_freq("G#4"), places=5)


class TestEnvelope(unittest.TestCase):
    def setUp(self):
        self.fs = 44100
        self.duration = 1.0
        self.samples = int(self.fs * self.duration)
        self.wave = np.ones(self.samples)
        
    def test_envelope_basic(self):
        # Test that envelope is applied
        result = apply_envelope(self.wave, self.duration, self.fs)
        self.assertEqual(len(result), self.samples)
        # Check that envelope starts near 0 (attack)
        self.assertLess(result[0], 0.1)
        
    def test_envelope_parameters(self):
        # Test with different parameters
        result = apply_envelope(
            self.wave, self.duration, self.fs,
            attack=0.1, decay=0.2, sustain=0.5, release=0.3
        )
        self.assertEqual(len(result), self.samples)
        
    def test_envelope_short_duration(self):
        # Test with very short duration
        short_dur = 0.01
        short_samples = int(self.fs * short_dur)
        short_wave = np.ones(short_samples)
        result = apply_envelope(short_wave, short_dur, self.fs)
        self.assertEqual(len(result), short_samples)


class TestSidechain(unittest.TestCase):
    def setUp(self):
        self.fs = 44100
        self.tempo = 120
        self.duration = 4.0
        self.samples = int(self.fs * self.duration)
        self.audio = np.ones(self.samples)
        
    def test_sidechain_basic(self):
        kick_times = [0.0, 0.5, 1.0, 1.5]  # Every half second
        result = apply_sidechain(self.audio, kick_times, self.fs, self.tempo)
        self.assertEqual(len(result), self.samples)
        # Check that amplitude is reduced at kick times
        for kick_time in kick_times:
            sample_idx = int(kick_time * self.fs)
            if sample_idx < len(result):
                # Allow some tolerance due to smoothing
                self.assertLess(result[sample_idx + 100], 0.8)
                
    def test_sidechain_empty_kicks(self):
        result = apply_sidechain(self.audio, [], self.fs, self.tempo)
        # Should return audio mostly unchanged (except for smoothing)
        self.assertEqual(len(result), self.samples)
        
    def test_sidechain_strength(self):
        kick_times = [0.0, 1.0]
        result_strong = apply_sidechain(self.audio, kick_times, self.fs, self.tempo, strength=0.9)
        result_weak = apply_sidechain(self.audio, kick_times, self.fs, self.tempo, strength=0.3)
        # Stronger sidechain should duck more
        self.assertLess(float(np.min(result_strong)), float(np.min(result_weak)))


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.fs = 44100
        self.duration = 0.5
        self.samples = int(self.fs * self.duration)
        # Create test signal with multiple frequencies
        t = np.linspace(0, self.duration, self.samples)
        self.test_wave = np.sin(2 * np.pi * 100 * t) + np.sin(2 * np.pi * 1000 * t) + np.sin(2 * np.pi * 5000 * t)
        
    def test_apply_lowpass_scalar(self):
        filtered = apply_lowpass(self.test_wave, 500, self.fs)
        self.assertEqual(len(filtered), self.samples)
        # Should preserve low frequencies better than high
        fft_orig = np.fft.fft(self.test_wave)
        fft_filtered = np.fft.fft(filtered)
        # Check that high frequencies are attenuated
        high_freq_idx = int(5000 * self.samples / self.fs)
        low_freq_idx = int(100 * self.samples / self.fs)
        self.assertLess(np.abs(fft_filtered[high_freq_idx]), np.abs(fft_orig[high_freq_idx]) * 0.5)
        
    def test_apply_lowpass_array(self):
        # Test with array of cutoff values (time-varying filter)
        cutoff_array = np.linspace(200, 2000, 100)
        filtered = apply_lowpass(self.test_wave, cutoff_array, self.fs)
        self.assertEqual(len(filtered), self.samples)
        
    def test_apply_highpass(self):
        filtered = apply_highpass(self.test_wave, 2000, self.fs)
        self.assertEqual(len(filtered), self.samples)
        # Should preserve high frequencies better than low
        fft_orig = np.fft.fft(self.test_wave)
        fft_filtered = np.fft.fft(filtered)
        # Check that low frequencies are attenuated
        low_freq_idx = int(100 * self.samples / self.fs)
        self.assertLess(np.abs(fft_filtered[low_freq_idx]), np.abs(fft_orig[low_freq_idx]) * 0.5)


class TestAutomation(unittest.TestCase):
    def setUp(self):
        self.fs = 44100
        self.duration = 1.0
        self.samples = int(self.fs * self.duration)
        self.test_wave = np.ones(self.samples)
        
    def test_automation_fade_in(self):
        result = apply_automation(self.test_wave, "fade_in", self.duration, self.fs)
        self.assertEqual(len(result), self.samples)
        # Should start quiet and end loud
        self.assertLess(result[0], result[-1])
        self.assertAlmostEqual(result[0], 0, places=2)
        self.assertAlmostEqual(result[-1], 1, places=2)
        
    def test_automation_fade_out(self):
        result = apply_automation(self.test_wave, "fade_out", self.duration, self.fs)
        self.assertEqual(len(result), self.samples)
        # Should start loud and end quiet
        self.assertGreater(result[0], result[-1])
        self.assertAlmostEqual(result[0], 1, places=2)
        self.assertAlmostEqual(result[-1], 0, places=2)
        
    def test_automation_swell(self):
        result = apply_automation(self.test_wave, "swell", self.duration, self.fs)
        self.assertEqual(len(result), self.samples)
        # Should be loudest in the middle
        mid_point = self.samples // 2
        self.assertGreater(result[mid_point], result[0])
        self.assertGreater(result[mid_point], result[-1])
        
    def test_automation_pulse(self):
        result = apply_automation(self.test_wave, "pulse", self.duration, self.fs)
        self.assertEqual(len(result), self.samples)
        # Should oscillate
        self.assertLessEqual(np.max(result), 1.0)
        self.assertGreaterEqual(np.min(result), 0.0)


class TestEdgeCases(unittest.TestCase):
    def test_zero_duration(self):
        # Should handle zero duration gracefully
        from main import generate_kick
        wave = generate_kick(0, 44100)
        self.assertEqual(len(wave), 0)
        
    def test_very_low_frequency(self):
        # Should handle very low frequencies
        from main import generate_bass
        wave = generate_bass(20, 0.1, 44100)
        self.assertIsNotNone(wave)
        
    def test_very_high_frequency(self):
        # Should handle very high frequencies
        from main import generate_melody
        wave = generate_melody(8000, 0.1, 44100)
        self.assertIsNotNone(wave)


if __name__ == '__main__':
    unittest.main()