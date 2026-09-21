"""Optional asset refresh: python -m pip install Pillow, then run this script.

Normal builds use committed assets and never fetch remote project images.
Historical source images are retained under webpage/ for the original Django site.
"""
from io import BytesIO
import json
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'src/static/images'
ORIGINALS = ROOT / 'webpage/projects/static/projects/images'


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    data = json.loads((ROOT / 'content/portfolio/projects.json').read_text(encoding='utf-8'))
    for project in data['projects']:
        source = project['image_source']
        if source.startswith('https://'):
            request = Request(source, headers={'User-Agent': 'Portfolio-asset-refresh/1.0'})
            with urlopen(request, timeout=30) as response:
                image = Image.open(BytesIO(response.read()))
        else:
            image = Image.open(ORIGINALS / Path(source).name)
        # Static preview frames keep animations from distracting from the project content.
        image.seek(0)
        image = ImageOps.exif_transpose(image).convert('RGB')
        image = ImageOps.fit(image, (800, 450), method=Image.Resampling.LANCZOS)
        target = OUTPUT / (project['slug'] + '.webp')
        image.save(target, 'WEBP', quality=82, method=6)
        print(f'{target.name}: {target.stat().st_size:,} bytes')
    hero = ImageOps.exif_transpose(Image.open(ORIGINALS / 'header.jpg')).convert('RGB')
    hero.thumbnail((1920, 1280), Image.Resampling.LANCZOS)
    hero.save(OUTPUT / 'header.webp', 'WEBP', quality=82, method=6)
    ImageOps.fit(hero, (1200, 630), method=Image.Resampling.LANCZOS).save(OUTPUT / 'social-preview.jpg', quality=85, optimize=True)


if __name__ == '__main__':
    main()
