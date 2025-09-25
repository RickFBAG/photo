Smart Display for Inky Impression 7.3" (Pi Zero 2 W)

Quick start
- Python 3.11+ recommended
- Install on Raspberry Pi OS (Bookworm) with PIL and Inky libraries

Structure
- `app/` core code (renderer, widgets, services, web)
- `config/` settings and themes
- `run.py` entrypoint

Setup (Pi)
```bash
sudo apt update && sudo apt install -y python3-pip python3-pil python3-numpy
pip3 install -r requirements.txt
python3 run.py
```

Notes
- First run will create default `config/settings.yaml`.
- Web UI served on http://<pi-ip>:8080 for configuration and preview.


