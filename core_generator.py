import hashlib
import itertools

def generate_vse_stream(seed_numbers: list[int], stream_length: int = 100, start_offset: int = 39543) -> list[str]:
    """
    Manufacturer core library logic with a custom offset rule system.
    Skips directly to a specific position in the infinite deterministic stream 
    (e.g., 39543) before starting the data layering process.
    """
    if len(seed_numbers) != 3:
        raise ValueError("VSE Core Engine requires exactly 3 starting numbers.")

    # 1. Lépés: A 6 alapvariáció kigenerálása
    string_seeds = [str(num) for num in seed_numbers]
    base_blocks = ["".join(p) for p in itertools.permutations(string_seeds)]
    total_blocks = len(base_blocks)
    
    pattern_stream = []
    
    # 2. Lépés: Nem ismétlődő kódok generálása az eltolástól indítva
    # Nem a 0-tól indulunk, hanem a megadott sorszámtól (pl. 39543-tól)
    for step in range(start_offset, start_offset + stream_length):
        index_a = step % total_blocks
        current_block = base_blocks[index_a]
        
        # Az egyedi kulcsot most már a megnövelt, eltolt sorszám adja
        unique_step_key = f"{current_block}-{step}"
        
        # Matematikai hash láncolat
        hash_digest = hashlib.md5(unique_step_key.encode('utf-8')).hexdigest()
        numeric_conversion = str(int(hash_digest, 16))
        
        # Fix 8 karakteres, nullákkal dúsított kód kivágása
        eight_digit_code = numeric_conversion.zfill(8)[:8]
        
        pattern_stream.append(eight_digit_code)
        
    return pattern_stream