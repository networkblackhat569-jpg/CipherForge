#!/usr/bin/env python3
import random
import string

# ---------------------------------------------------
#  PassForge v1.0.0 – Advanced Password Generator
#  Author : netR4ptOr@
#  Contact: networkblackhat569@gmail.com
#  GitHub : https://github.com/yourhandle/passforge
#  ⚠ For Educational / Personal Use Only
# ---------------------------------------------------

def banner():
    print(r"""
                      ____                  _____                      
                     |  _ \ __ _ ___ ___   |  ___|__  _ __ __ _  ___  
                     | |_) / _` / __/ __|  | |_ / _ \| '__/ _` |/ _ \ 
                     |  __/ (_| \__ \__ \  |  _| (_) | | | (_| |  __/ 
                     |_|   \__,_|___/___/  |_|  \___/|_|  \__, |\___| 
                                                       |___/        

======================================================
  🔐 PassForge v1.0.0  –  Advanced Password Generator
  👤 Author : netR4ptOr@
  📧 Contact: networkblackhat569@gmail.com
  🐙 GitHub : https://github.com/yourhandle/passforge
  ⚠ For Educational / Personal Use Only
======================================================
""")


def generate_password(length=12, use_digits=True, use_symbols=True):
    """Generate a strong random password"""
    chars = string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += string.punctuation

    return ''.join(random.choice(chars) for _ in range(length))


def main():
    banner()

    try:
        length = int(input("🔢 Enter password length (default 12): ") or 12)
        use_digits = input("🔢 Include digits? (y/n, default y): ").lower() != "n"
        use_symbols = input("💠 Include symbols? (y/n, default y): ").lower() != "n"
        count = int(input("🔁 How many passwords to generate? (default 1): ") or 1)

        print("\n✅ Generated Password(s):\n")
        with open("passwords.txt", "a") as f:
            for i in range(count):
                pwd = generate_password(length, use_digits, use_symbols)
                print(f"[{i+1}] {pwd}")
                f.write(pwd + "\n")

        print("\n💾 Saved to: passwords.txt\n")

    except KeyboardInterrupt:
        print("\n❌ Interrupted by user. Exiting...")
    except Exception as e:
        print(f"\n⚠ Error: {e}")


if __name__ == "__main__":
    main()
