import os
import subprocess
from datetime import datetime
from pathlib import Path

backup_dir = Path(os.getenv("BACKUP_DIR", "/backups"))
backup_dir.mkdir(parents=True, exist_ok=True)
filename = backup_dir / f"nexa_{datetime.utcnow():%Y%m%dT%H%M%SZ}.dump"
subprocess.run(["pg_dump", os.environ["DATABASE_URL"], "--format=custom", "--file", str(filename)], check=True)
print(filename)
