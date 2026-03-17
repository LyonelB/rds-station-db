#!/usr/bin/env python3
"""fetch_logos.py - Auto-fetch station logos from radio-browser.info
Usage:
  python3 scripts/fetch_logos.py --country FR
  python3 scripts/fetch_logos.py --country FR --dry-run
  python3 scripts/fetch_logos.py --all
"""
import argparse, json, time, urllib.request, urllib.parse, urllib.error
from pathlib import Path

DATA_DIR   = Path(__file__).parent.parent / "data"
LOGOS_DIR  = Path(__file__).parent.parent / "logos"
RB_API     = "https://de1.api.radio-browser.info"
USER_AGENT = "rds-station-db/1.0 (https://github.com/LyonelB/rds-station-db)"

def rb_search(name, countrycode):
    url = (f"{RB_API}/json/stations/search"
           f"?name={urllib.parse.quote(name)}&countrycode={countrycode}"
           f"&limit=5&hidebroken=true&order=votes&reverse=true")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"  [radio-browser] Error: {e}"); return []

def best_favicon(results, name):
    name_lower = name.lower()
    for r in results:
        if r.get("favicon") and (name_lower in r.get("name","").lower()
                                  or r.get("name","").lower() in name_lower):
            return r["favicon"]
    for r in results:
        if r.get("favicon"): return r["favicon"]
    return None

def download_logo(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
            if len(data) < 100: return False
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data); return True
    except Exception as e:
        print(f"  [download] Error: {e}"); return False

def process_country(cc, dry_run=False):
    json_file = DATA_DIR / f"{cc}.json"
    if not json_file.exists(): print(f"File not found: {json_file}"); return
    with open(json_file) as f: data = json.load(f)
    modified = False
    for s in data["stations"]:
        pi, name = s["pi"], s["name"]
        if s.get("logo_url") and s.get("logo_source") == "local":
            existing = list((LOGOS_DIR / cc).glob(f"{pi}.*"))
            if existing:
                print(f"  [{pi}] {name} — logo local présent ({existing[0].name})")
                continue
            else:
                print(f"  [{pi}] {name} — logo_url défini mais fichier absent, recherche...")
        elif s.get("logo_url"):
            print(f"  [{pi}] {name} — logo déjà présent ({s.get('logo_source')})")
            continue
        print(f"  [{pi}] {name} — recherche...")
        results  = rb_search(name, cc)
        favicon  = best_favicon(results, name)
        if not favicon: print(f"  [{pi}] {name} — introuvable"); continue
        ext       = Path(urllib.parse.urlparse(favicon).path).suffix or ".png"
        local_path = LOGOS_DIR / cc / f"{pi}{ext}"
        raw_url   = (f"https://raw.githubusercontent.com/LyonelB/rds-station-db/main"
                     f"/logos/{cc}/{pi}{ext}")
        if dry_run: print(f"  [{pi}] {name} — téléchargerait : {favicon}"); continue
        if download_logo(favicon, local_path):
            s["logo_url"] = raw_url; s["logo_source"] = "radio-browser"
            print(f"  [{pi}] {name} — ✅ {local_path.name}"); modified = True
        else:
            print(f"  [{pi}] {name} — ❌ échec")
        time.sleep(0.5)
    if modified and not dry_run:
        with open(json_file, "w") as f: json.dump(data, f, indent=2, ensure_ascii=False); f.write("\n")
        print(f"\nMis à jour : {json_file.name}")

def main():
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--country"); g.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run: print("[DRY RUN]\n")
    countries = [f.stem for f in sorted(DATA_DIR.glob("*.json")) if f.stem != "_schema"] \
        if args.all else [args.country.upper()]
    for cc in countries:
        print(f"\n=== {cc} ==="); process_country(cc, args.dry_run)

if __name__ == "__main__": main()
