"""Download Ken French international country returns data.

Source: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
"""

import urllib.request
import zipfile
import io
from fmr.paths import ProjPaths

URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_International_Countries.zip"

paths = ProjPaths()
dest = paths.international_countries_path
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
