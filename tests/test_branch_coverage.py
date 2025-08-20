"""Tests specifically designed to achieve 100% branch coverage.

Branch coverage ensures all possible paths through conditionals are tested,
not just that every line is executed.
"""

import unittest
import numpy as np
import tempfile
import os
import yaml
from main import (
    apply_envelope,
    generate_kick,
    generate_snare,
    generate_bass,
    generate_pad,
    generate_melody,
    generate_supersaw,
    generate_future_bass,
    generate_pitch_bend_bass,
    apply_lowpass,
    apply_automation,
    generate_edm_from_yaml,
    note_to_freq
)


class TestBranchCoverage(unittest.TestCase):
    """Tests targeting specific branch conditions for 100% coverage."""
    
    def setUp(self):
        self.fs = 44100
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        # Clean up temp files
        for file in os.listdir(self.temp_dir):
            os.remove(os.path.join(self.temp_dir, file))
        os.rmdir(self.temp_dir)
    
    def test_envelope_zero_attack(self):
        """Test envelope with attack=0 to cover the false branch of 'if attack_samples > 0'"""
        wave = np.ones(1000)
        result = apply_envelope(wave, 0.1, self.fs, attack=0.0, decay=0.01, sustain=0.5, release=0.01)
        self.assertEqual(len(result), len(wave))
        # First sample should start at sustain level since no attack
        self.assertGreater(result[0], 0.4)
    
    def test_envelope_zero_decay(self):
        """Test envelope with decay=0 to cover the false branch of 'if decay_samples > 0'"""
        wave = np.ones(1000)
        result = apply_envelope(wave, 0.1, self.fs, attack=0.01, decay=0.0, sustain=0.5, release=0.01)
        self.assertEqual(len(result), len(wave))
    
    def test_envelope_zero_release(self):
        """Test envelope with release=0 to cover edge cases in release calculation"""
        wave = np.ones(1000)
        result = apply_envelope(wave, 0.1, self.fs, attack=0.01, decay=0.01, sustain=0.5, release=0.0)
        self.assertEqual(len(result), len(wave))
    
    def test_envelope_all_zero(self):
        """Test envelope with all parameters at 0"""
        wave = np.ones(1000)
        result = apply_envelope(wave, 0.1, self.fs, attack=0.0, decay=0.0, sustain=0.0, release=0.0)
        self.assertEqual(len(result), len(wave))
    
    def test_envelope_very_long_times(self):
        """Test envelope where attack+decay+release > duration"""
        wave = np.ones(1000)
        result = apply_envelope(wave, 0.02, self.fs, attack=0.5, decay=0.5, sustain=0.5, release=0.5)
        self.assertEqual(len(result), len(wave))
    
    def test_lowpass_with_resonance_exactly_1(self):
        """Test lowpass filter with resonance=1.0 (boundary condition)"""
        wave = np.sin(2 * np.pi * 440 * np.linspace(0, 1, self.fs))
        result = apply_lowpass(wave, 1000, self.fs, resonance=1.0)
        self.assertEqual(len(result), len(wave))
    
    def test_lowpass_with_resonance_less_than_1(self):
        """Test lowpass filter with resonance<1 to ensure no resonance branch"""
        wave = np.sin(2 * np.pi * 440 * np.linspace(0, 1, self.fs))
        result = apply_lowpass(wave, 1000, self.fs, resonance=0.5)
        self.assertEqual(len(result), len(wave))
    
    def test_lowpass_with_very_high_cutoff(self):
        """Test lowpass with cutoff > nyquist frequency"""
        wave = np.sin(2 * np.pi * 440 * np.linspace(0, 1, self.fs))
        result = apply_lowpass(wave, 25000, self.fs)  # Above nyquist
        self.assertEqual(len(result), len(wave))
    
    def test_lowpass_with_single_value_array(self):
        """Test lowpass with array cutoff of length 1"""
        wave = np.sin(2 * np.pi * 440 * np.linspace(0, 1, self.fs))
        result = apply_lowpass(wave, np.array([1000]), self.fs)
        self.assertEqual(len(result), len(wave))
    
    def test_automation_none_type(self):
        """Test automation with 'none' type or invalid type"""
        wave = np.ones(self.fs)
        result = apply_automation(wave, "none", 1.0, self.fs)
        np.testing.assert_array_equal(result, wave)  # Should return unchanged
    
    def test_note_to_freq_empty_string(self):
        """Test note_to_freq with empty string"""
        freq = note_to_freq("")
        self.assertEqual(freq, 0)
    
    def test_note_to_freq_no_octave(self):
        """Test note with no octave specified (should default to 4)"""
        freq = note_to_freq("A")
        self.assertAlmostEqual(freq, 440.0, places=1)
    
    def test_note_to_freq_single_char_no_flat(self):
        """Test single character note (not a flat)"""
        freq = note_to_freq("C")
        self.assertGreater(freq, 0)
    
    def test_generate_kick_with_punch_parameter(self):
        """Test kick with different punch values"""
        # Default punch
        wave1 = generate_kick(0.1, self.fs)
        # High punch
        wave2 = generate_kick(0.1, self.fs, punch=2.0)
        # Low punch
        wave3 = generate_kick(0.1, self.fs, punch=0.5)
        
        self.assertEqual(len(wave1), int(0.1 * self.fs))
        self.assertEqual(len(wave2), int(0.1 * self.fs))
        self.assertEqual(len(wave3), int(0.1 * self.fs))
    
    def test_generate_snare_tone_variations(self):
        """Test snare with different tone values"""
        wave_low = generate_snare(0.1, self.fs, tone=0.0)
        wave_mid = generate_snare(0.1, self.fs, tone=0.5)
        wave_high = generate_snare(0.1, self.fs, tone=1.0)
        
        self.assertEqual(len(wave_low), int(0.1 * self.fs))
        self.assertEqual(len(wave_mid), int(0.1 * self.fs))
        self.assertEqual(len(wave_high), int(0.1 * self.fs))
    
    def test_generate_supersaw_voice_variations(self):
        """Test supersaw with different voice counts"""
        wave1 = generate_supersaw(440, 0.1, self.fs, voices=1)
        wave3 = generate_supersaw(440, 0.1, self.fs, voices=3)
        wave7 = generate_supersaw(440, 0.1, self.fs, voices=7)
        
        self.assertEqual(len(wave1), int(0.1 * self.fs))
        self.assertEqual(len(wave3), int(0.1 * self.fs))
        self.assertEqual(len(wave7), int(0.1 * self.fs))
    
    def test_generate_supersaw_detune_variations(self):
        """Test supersaw with different detune amounts"""
        wave_none = generate_supersaw(440, 0.1, self.fs, detune=0.0)
        wave_small = generate_supersaw(440, 0.1, self.fs, detune=0.01)
        wave_large = generate_supersaw(440, 0.1, self.fs, detune=0.1)
        
        self.assertEqual(len(wave_none), int(0.1 * self.fs))
        self.assertEqual(len(wave_small), int(0.1 * self.fs))
        self.assertEqual(len(wave_large), int(0.1 * self.fs))
    
    def test_yaml_generation_with_all_sidechain_styles(self):
        """Test different sidechain styles to cover all branches"""
        for style in ['pump', 'duck', 'subtle', None]:
            yaml_data = {
                'tempo': 120,
                'sample_rate': 44100,
                'sidechain': True if style else False,
                'sidechain_style': style,
                'sidechain_strength': 0.7,
                'sections': [{
                    'name': 'test',
                    'bars': 1,
                    'tracks': [
                        {'type': 'kick', 'pattern': [1, 0, 0, 0]},
                        {'type': 'pad', 'notes': ['C4'], 'durations': [4]}
                    ]
                }]
            }
            
            yaml_path = os.path.join(self.temp_dir, f'sidechain_{style}.yml')
            wav_path = os.path.join(self.temp_dir, f'sidechain_{style}.wav')
            
            with open(yaml_path, 'w') as f:
                yaml.dump(yaml_data, f)
            
            generate_edm_from_yaml(yaml_path, wav_path)
            self.assertTrue(os.path.exists(wav_path))
    
    def test_yaml_generation_missing_optional_fields(self):
        """Test YAML generation with missing optional fields"""
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            # No sidechain fields
            'sections': [{
                'name': 'test',
                'bars': 1,
                'tracks': [
                    {'type': 'kick', 'pattern': [1]},  # No volume
                ]
            }]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'minimal.yml')
        wav_path = os.path.join(self.temp_dir, 'minimal.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
        
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
    
    def test_yaml_track_with_automation(self):
        """Test tracks with automation parameter"""
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [{
                'name': 'test',
                'bars': 2,
                'tracks': [
                    {
                        'type': 'pad',
                        'notes': ['C4'],
                        'durations': [8],
                        'automation': 'fade_in'
                    },
                    {
                        'type': 'melody',
                        'notes': ['E4'],
                        'durations': [8],
                        'automation': 'fade_out'
                    }
                ]
            }]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'automation.yml')
        wav_path = os.path.join(self.temp_dir, 'automation.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
        
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
    
    def test_yaml_track_with_start_bar(self):
        """Test tracks with start_bar parameter"""
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [{
                'name': 'test',
                'bars': 4,
                'tracks': [
                    {
                        'type': 'kick',
                        'pattern': [1, 0, 0, 0],
                        'start_bar': 2  # Start at bar 2
                    }
                ]
            }]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'start_bar.yml')
        wav_path = os.path.join(self.temp_dir, 'start_bar.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
        
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))
    
    def test_pitch_bend_bass_styles(self):
        """Test pitch bend bass with all bass styles"""
        for style in ['sub', 'reese', 'pluck', 'future']:
            wave = generate_pitch_bend_bass("C2", "E2", 0.1, self.fs, bass_type=style)
            self.assertEqual(len(wave), int(0.1 * self.fs))
    
    def test_generate_future_bass_frequency_zero(self):
        """Test future bass with zero frequency"""
        wave = generate_future_bass(0, 0.1, self.fs)
        self.assertEqual(len(wave), int(0.1 * self.fs))
        np.testing.assert_array_equal(wave, np.zeros(len(wave)))
    
    def test_yaml_with_all_track_types(self):
        """Test YAML generation with every track type to ensure all branches are covered"""
        track_configs = [
            {'type': 'kick', 'pattern': [1]},
            {'type': 'snare', 'pattern': [1]},
            {'type': 'hihat', 'pattern': [1]},
            {'type': 'clap', 'pattern': [1]},
            {'type': 'percussion', 'pattern': [1]},
            {'type': 'crash', 'pattern': [1]},
            {'type': 'bass', 'notes': ['C2'], 'durations': [1]},
            {'type': 'sub_bass', 'notes': ['C1'], 'durations': [1]},
            {'type': 'melody', 'notes': ['C4'], 'durations': [1]},
            {'type': 'pad', 'notes': ['C3'], 'durations': [1]},
            {'type': 'arp', 'notes': ['C4'], 'durations': [1]},
            {'type': 'pluck', 'notes': ['C4'], 'durations': [1]},
            {'type': 'sweep', 'pattern': [1]},
            {'type': 'riser', 'pattern': [1]},
            {'type': 'downlifter', 'pattern': [1]},
            {'type': 'impact', 'pattern': [1]},
            {'type': 'supersaw', 'notes': ['C4'], 'durations': [1]},
            {'type': 'future_bass', 'notes': ['C3'], 'durations': [1]},
            {'type': 'reese_bass', 'notes': ['C2'], 'durations': [1]},
            {'type': 'pluck_bass', 'notes': ['C2'], 'durations': [1]},
            {'type': 'dubstep_bass', 'notes': ['C1'], 'durations': [1], 'wobble_rate': 2},
            {'type': 'pitch_bend_bass', 'notes': ['C2'], 'bend_notes': ['E2'], 'durations': [1]},
        ]
        
        yaml_data = {
            'tempo': 120,
            'sample_rate': 44100,
            'sections': [{
                'name': 'test',
                'bars': 1,
                'tracks': track_configs
            }]
        }
        
        yaml_path = os.path.join(self.temp_dir, 'all_tracks.yml')
        wav_path = os.path.join(self.temp_dir, 'all_tracks.wav')
        
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_data, f)
        
        generate_edm_from_yaml(yaml_path, wav_path)
        self.assertTrue(os.path.exists(wav_path))


if __name__ == '__main__':
    unittest.main()