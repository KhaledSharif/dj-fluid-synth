"""Test instrument generators and synth functions."""

import unittest
import numpy as np
from main import (
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
    generate_supersaw,
    generate_future_bass,
    generate_reese_bass,
    generate_pluck_bass,
    generate_dubstep_bass,
    generate_white_noise_riser,
    generate_impact,
    generate_pitch_bend_bass
)


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


if __name__ == '__main__':
    unittest.main()