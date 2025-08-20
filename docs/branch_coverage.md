# Understanding Branch Coverage vs Line Coverage

## Key Differences

### Line Coverage

- **Measures**: Whether each line of code has been executed at least once
- **Simple metric**: Binary - either a line was executed or it wasn't
- **Can be misleading**: A line with a conditional might be "covered" without testing all paths

### Branch Coverage

- **Measures**: Whether each possible branch in control flow has been taken
- **More thorough**: Tests both TRUE and FALSE paths of conditionals
- **Better quality indicator**: Ensures all decision paths are tested

## Examples

### Example 1: Simple If Statement

```python
def check_value(x):
    if x > 0:           # Line 2
        return "positive"  # Line 3
    return "non-positive"  # Line 4
```

**Line Coverage:**

- Test with `x=1`: Lines 2,3 executed = 100% line coverage ✓
- BUT: Never tested the `x <= 0` case!

**Branch Coverage:**

- Test with `x=1`: TRUE branch taken (50% branch coverage)
- Need `x=0` or `x=-1`: FALSE branch taken
- Both tests needed for 100% branch coverage

### Example 2: Complex Conditions

```python
def apply_envelope(wave, duration, fs, attack=0.01):
    attack_samples = int(attack * fs)
    
    if attack_samples > 0:  # Branch point!
        # Apply attack curve
        envelope[:attack_samples] = calculate_curve()
```

**Hidden Branches:**

- `attack_samples > 0` - TRUE branch (normal case)
- `attack_samples <= 0` - FALSE branch (when attack=0)

Testing with default `attack=0.01` gives 100% line coverage but only 50% branch coverage!

### Example 3: Short-Circuit Evaluation

```python
if config.get('sidechain') and config.get('sidechain_strength') > 0:
    apply_sidechain()
```

**Four Branch Paths:**

1. `sidechain=False` (short-circuits, second condition not evaluated)
2. `sidechain=True, strength=0`
3. `sidechain=True, strength>0` (enters block)
4. `sidechain=None` (different from False in some contexts)

## Common Branch Coverage Gaps

### 1. Default Parameters

```python
def generate_kick(duration, fs, punch=1.0):
```

- Need tests with default `punch=1.0` AND custom values

### 2. Boundary Conditions

```python
if resonance > 1:
    add_resonance()
```

- Test with `resonance=0.5, 1.0, 1.5` (below, at, above boundary)

### 3. Error Paths

```python
if start_freq == 0 and end_freq == 0:
    return np.zeros(...)  # Error case rarely tested
```

### 4. Loop Iterations

```python
for voice in range(voices):
    generate_voice()
```

- Test with `voices=0` (no iterations)
- Test with `voices=1` (single iteration)
- Test with `voices>1` (multiple iterations)

## Achieving 100% Branch Coverage

### Strategy 1: Parameterized Tests

```python
def test_envelope_all_branches(self):
    test_cases = [
        (0.0, 0.01, 0.5, 0.01),  # zero attack
        (0.01, 0.0, 0.5, 0.01),  # zero decay
        (0.01, 0.01, 0.5, 0.0),  # zero release
        (0.0, 0.0, 0.0, 0.0),    # all zero
    ]
    for attack, decay, sustain, release in test_cases:
        result = apply_envelope(wave, duration, fs, attack, decay, sustain, release)
        self.assertIsNotNone(result)
```

### Strategy 2: Boundary Value Testing

```python
def test_lowpass_resonance_boundaries(self):
    for resonance in [0.5, 1.0, 1.5, 2.0]:
        result = apply_lowpass(wave, 1000, fs, resonance)
        # Different branches execute based on resonance > 1
```

### Strategy 3: Edge Case Testing

```python
def test_pitch_bend_edge_cases(self):
    test_cases = [
        ("C4", "E4"),    # Both notes valid
        ("rest", "E4"),  # Start is rest
        ("C4", "rest"),  # End is rest
        ("rest", "rest"), # Both rest
    ]
```

## Measuring Branch Coverage

### Using coverage.py

```bash
# Run with branch coverage
coverage run --branch -m unittest discover tests

# Generate detailed report
coverage report --show-missing

# Generate HTML report for visual branch analysis
coverage html
# Look for yellow highlighting showing partial branches
```

### Interpreting Results

```
Name         Stmts   Miss Branch BrPart  Cover
------------------------------------------------
main.py        493     29    164     25    91%
```

- **Stmts**: Total statements
- **Miss**: Uncovered statements
- **Branch**: Total branches
- **BrPart**: Partially covered branches
- **Cover**: Combined coverage percentage

### Finding Missing Branches

In the HTML report:

- **Green**: Fully covered
- **Red**: Not covered at all
- **Yellow**: Partially covered (missing branches)

## Benefits of High Branch Coverage

1. **Catches Logic Errors**: Ensures all decision paths work correctly
2. **Better Edge Case Testing**: Forces testing of boundary conditions
3. **Improved Reliability**: Reduces chance of production bugs
4. **Documentation**: Tests serve as examples of all possible behaviors
5. **Refactoring Confidence**: Changes won't break untested paths

## Trade-offs

### When 100% Branch Coverage May Not Be Practical

1. **Defensive Programming**

```python
# This should "never happen" but we handle it anyway
if impossible_condition:
    log_error()
    return safe_default
```

2. **Platform-Specific Code**

```python
if sys.platform == "win32":
    windows_specific()
else:
    unix_specific()
```

3. **Error Handlers for External Dependencies**

```python
try:
    external_api_call()
except NetworkError:
    # Hard to test without mocking
```

## Best Practices

1. **Aim for >90% branch coverage** for critical paths
2. **Focus on business logic** rather than boilerplate
3. **Use mocking** for external dependencies
4. **Document why** certain branches aren't covered
5. **Review branch reports** during code review
6. **Automate coverage checks** in CI/CD pipeline

## Conclusion

Branch coverage provides a more thorough measure of test quality than line coverage alone. While 100% branch coverage doesn't guarantee bug-free code, it significantly increases confidence that all code paths have been exercised and validated.
