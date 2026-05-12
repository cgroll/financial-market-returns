"""Download Ken French 30 Industry Portfolios daily returns data."""

import urllib.request
import zipfile
import io
from fmr.paths import ProjPaths

URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/30_Industry_Portfolios_daily_TXT.zip"

paths = ProjPaths()
dest = paths.industry_portfolios_30_path
dest.mkdir(parents=True, exist_ok=True)

print(f"Downloading {URL} ...")
with urllib.request.urlopen(URL) as response:
    data = response.read()

print(f"Extracting to {dest} ...")
with zipfile.ZipFile(io.BytesIO(data)) as zf:
    zf.extractall(dest)
    extracted = zf.namelist()

print(f"Extracted {len(extracted)} file(s):")
for name in extracted:
    print(f"  {name}")

print(f"Done → {dest}")
