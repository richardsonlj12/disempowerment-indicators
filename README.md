# KEEL: Indicators of gradual disempowerment

KEEL is a public static website that tracks indicators of AI-driven "gradual disempowerment" (after Kulveit et al. 2025), built entirely from free public data. A Python package (`indicators`) fetches and processes the data, and a Quarto site renders it.

- Repository: [richardsonlj12/keel](https://github.com/richardsonlj12/keel)
- Website: https://richardsonlj12.github.io/keel/

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

Network tests are marked `live` and excluded by default; run them with `pytest -m live`.

## Preview the site

Install Quarto (>= 1.11) without admin rights from the official GitHub release (macOS):

```bash
mkdir -p ~/.local/opt/quarto ~/.local/bin
curl -L -o quarto.tar.gz https://github.com/quarto-dev/quarto-cli/releases/download/v1.11.9/quarto-1.11.9-macos.tar.gz
tar xzf quarto.tar.gz -C ~/.local/opt/quarto
ln -sf ~/.local/opt/quarto/bin/quarto ~/.local/bin/quarto
quarto --version
```

Make sure `~/.local/bin` is on your `PATH`. Then, from the repo root:

```bash
quarto preview site
```
