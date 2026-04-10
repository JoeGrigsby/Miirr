#!/usr/bin/env python3
"""Starfleet Command — a Star Trek themed decision program."""

def red_alert():
    print("\n*** RED ALERT ***")
    print("Shields at 30%. Hull breach on deck 7.")
    action = input("Your order, Captain? (fire / retreat / hail): ").strip().lower()

    if action == "fire":
        print("Firing photon torpedoes... Direct hit! Enemy vessel destroyed.")
        print("Well done, Captain. The Federation is safe.")
    elif action == "retreat":
        print("Retreating to Federation space at warp 9.")
        print("Discretion is the better part of valor, Captain.")
    elif action == "hail":
        print("Opening hailing frequencies...")
        print("The Klingons accept a ceasefire. Peace has been preserved.")
    else:
        print("Unclear order, Captain. The crew stands confused. We are destroyed.")

def anomaly():
    print("\nSensors detect an anomaly — a spatial rift is forming off the port bow.")
    action = input("What do we do? (scan / enter / ignore): ").strip().lower()

    if action == "scan":
        print("Scanning... It appears to be a stable wormhole to the Gamma Quadrant.")
        print("Starfleet will want to know about this. Logging coordinates.")
    elif action == "enter":
        print("Entering the rift... Temporal displacement detected!")
        print("You've traveled back to 1986 San Francisco. Find some whales.")
    elif action == "ignore":
        print("The rift expands and swallows the ship. Should've scanned it first.")
    else:
        print("Indecision is fatal, Captain. The rift collapses on the ship.")

def first_contact():
    print("\nAn unknown vessel is hailing us. They claim to be peaceful explorers.")
    action = input("How do you respond? (greet / scan / raise shields): ").strip().lower()

    if action == "greet":
        print("You respond warmly. A new civilization joins the Federation.")
        print("Today is a great day for diplomacy, Captain.")
    elif action == "scan":
        print("Scanning their ship reveals cloaked weapons. You raise shields just in time.")
        print("Good instincts, Captain. They retreat.")
    elif action == "raise shields":
        print("They interpret this as aggression and open fire.")
        print("A diplomatic incident. Starfleet Command is not pleased.")
    else:
        print("Silence. They interpret it as a challenge and attack.")

SITUATIONS = {
    "1": ("Red Alert — Klingon warbird decloaking!", red_alert),
    "2": ("Spatial anomaly detected!", anomaly),
    "3": ("First contact with unknown species", first_contact),
}

def main():
    print("=" * 50)
    print("  STARFLEET COMMAND — Captain's Bridge")
    print("=" * 50)
    print("Stardate 47634.4. You are Captain of the USS Miirr.")
    print("\nAn incoming report from the bridge:\n")
    for key, (desc, _) in SITUATIONS.items():
        print(f"  [{key}] {desc}")

    choice = input("\nWhat situation do you face, Captain? (1/2/3): ").strip()

    if choice in SITUATIONS:
        SITUATIONS[choice][1]()
    else:
        print("Invalid choice. Mr. Worf looks at you with disappointment.")

    print("\nEnd of simulation. Live long and prosper.\n")

if __name__ == "__main__":
    main()
