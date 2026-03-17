# rds-station-db

Base de données open source des stations de radio FM avec leurs codes RDS (PI / PS) et logos.
Conçue pour être consommée par [fm-monitor](https://github.com/LyonelB/fm-monitor) via requêtes HTTP directes sur les fichiers JSON bruts GitHub.

[![Validate JSON](https://github.com/LyonelB/rds-station-db/actions/workflows/validate.yml/badge.svg)](https://github.com/LyonelB/rds-station-db/actions/workflows/validate.yml)
[![License: CC0](https://img.shields.io/badge/License-CC0_1.0-lightgrey.svg)](LICENSE)

## Structure

```
data/
  FR.json          → France (22 stations)
  _schema.json     → Schéma JSON de référence
logos/
  FR/FA41.png      → Logo indexé par code PI
scripts/
  validate.py      → Validation CI
  fetch_logos.py   → Récupération automatique via radio-browser.info
  rds_lookup.py    → Module Python prêt pour fm-monitor
.github/
  ISSUE_TEMPLATE/  → Formulaires de contribution (add / modify / remove)
  workflows/       → CI GitHub Actions
```

## Utilisation depuis fm-monitor

```python
from rds_lookup import RDSLookup

lookup = RDSLookup(country="FR")
station = lookup.get(pi="FA41", ps="GRAFFITI")

if station:
    print(station["name"])      # Graffiti Radio
    print(station["logo_url"])  # https://raw.github...
```

Cache local 24h, refresh automatique en arrière-plan.

**URL directe :**
```
https://raw.githubusercontent.com/LyonelB/rds-station-db/main/data/FR.json
```

## Contribuer

Utilisez les [GitHub Issues](../../issues/new/choose) :
- ➕ **Ajouter** une station
- ✏️ **Modifier** une station existante
- 🗑️ **Retirer** une station ou des données

## Récupération automatique de logos

```bash
python3 scripts/fetch_logos.py --country FR --dry-run
python3 scripts/fetch_logos.py --country FR
```

## Licence

Données : **[CC0 1.0](LICENSE)** (domaine public).
Logos : appartiennent à leurs propriétaires respectifs.

---
Projet initié par [@LyonelB](https://github.com/LyonelB) pour [fm-monitor](https://github.com/LyonelB/fm-monitor).
