#!/usr/bin/env python3
"""
MIIRR — Star Trek: Ascendancy (CLI Edition)
Turn-based 4X strategy: explore, colonize, research, and conquer the galaxy.
"""

import random
import sys
import os

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

CIVS = {
    "federation": {
        "name": "United Federation of Planets", "short": "Federation",
        "prod": 2, "res": 3, "inf": 3, "com": 2, "actions": 3,
        "home": "sol",
        "techs": ["warp_drive", "deflector_shields", "diplomacy_corps", "advanced_sensors", "replicators"],
        "sym": "✦",
    },
    "klingon": {
        "name": "Klingon Empire", "short": "Klingons",
        "prod": 3, "res": 2, "inf": 1, "com": 4, "actions": 3,
        "home": "qonos",
        "techs": ["warp_drive", "disruptors", "battle_tactics", "cloaking_device", "warriors_code"],
        "sym": "⚔",
    },
    "romulan": {
        "name": "Romulan Star Empire", "short": "Romulans",
        "prod": 2, "res": 2, "inf": 4, "com": 3, "actions": 3,
        "home": "romulus",
        "techs": ["warp_drive", "cloaking_device", "tal_shiar", "singularity_core", "deception_protocol"],
        "sym": "◈",
    },
}

TECH = {
    "warp_drive":          {"name": "Warp Drive",           "cost": 0,  "eff": "+1 move range (base)"},
    "deflector_shields":   {"name": "Deflector Shields",    "cost": 4,  "eff": "+1 defense die in combat"},
    "diplomacy_corps":     {"name": "Diplomacy Corps",      "cost": 5,  "eff": "+1 Influence per turn"},
    "advanced_sensors":    {"name": "Advanced Sensors",     "cost": 4,  "eff": "Reveal adjacent systems on explore"},
    "replicators":         {"name": "Replicators",          "cost": 6,  "eff": "+1 Production per turn"},
    "disruptors":          {"name": "Disruptor Banks",      "cost": 4,  "eff": "+2 attack in combat"},
    "battle_tactics":      {"name": "Battle Tactics",       "cost": 5,  "eff": "+1 action after combat win"},
    "cloaking_device":     {"name": "Cloaking Device",      "cost": 6,  "eff": "AI cannot detect your ships"},
    "warriors_code":       {"name": "Warrior's Code",       "cost": 4,  "eff": "+2 Ascendancy per combat win"},
    "tal_shiar":           {"name": "Tal Shiar Intel",      "cost": 5,  "eff": "See all AI resource totals"},
    "singularity_core":    {"name": "Singularity Core",     "cost": 6,  "eff": "+2 Production per turn"},
    "deception_protocol":  {"name": "Deception Protocol",  "cost": 4,  "eff": "+2 Influence attack"},
}

SYSTEMS = {
    "sol":       {"name": "Sol",          "p": 3, "r": 3, "i": 3, "type": "home"},
    "qonos":     {"name": "Qo'noS",       "p": 3, "r": 2, "i": 2, "type": "home"},
    "romulus":   {"name": "Romulus",      "p": 2, "r": 2, "i": 4, "type": "home"},
    "vulcan":    {"name": "Vulcan",       "p": 1, "r": 4, "i": 2, "type": "scientific"},
    "andor":     {"name": "Andor",        "p": 4, "r": 1, "i": 1, "type": "industrial"},
    "betazed":   {"name": "Betazed",      "p": 2, "r": 2, "i": 3, "type": "strategic"},
    "cardassia": {"name": "Cardassia",    "p": 3, "r": 1, "i": 2, "type": "industrial"},
    "bajor":     {"name": "Bajor",        "p": 2, "r": 2, "i": 3, "type": "strategic"},
    "ferengi":   {"name": "Ferengi",      "p": 2, "r": 2, "i": 2, "type": "commercial"},
    "talos":     {"name": "Talos IV",     "p": 1, "r": 3, "i": 4, "type": "mysterious"},
    "rura":      {"name": "Rura Penthe",  "p": 4, "r": 1, "i": 1, "type": "industrial"},
    "neutral":   {"name": "Neutral Zone", "p": 2, "r": 2, "i": 2, "type": "strategic"},
    "ds9":       {"name": "DS9 Sector",   "p": 2, "r": 2, "i": 3, "type": "strategic"},
    "genesis":   {"name": "Genesis",      "p": 1, "r": 5, "i": 1, "type": "scientific"},
    "veridian":  {"name": "Veridian III", "p": 1, "r": 3, "i": 3, "type": "mysterious"},
}

LANES = [
    ("sol","vulcan"),("sol","andor"),("sol","betazed"),("sol","ferengi"),
    ("vulcan","ferengi"),("vulcan","rura"),
    ("andor","talos"),("andor","genesis"),
    ("betazed","cardassia"),("betazed","ferengi"),("betazed","bajor"),
    ("ferengi","neutral"),("neutral","bajor"),("neutral","qonos"),("neutral","rura"),
    ("bajor","cardassia"),("bajor","ds9"),
    ("cardassia","ds9"),("cardassia","genesis"),
    ("qonos","rura"),("qonos","romulus"),
    ("romulus","ds9"),("romulus","veridian"),
    ("ds9","veridian"),("talos","genesis"),
]

AI_PAIR = {
    "federation": ["klingon","romulan"],
    "klingon":    ["federation","romulan"],
    "romulan":    ["federation","klingon"],
}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def clear(): os.system("cls" if os.name == "nt" else "clear")

def adjacent(sid):
    return [b for a,b in LANES if a==sid] + [a for a,b in LANES if b==sid]

def roll6(): return random.randint(1, 6)

def hr(char="─", n=56): return char * n

def cname(k): return CIVS[k]["short"] if k else "—"

# ─────────────────────────────────────────────
# GAME STATE
# ─────────────────────────────────────────────

def new_game(civ_key):
    civ = CIVS[civ_key]
    g = {
        "civ": civ_key,
        "turn": 1,
        "acts": civ["actions"],
        "res": {"p": 8, "r": 6, "i": 6, "a": 0},
        "techs": {"warp_drive"},
        "sys": {k: {"owner": None, "explored": False, "ships": []} for k in SYSTEMS},
        "ships": [],
        "sid": 1,
    }
    # Home systems
    g["sys"][civ["home"]]["owner"]    = civ_key
    g["sys"][civ["home"]]["explored"] = True
    for ai in AI_PAIR[civ_key]:
        g["sys"][CIVS[ai]["home"]]["owner"]    = ai
        g["sys"][CIVS[ai]["home"]]["explored"] = True

    # Starting ships
    add_ship(g, civ_key, "command", civ["home"])
    add_ship(g, civ_key, "scout",   civ["home"])
    for ai in AI_PAIR[civ_key]:
        add_ship(g, ai, "command", CIVS[ai]["home"])
    return g

def add_ship(g, owner, ship_type, sys_id):
    s = {"id": g["sid"], "owner": owner, "type": ship_type, "loc": sys_id}
    g["sid"] += 1
    g["ships"].append(s)
    g["sys"][sys_id]["ships"].append(s["id"])
    return s

def my_ships(g):    return [s for s in g["ships"] if s["owner"] == g["civ"]]
def ships_at(g, sid): return [s for s in g["ships"] if s["loc"] == sid]
def my_ship_at(g, sid): return next((s for s in g["ships"] if s["loc"]==sid and s["owner"]==g["civ"]), None)

# ─────────────────────────────────────────────
# DISPLAY
# ─────────────────────────────────────────────

def show_status(g):
    clear()
    civ = CIVS[g["civ"]]
    r = g["res"]
    print(hr("═"))
    print(f"  {civ['sym']} MIIRR — Star Trek: Ascendancy  |  Turn {g['turn']}  |  {civ['name']}")
    print(hr("═"))
    print(f"  ⚙ Production: {r['p']}   🔬 Research: {r['r']}   ◈ Influence: {r['i']}   "
          f"✦ Ascendancy: {r['a']}/20   Actions: {g['acts']}")
    print(hr())

def show_map(g):
    print("  GALACTIC MAP")
    print(hr("-"))
    # Columns: owned systems grouped by faction
    factions = [g["civ"]] + AI_PAIR[g["civ"]]
    col_w = 18
    header = "".join(f"  {cname(f):<{col_w}}" for f in factions) + "   Unexplored"
    print(header)
    print(hr("-"))

    rows = {}
    for f in factions:
        rows[f] = [sid for sid, st in g["sys"].items() if st["owner"] == f]
    unk = [sid for sid, st in g["sys"].items() if not st["explored"]]

    max_len = max(len(rows[f]) for f in factions)
    for idx in range(max(max_len, len(unk))):
        line = ""
        for f in factions:
            sids = rows[f]
            if idx < len(sids):
                sid = sids[idx]
                ships = ships_at(g, sid)
                ship_mark = " ◉" if any(s["owner"] == g["civ"] for s in ships) else ""
                line += f"  {SYSTEMS[sid]['name']}{ship_mark:<{col_w - len(SYSTEMS[sid]['name'])}}"
            else:
                line += f"  {'':<{col_w}}"
        if idx < len(unk):
            line += f"   {SYSTEMS[unk[idx]]['name']} (?)"
        print(line)
    print(hr("-"))
    # Score summary
    for f in factions:
        count = len(rows[f])
        print(f"  {CIVS[f]['sym']} {cname(f)}: {count} systems", end="   ")
    print()
    print(hr())

def show_ships(g):
    print("  YOUR SHIPS")
    print(hr("-"))
    for s in my_ships(g):
        sys_name = SYSTEMS[s["loc"]]["name"]
        adj = ", ".join(SYSTEMS[a]["name"] for a in adjacent(s["loc"]))
        print(f"  #{s['id']} [{s['type']:7}] at {sys_name:<15}  Adjacent: {adj}")
    print(hr())

def show_techs(g):
    print("  TECHNOLOGY")
    print(hr("-"))
    for tid in CIVS[g["civ"]]["techs"]:
        td = TECH[tid]
        status = "[DONE]" if tid in g["techs"] else f"[{td['cost']}🔬]"
        print(f"  {status:8} {td['name']:<24} {td['eff']}")
    print(hr())

# ─────────────────────────────────────────────
# ACTIONS
# ─────────────────────────────────────────────

def action_explore(g):
    ships = my_ships(g)
    if not ships:
        print("No ships available.")
        return
    unexplored = [s for s in ships if not g["sys"][s["loc"]]["explored"]]
    if not unexplored:
        print("None of your ships are at an unexplored system.")
        return
    print("Ships at unexplored systems:")
    for i, s in enumerate(unexplored, 1):
        print(f"  {i}. Ship #{s['id']} at {SYSTEMS[s['loc']]['name']}")
    idx = input_int("Select ship: ", 1, len(unexplored)) - 1
    if idx < 0: return
    ship = unexplored[idx]
    sid = ship["loc"]
    g["sys"][sid]["explored"] = True
    sd = SYSTEMS[sid]
    print(f"  ✓ Explored {sd['name']} — ⚙{sd['p']} 🔬{sd['r']} ◈{sd['i']} [{sd['type']}]")
    if "advanced_sensors" in g["techs"]:
        for adj in adjacent(sid):
            if not g["sys"][adj]["explored"]:
                g["sys"][adj]["explored"] = True
                print(f"    Advanced sensors reveal {SYSTEMS[adj]['name']}")
    g["acts"] -= 1

def action_colonize(g):
    ships = my_ships(g)
    eligible = [s for s in ships if g["sys"][s["loc"]]["explored"] and not g["sys"][s["loc"]]["owner"]]
    if not eligible:
        print("No ships are at an explored, unclaimed system.")
        return
    print("Ships able to colonize:")
    for i, s in enumerate(eligible, 1):
        sd = SYSTEMS[s["loc"]]
        print(f"  {i}. Ship #{s['id']} at {sd['name']} (⚙{sd['p']} 🔬{sd['r']} ◈{sd['i']})")
    idx = input_int("Select: ", 1, len(eligible)) - 1
    if idx < 0: return
    ship = eligible[idx]
    sid = ship["loc"]
    g["sys"][sid]["owner"] = g["civ"]
    g["res"]["a"] += 1
    print(f"  ✓ Colonized {SYSTEMS[sid]['name']}! Ascendancy +1 ({g['res']['a']}/20)")
    g["acts"] -= 1
    check_victory(g)

def action_move(g):
    ships = my_ships(g)
    if not ships:
        print("No ships available.")
        return
    print("Your ships:")
    for i, s in enumerate(ships, 1):
        print(f"  {i}. Ship #{s['id']} [{s['type']}] at {SYSTEMS[s['loc']]['name']}")
    idx = input_int("Select ship: ", 1, len(ships)) - 1
    if idx < 0: return
    ship = ships[idx]
    adj = adjacent(ship["loc"])
    print(f"  Adjacent systems from {SYSTEMS[ship['loc']]['name']}:")
    for i, a in enumerate(adj, 1):
        st = g["sys"][a]
        status = f"[{cname(st['owner'])}]" if st["owner"] else ("[explored]" if st["explored"] else "[unknown]")
        print(f"    {i}. {SYSTEMS[a]['name']} {status}")
    idx2 = input_int("Move to: ", 1, len(adj)) - 1
    if idx2 < 0: return
    dest = adj[idx2]
    # Move
    g["sys"][ship["loc"]]["ships"].remove(ship["id"])
    ship["loc"] = dest
    g["sys"][dest]["ships"].append(ship["id"])
    print(f"  ✓ Ship #{ship['id']} moved to {SYSTEMS[dest]['name']}")
    g["acts"] -= 1
    # Combat check
    enemies = [s for s in g["ships"] if s["loc"] == dest and s["owner"] != g["civ"]]
    if enemies:
        combat(g, g["civ"], enemies[0]["owner"], dest)

def action_build(g):
    owned = [(sid, st) for sid, st in g["sys"].items() if st["owner"] == g["civ"]]
    if g["res"]["p"] < 3:
        print(f"  Insufficient production (need 3, have {g['res']['p']}).")
        return
    print("Your systems:")
    for i, (sid, _) in enumerate(owned, 1):
        print(f"  {i}. {SYSTEMS[sid]['name']}")
    idx = input_int("Build at: ", 1, len(owned)) - 1
    if idx < 0: return
    sid = owned[idx][0]
    g["res"]["p"] -= 3
    add_ship(g, g["civ"], "scout", sid)
    g["acts"] -= 1
    print(f"  ✓ New scout ship built at {SYSTEMS[sid]['name']}.")

def action_research(g):
    if g["res"]["r"] < 4:
        print(f"  Insufficient research (need 4, have {g['res']['r']}).")
        return
    avail = [t for t in CIVS[g["civ"]]["techs"] if t not in g["techs"]]
    if not avail:
        print("  All technologies researched!")
        return
    print("Available technologies:")
    for i, tid in enumerate(avail, 1):
        td = TECH[tid]
        mark = "  " if g["res"]["r"] >= td["cost"] else "✗ "
        print(f"  {i}. {mark}{td['name']:<24} (cost {td['cost']}🔬)  {td['eff']}")
    idx = input_int("Research: ", 1, len(avail)) - 1
    if idx < 0: return
    tid = avail[idx]
    td = TECH[tid]
    if g["res"]["r"] < td["cost"]:
        print(f"  Not enough research ({td['cost']} needed).")
        return
    g["res"]["r"] -= td["cost"]
    g["techs"].add(tid)
    apply_tech(g, tid)
    g["acts"] -= 1
    print(f"  ✓ Research complete: {td['name']}")

def apply_tech(g, tid):
    if tid == "diplomacy_corps":  g["res"]["i"] += 2
    if tid == "replicators":      g["res"]["p"] += 2
    if tid == "singularity_core": g["res"]["p"] += 3

# ─────────────────────────────────────────────
# COMBAT
# ─────────────────────────────────────────────

def combat(g, attacker, defender, sys_id):
    ac, dc = CIVS[attacker], CIVS[defender]
    ar = roll6() + ac["com"] + (2 if attacker == g["civ"] and "disruptors" in g["techs"] else 0)
    dr = roll6() + dc["com"] + (1 if defender == g["civ"] and "deflector_shields" in g["techs"] else 0)
    name = SYSTEMS[sys_id]["name"]
    print(f"\n  ⚔ COMBAT at {name}: {ac['short']}[{ar}] vs {dc['short']}[{dr}]")
    winner = attacker if ar > dr else defender
    loser  = defender if ar > dr else attacker
    loser_ship = next((s for s in g["ships"] if s["loc"] == sys_id and s["owner"] == loser), None)
    if loser_ship:
        g["ships"].remove(loser_ship)
        g["sys"][sys_id]["ships"].remove(loser_ship["id"])
        print(f"  {CIVS[winner]['short']} wins — enemy ship destroyed!")
        if winner == g["civ"]:
            bonus = 3 if "warriors_code" in g["techs"] else 1
            g["res"]["a"] += bonus
            print(f"  Ascendancy +{bonus} from victory! ({g['res']['a']}/20)")
            if "battle_tactics" in g["techs"]:
                g["acts"] += 1
                print("  Battle Tactics: +1 bonus action!")
        # Capture system
        still_there = any(s for s in g["ships"] if s["loc"] == sys_id and s["owner"] == loser)
        if not still_there and g["sys"][sys_id]["owner"] == loser:
            g["sys"][sys_id]["owner"] = winner
            print(f"  {name} captured by {CIVS[winner]['short']}!")
            if winner == g["civ"]:
                g["res"]["a"] += 2
    else:
        print(f"  {CIVS[winner]['short']} repels the attack.")
    check_victory(g)

# ─────────────────────────────────────────────
# AI
# ─────────────────────────────────────────────

def run_ai(g):
    for ai in AI_PAIR[g["civ"]]:
        ai_ships = [s for s in g["ships"] if s["owner"] == ai]
        for ship in ai_ships:
            st = g["sys"][ship["loc"]]
            if not st["explored"]: st["explored"] = True
            if st["explored"] and not st["owner"]:
                st["owner"] = ai
                print(f"  {cname(ai)} colonizes {SYSTEMS[ship['loc']]['name']}.")
            adj = adjacent(ship["loc"])
            pref = next((a for a in adj if not g["sys"][a]["owner"]), None) or \
                   next((a for a in adj if g["sys"][a]["owner"] != ai), None) or \
                   (adj[0] if adj else None)
            if pref:
                g["sys"][ship["loc"]]["ships"].remove(ship["id"])
                ship["loc"] = pref
                g["sys"][pref]["ships"].append(ship["id"])
                player_there = [s for s in g["ships"] if s["loc"]==pref and s["owner"]==g["civ"]]
                if player_there:
                    combat(g, ai, g["civ"], pref)
        owned = [sid for sid, st in g["sys"].items() if st["owner"] == ai]
        if len(owned) >= 2 and random.random() > 0.65:
            add_ship(g, ai, "scout", random.choice(owned))

# ─────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────

def collect_resources(g):
    civ = CIVS[g["civ"]]
    p = r = i = 0
    for sid, st in g["sys"].items():
        if st["owner"] == g["civ"]:
            sd = SYSTEMS[sid]; p += sd["p"]; r += sd["r"]; i += sd["i"]
    if "diplomacy_corps"  in g["techs"]: i += 1
    if "replicators"      in g["techs"]: p += 1
    if "singularity_core" in g["techs"]: p += 2
    p += civ["prod"] - 2; r += civ["res"] - 2; i += civ["inf"] - 2
    g["res"]["p"] += max(1, p)
    g["res"]["r"] += max(1, r)
    g["res"]["i"] += max(1, i)
    ctrl = sum(1 for st in g["sys"].values() if st["owner"] == g["civ"])
    if ctrl >= 3: g["res"]["a"] += ctrl // 3

# ─────────────────────────────────────────────
# VICTORY
# ─────────────────────────────────────────────

def check_victory(g):
    civ_name = CIVS[g["civ"]]["name"]
    if g["res"]["a"] >= 20:
        print(f"\n{'═'*56}")
        print(f"  ✦ ASCENDANCY ACHIEVED — Turn {g['turn']} ✦")
        print(f"  {civ_name} has achieved galactic Ascendancy!")
        print(f"{'═'*56}\n")
        sys.exit(0)
    mine = sum(1 for st in g["sys"].values() if st["owner"] == g["civ"])
    if mine >= 8:
        print(f"\n{'═'*56}")
        print(f"  ✦ GALACTIC CONQUEST — {mine} systems controlled ✦")
        print(f"  {civ_name} spans the known galaxy!")
        print(f"{'═'*56}\n")
        sys.exit(0)
    for ai in AI_PAIR[g["civ"]]:
        ai_sys = sum(1 for st in g["sys"].values() if st["owner"] == ai)
        if ai_sys >= 8:
            print(f"\n{'═'*56}")
            print(f"  ⚔ DEFEAT — {CIVS[ai]['name']} has conquered the galaxy.")
            print(f"{'═'*56}\n")
            sys.exit(0)

# ─────────────────────────────────────────────
# INPUT
# ─────────────────────────────────────────────

def input_int(prompt, lo, hi):
    while True:
        try:
            raw = input(f"  {prompt}").strip()
            if raw.lower() in ("q","quit","cancel","back",""):
                return -1
            v = int(raw)
            if lo <= v <= hi:
                return v
            print(f"  Enter a number between {lo} and {hi}, or 'back'.")
        except (ValueError, EOFError):
            return -1

def pick_civ():
    print()
    print("  ╔══════════════════════════════════════╗")
    print("  ║  MIIRR — Star Trek: Ascendancy       ║")
    print("  ╚══════════════════════════════════════╝")
    print()
    civs = list(CIVS.keys())
    for i, k in enumerate(civs, 1):
        c = CIVS[k]
        print(f"  {i}. {c['sym']} {c['name']}")
        print(f"     ⚙{c['prod']}  🔬{c['res']}  ◈{c['inf']}  ⚔{c['com']}")
        print()
    idx = input_int("Choose civilization: ", 1, len(civs)) - 1
    if idx < 0:
        print("Goodbye."); sys.exit(0)
    return civs[idx]

# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────

ACTIONS = {
    "1": ("Explore System",   action_explore),
    "2": ("Colonize System",  action_colonize),
    "3": ("Move Ship",        action_move),
    "4": ("Build Ship (3⚙)", action_build),
    "5": ("Research Tech",    action_research),
    "m": ("Show Map",         lambda g: show_map(g) or True),
    "s": ("Show Ships",       lambda g: show_ships(g) or True),
    "t": ("Show Techs",       lambda g: show_techs(g) or True),
    "e": ("End Turn",         None),
}

def main():
    civ_key = pick_civ()
    g = new_game(civ_key)
    civ = CIVS[civ_key]
    print(f"\n  {civ['sym']} {civ['name']} — engage!\n")
    input("  [Press Enter to begin]")

    while True:
        show_status(g)
        show_map(g)

        if g["acts"] <= 0:
            print("  No actions remaining. Ending turn...")
            input("  [Press Enter]")
        else:
            print("  ACTIONS:")
            for key, (label, _) in ACTIONS.items():
                if key.isdigit():
                    print(f"    [{key}] {label}")
            print(f"    [e] End Turn    [m] Map    [s] Ships    [t] Techs")
            print()
            choice = input("  > ").strip().lower()

            if choice == "e":
                pass  # fall through to end turn
            elif choice in ACTIONS and ACTIONS[choice][1] is not None:
                _, fn = ACTIONS[choice]
                fn(g)
                input("\n  [Press Enter to continue]")
                continue
            else:
                input("  Unknown command. [Press Enter]")
                continue

        # End of player turn
        print(f"\n  ── Turn {g['turn']} complete. AI factions acting… ──")
        run_ai(g)
        collect_resources(g)
        g["turn"] += 1
        g["acts"] = civ["actions"]
        print(f"  ── Turn {g['turn']} begins. Resources collected. ──")
        print(f"  ⚙+{g['res']['p']}  🔬+{g['res']['r']}  ◈+{g['res']['i']}  ✦{g['res']['a']}/20")
        check_victory(g)
        input("  [Press Enter]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Qapla'! (Goodbye)\n")
