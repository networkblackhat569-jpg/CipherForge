# CipherForge CLI v3.0
# by BlackIceSec | blackicesec@protonmail.com

import random, string, os, sys, time, math
from colorama import init, Fore, Style
import pyperclip

# Initialize colorama
init(autoreset=True)
session_passwords = []

# ---------------- Animation Utils ---------------- #
def typing_effect(text, delay=0.02):
    """Print text with hacker-style typing effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def loading_animation(task="Processing", duration=1.5):
    """Simple loading animation with dots"""
    print(Fore.CYAN + task, end="", flush=True)
    for _ in range(5):
        time.sleep(duration/5)
        print(Fore.CYAN + ".", end="", flush=True)
    print("\n")

# ---------------- Password Utils ---------------- #
def generate_password(length=12, strength='medium'):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()-_=+[]{}|;:,.<>?/"

    if strength == 'easy':
        chars = lower + digits
    elif strength == 'medium':
        chars = lower + upper + digits
    elif strength == 'strong':
        chars = lower + upper + digits + symbols
    elif strength == 'very strong':
        chars = lower + upper + digits + symbols*2
    else:
        chars = lower + upper + digits

    password = ''.join(random.choice(chars) for _ in range(length))
    session_passwords.append(password)
    return password

def check_strength(password):
    """Entropy-based password strength checker"""
    pool = 0
    if any(c.islower() for c in password):
        pool += 26
    if any(c.isupper() for c in password):
        pool += 26
    if any(c.isdigit() for c in password):
        pool += 10
    if any(c in "!@#$%^&*()-_=+[]{}|;:,.<>?/" for c in password):
        pool += 30

    entropy = math.log2(pool ** len(password)) if pool else 0

    if entropy < 40:
        return Fore.RED + "Weak 🔴"
    elif entropy < 60:
        return Fore.YELLOW + "Medium 🟡"
    elif entropy < 80:
        return Fore.GREEN + "Strong 🟢"
    else:
        return Fore.CYAN + "Very Strong 🔵"

def clear_session():
    global session_passwords
    session_passwords = []

# ---------------- CLI Layout ---------------- #
def banner():
    os.system('cls' if os.name=='nt' else 'clear')
    ascii_logo = r"""
   ____ ___ ____  _   _ _____ ____   ___  ____  _____ ____ 
  / ___|_ _|  _ \| | | | ____|  _ \ / _ \|  _ \| ____/ ___|
 | |    | || |_) | |_| |  _| | |_) | | | | |_) |  _| \___ \
 | |___ | ||  __/|  _  | |___|  _ <| |_| |  _ <| |___ ___) |
  \____|___|_|   |_| |_|_____|_| \_\\___/|_| \_\_____|____/ 
    """
    print(Fore.CYAN + Style.BRIGHT + ascii_logo)
    print(Fore.CYAN + Style.BRIGHT + "\n               CIPHERFORGE CLI v3.0")
    print(Fore.CYAN + Style.BRIGHT + "  by netR4ptOr@ | networkblackhat5692@gmail.com")
    print(Fore.CYAN + Style.BRIGHT + "=================================================\n")

def main_menu():
    print(Fore.YELLOW + "============== Main Menu ================")
    print(Fore.GREEN + "[1] Generate by Preset (easy/medium/strong/very strong)")
    print(Fore.GREEN + "[2] Custom Generation (full control)")
    print(Fore.GREEN + "[3] Bulk Quick Generate")
    print(Fore.GREEN + "[4] Copy Last Password to Clipboard")
    print(Fore.GREEN + "[5] Save Generated Passwords to File")
    print(Fore.GREEN + "[6] Clear Current Session")
    print(Fore.GREEN + "[7] About / Help")
    print(Fore.RED   + "[0] Exit")
    print(Fore.YELLOW + "========================================")

# ---------------- Menu Actions ---------------- #
def generate_preset():
    print("\nChoose Strength: easy / medium / strong / very strong")
    strength = input("Strength ➤ ").lower()
    length = input("Length ➤ ")
    if not length.isdigit(): length = "12"
    loading_animation("Generating password")
    pwd = generate_password(int(length), strength)
    typing_effect(Fore.MAGENTA + f"\nGenerated Password: {pwd}\n")
    print(Fore.CYAN + "Strength ➤ " + check_strength(pwd) + "\n")

def generate_custom():
    chars = input("Enter custom characters to use ➤ ")
    length = input("Length ➤ ")
    if not length.isdigit(): length = "12"
    loading_animation("Generating custom password")
    pwd = ''.join(random.choice(chars) for _ in range(int(length)))
    session_passwords.append(pwd)
    typing_effect(Fore.MAGENTA + f"\nGenerated Password: {pwd}\n")
    print(Fore.CYAN + "Strength ➤ " + check_strength(pwd) + "\n")

def bulk_generate():
    count = input("Number of passwords ➤ ")
    length = input("Length ➤ ")
    if not count.isdigit(): count = "5"
    if not length.isdigit(): length = "12"
    strength = input("Strength (easy/medium/strong/very strong) ➤ ").lower()
    print()
    for i in range(int(count)):
        loading_animation(f"Generating password {i+1}")
        pwd = generate_password(int(length), strength)
        typing_effect(Fore.MAGENTA + pwd, delay=0.01)
        print(Fore.CYAN + "Strength ➤ " + check_strength(pwd) + "\n")

def copy_last():
    if session_passwords:
        pyperclip.copy(session_passwords[-1])
        typing_effect(Fore.CYAN + "✅ Last password copied to clipboard!\n", delay=0.01)
    else:
        typing_effect(Fore.RED + "❌ No password in session yet.\n", delay=0.01)

def save_file():
    if not session_passwords:
        typing_effect(Fore.RED + "❌ No passwords to save.\n")
        return
    filename = input("Enter filename to save ➤ ")
    with open(filename, 'w') as f:
        f.write('\n'.join(session_passwords))
    typing_effect(Fore.CYAN + f"✅ Saved {len(session_passwords)} passwords to {filename}\n")

def about_help():
    typing_effect(Fore.CYAN + """
CipherForge CLI v3.0
by netR4ptOr@
Advanced Password & Security Tool

Features:
- Preset / Custom / Bulk password generation
- Clipboard copy
- Session management
- Save passwords to file
- Password strength checker
- ASCII logo & hacker-style animations
""", delay=0.01)

# ---------------- Main Loop ---------------- #
while True:
    banner()
    main_menu()
    choice = input(Fore.GREEN + "Select option ➤ ")

    if choice == '1':
        generate_preset()
    elif choice == '2':
        generate_custom()
    elif choice == '3':
        bulk_generate()
    elif choice == '4':
        copy_last()
    elif choice == '5':
        save_file()
    elif choice == '6':
        clear_session()
        typing_effect(Fore.CYAN + "✅ Session cleared!\n")
    elif choice == '7':
        about_help()
    elif choice == '0':
        typing_effect(Fore.RED + "🔒 Exiting CipherForge CLI...", delay=0.05)
        break
    else:
        typing_effect(Fore.RED + "❌ Invalid choice! Try again.\n")

    input(Fore.YELLOW + "Press Enter to return to Main Menu...")

