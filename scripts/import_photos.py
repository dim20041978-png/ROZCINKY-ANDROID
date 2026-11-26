import io, json, re, html, time
from pathlib import Path
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen
from PIL import Image, ImageOps

ROOT = Path("app/src/main/assets/graphics")
FILES = {
 "breaker": "Miniature circuit breaker.png",
 "socket_box": "Electrical box01.jpg",
 "electric_meter": "Electric meter and the circuit breaker.JPG",
 "chase_brick": "Clay block ( proton porotherm ) wall with chases.jpg",
 "rcd": "ResidualCurrentCircuitBreak.jpg",
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
    if "missing" in page or not page.get("imageinfo"):
        raise RuntimeError(f"Commons file missing or has no imageinfo: {filename}")
    info = page["imageinfo"][0]
    meta = info["extmetadata"]
    def val(k): return clean(meta.get(k, {}).get("value", ""))
    license_name, license_url, artist = val("LicenseShortName"), val("LicenseUrl"), val("Artist")
    license_name = " ".join(license_name.split())
    license_parts = urlsplit(license_url)
    match = re.fullmatch(r"CC (BY(?:-SA)?) ([1-4][.]0)", license_name)
    zero = license_name in ("CC0", "CC0 1.0", "CC 0", "CC 0 1.0")
    expected = ("/licenses/"+match.group(1).lower()+"/"+match.group(2)+"/") if match else "/publicdomain/zero/1.0/"
    valid_url = license_parts.scheme in ("http","https") and license_parts.hostname == "creativecommons.org" and re.fullmatch(re.escape(expected.rstrip("/")) + r"(?:/(?:deed|legalcode)(?:[.][a-zA-Z0-9-]+)?)?/?", license_parts.path) is not None
    if not (match or zero) or not valid_url or not artist:
        raise RuntimeError(f"Unverified metadata: {filename}; license={license_name!r}; url={license_url!r}; author={artist!r}")
    if info["mime"] not in ("image/jpeg","image/png"): raise RuntimeError("Not a raster photo: "+filename)
    url = None
    for candidate in (info.get("thumburl"), info.get("url")):
        if not candidate: continue
        parts = urlsplit(candidate if not candidate.startswith("//") else "https:"+candidate)
        if parts.scheme in ("http", "https") and parts.hostname == "upload.wikimedia.org" and not parts.username and not parts.password and parts.port in (None, 443, 80):
            url = parts._replace(scheme="https", netloc="upload.wikimedia.org").geturl()
            break
    if url is None:
        raise RuntimeError(f"Unexpected image host for {filename}: thumb={info.get('thumburl')!r}, original={info.get('url')!r}")
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(get(url)))).convert("RGB")
    image.thumbnail((320,320))
    image.save(ROOT / ("jobs_"+key+".jpg"), quality=85)
    credits.append(dict(asset="jobs_"+key+".jpg", title=page["title"], author=artist, license=license_name, license_url=license_url, source=info["descriptionurl"], modifications="Resized and converted to JPEG"))
    print(key, page["title"], license_name, artist, info["descriptionurl"], flush=True)
    time.sleep(1)
(ROOT/"photo_credits.json").write_text(json.dumps(credits, ensure_ascii=False, indent=2), encoding="utf-8")
