import io, json, re, html, time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT = Path("app/src/main/assets/graphics")
FILES = {
 "panel": "Circuit Breakers.JPG", "fittings": "Plumbing fittings.jpg",
 "pipes": "Plumbing pipes.jpg", "meter": "Multi meter 2.jpg",
 "valve": "Valve (ball) detailed.jpg", "cable": "Connecting to electricity meter.JPG",
 "heating": "Einrohrheizung.JPG", "plumbing": "Plumbing heating 1.jpg",
 "relay": "Electrical Relay.jpg", "drain": "Potrubie pvc.jpg",
 "leak": "Leaky pipe removed ready for new connection.jpg",
 "filter": "Under-sink Water Filter System.jpg",
 "prep": "Drilling (243383107).jpg", "electric": "An electrician.jpg"
}
def get(url):
    for attempt in range(3):
        try:
            with urlopen(Request(url, headers={"User-Agent":"RozcinkyPhotoImporter/1.0 (https://github.com/dim20041978-png/ROZCINKY-ANDROID)"}), timeout=60) as response:
                return response.read(25000001)
        except Exception:
            if attempt == 2: raise
            time.sleep(5*(attempt+1))
def clean(value):
    return html.unescape(re.sub(r"<[^>]*>", "", value)).strip()
ROOT.mkdir(parents=True, exist_ok=True)
credits = []
for key, filename in FILES.items():
    params = dict(action="query", format="json", titles="File:"+filename, redirects=1, prop="imageinfo", iiprop="url|mime|extmetadata", iiurlwidth=320)
    pages = json.loads(get("https://commons.wikimedia.org/w/api.php?"+urlencode(params)))["query"]["pages"]
    page = next(iter(pages.values()))
    info = page["imageinfo"][0]
    meta = info["extmetadata"]
    def val(k): return clean(meta.get(k, {}).get("value", ""))
    license_name, license_url, artist = val("LicenseShortName"), val("LicenseUrl"), val("Artist")
    if not re.fullmatch(r"CC (?:BY(?:-SA)? [1-4]\\.0|0(?: 1\\.0)?)|CC0(?: 1\\.0)?", license_name) or not license_url.startswith("https://creativecommons.org/") or not artist:
        raise RuntimeError("Unverified license or author: "+filename+" "+license_name)
    if info["mime"] not in ("image/jpeg","image/png"): raise RuntimeError("Not a raster photo: "+filename)
    url = info.get("thumburl", info["url"])
    if not url.startswith("https://upload.wikimedia.org/"): raise RuntimeError("Unexpected host")
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(get(url)))).convert("RGB")
    image.thumbnail((320,320))
    image.save(ROOT / ("jobs_"+key+".jpg"), quality=85)
    credits.append(dict(asset="jobs_"+key+".jpg", title=page["title"], author=artist, license=license_name, license_url=license_url, source=info["descriptionurl"], modifications="Resized and converted to JPEG"))
    print(key, license_name, flush=True)
    time.sleep(1)
(ROOT/"photo_credits.json").write_text(json.dumps(credits, ensure_ascii=False, indent=2), encoding="utf-8")
