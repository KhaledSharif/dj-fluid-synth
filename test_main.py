import unittest
import numpy as np
import tempfile
import os
import yaml
from scipy.io import wavfile
from main import (
    note_to_freq,
    apply_envelope,
    generate_kick,
    generate_hihat,
    generate_snare,
    generate_clap,
    generate_bass,
    generate_sub_bass,
    generate_melody,
    generate_pad,
    generate_sweep,
    generate_pluck,
    generate_arp,
    generate_percussion,
    apply_sidechain,
    generate_edm_from_yaml,
    apply_lowpass,
    apply_highpass,
    generate_supersaw,
    generate_future_bass,
    generate_reese_bass,
    generate_pluck_bass,
    generate_dubstep_bass,
    generate_white_noise_riser,
    generate_impact,
    generate_pitch_bend_bass,
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


class TestInstrumentGenerators(unittest.TestCase):
    def setUp(self):
        self.fs = 44100
        self.duration = 0.5
        
    def test_generate_kick(self):
        wave = generate_kick(self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        # Kick should have energy
        self.assertGreater(np.sum(np.abs(wave)), 0)
        
    def test_generate_hihat(self):
        wave = generate_hihat(self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_snare(self):
        wave = generate_snare(self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_clap(self):
        wave = generate_clap(self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_percussion(self):
        wave = generate_percussion(self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_bass(self):
        freq = 110  # A2
        wave = generate_bass(freq, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_bass_rest(self):
        wave = generate_bass(0, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        np.testing.assert_array_equal(wave, np.zeros(len(wave)))
        
    def test_generate_sub_bass(self):
        freq = 55  # A1
        wave = generate_sub_bass(freq, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_melody(self):
        freq = 440  # A4
        wave = generate_melody(freq, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_pad(self):
        freq = 261.63  # C4
        wave = generate_pad(freq, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_pluck(self):
        freq = 440  # A4
        wave = generate_pluck(freq, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_arp(self):
        freq = 261.63  # C4
        wave = generate_arp(freq, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_sweep(self):
        wave = generate_sweep(self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_sweep_reverse(self):
        wave = generate_sweep(self.duration, self.fs, reverse=True)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)


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
        self.assertLess(np.min(result_strong), np.min(result_weak))


class TestYAMLGeneration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        
    def test_generate_simple_track(self):
        # Create a simple YAML file
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'kick',
                            'pattern': [1, 0, 1, 0]
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'test.yml')
        wav_path = os.path.join(self.temp_dir, 'test.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        # Generate the track
        generate_edm_from_yaml(yaml_path, wav_path)
        
        # Check that WAV file was created
        self.assertTrue(os.path.exists(wav_path))
        
        # Load and check the WAV file
        fs, audio = wavfile.read(wav_path)
        self.assertEqual(fs, 44100)
        self.assertGreater(len(audio), 0)
        
    def test_generate_with_melody(self):
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 2,
                    'tracks': [
                        {
                            'type': 'melody',
                            'notes': ['C4', 'D4', 'E4', 'G4'],
                            'durations': [1, 1, 1, 1]
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'melody.yml')
        wav_path = os.path.join(self.temp_dir, 'melody.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_multiple_tracks(self):
        yaml_data = {
            'tempo': 128,
            'sample_rate': 44100,
            'sidechain': False,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'kick',
                            'pattern': [1, 0, 0, 0],
                            'volume': 0.8
                        },
                        {
                            'type': 'bass',
                            'notes': ['C2', 'E2', 'G2', 'C3'],
                            'durations': [1, 1, 1, 1],
                            'volume': 0.6
                        },
                        {
                            'type': 'pad',
                            'notes': ['C4', 'G4'],
                            'durations': [2, 2],
                            'volume': 0.4
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'multi.yml')
        wav_path = os.path.join(self.temp_dir, 'multi.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_sidechain(self):
        yaml_data = {
            'tempo': 128,
            'sample_rate': 44100,
            'sidechain': True,
            'sidechain_strength': 0.6,
            'sections': [
                {
                    'name': 'test',
                    'bars': 2,
                    'tracks': [
                        {
                            'type': 'kick',
                            'pattern': [1, 0, 0, 0]
                        },
                        {
                            'type': 'pad',
                            'notes': ['C4'],
                            'durations': [8]
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'sidechain.yml')
        wav_path = os.path.join(self.temp_dir, 'sidechain.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_velocity(self):
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'snare',
                            'pattern': [0.3, 0.5, 0.7, 1.0],  # Velocity pattern
                            'volume': 0.8
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'velocity.yml')
        wav_path = os.path.join(self.temp_dir, 'velocity.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))


class TestEdgeCases(unittest.TestCase):
    def test_zero_duration(self):
        # Should handle zero duration gracefully
        wave = generate_kick(0, 44100)
        self.assertEqual(len(wave), 0)
        
    def test_very_low_frequency(self):
        # Should handle very low frequencies
        wave = generate_bass(20, 0.1, 44100)
        self.assertIsNotNone(wave)
        
    def test_very_high_frequency(self):
        # Should handle very high frequencies
        wave = generate_melody(8000, 0.1, 44100)
        self.assertIsNotNone(wave)


class TestNewSynths(unittest.TestCase):
    def setUp(self):
        self.fs = 44100
        self.duration = 0.5
        self.freq = 440  # A4
        
    def test_generate_supersaw(self):
        wave = generate_supersaw(self.freq, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_supersaw_rest(self):
        wave = generate_supersaw(0, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        np.testing.assert_array_equal(wave, np.zeros(len(wave)))
        
    def test_generate_future_bass(self):
        wave = generate_future_bass(self.freq, self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_reese_bass(self):
        wave = generate_reese_bass(110, self.duration, self.fs)  # A2
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_pluck_bass(self):
        wave = generate_pluck_bass(110, self.duration, self.fs)  # A2
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_dubstep_bass(self):
        wave = generate_dubstep_bass(55, self.duration, self.fs, wobble_rate=4)  # A1
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_white_noise_riser(self):
        wave = generate_white_noise_riser(self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_impact(self):
        wave = generate_impact(self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_pitch_bend_bass(self):
        wave = generate_pitch_bend_bass("A2", "E3", self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        self.assertLessEqual(np.max(np.abs(wave)), 1.0)
        
    def test_generate_pitch_bend_bass_rest(self):
        wave = generate_pitch_bend_bass("rest", "rest", self.duration, self.fs)
        self.assertEqual(len(wave), int(self.fs * self.duration))
        np.testing.assert_array_equal(wave, np.zeros(len(wave)))


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


class TestEnhancedFeatures(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
        
    def test_generate_with_supersaw(self):
        yaml_data = {
            'tempo': 128,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'supersaw',
                            'notes': ['C4', 'E4', 'G4'],
                            'durations': [1, 1, 2],
                            'detune': 0.03,
                            'voices': 7,
                            'volume': 0.5
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'supersaw.yml')
        wav_path = os.path.join(self.temp_dir, 'supersaw.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_flat_notes(self):
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {
                            'type': 'melody',
                            'notes': ['Bb3', 'Eb4', 'Ab4', 'Db5'],
                            'durations': [1, 1, 1, 1]
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'flats.yml')
        wav_path = os.path.join(self.temp_dir, 'flats.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
        
    def test_generate_with_pitch_bend(self):
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [
                {
                    'name': 'test',
                    'bars': 2,
                    'tracks': [
                        {
                            'type': 'pitch_bend_bass',
                            'notes': ['C2', 'F2', 'G2', 'C3'],
                            'bend_notes': ['E2', 'G2', 'A2', 'C3'],
                            'durations': [1, 1, 1, 1],
                            'bass_style': 'pluck',
                            'volume': 0.7
                        }
                    ]
                }
            ]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'pitch_bend.yml')
        wav_path = os.path.join(self.temp_dir, 'pitch_bend.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
            
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))


if __name__ == '__main__':
    unittest.main()