"""Deterministic synthetic photographs, generated only in a new owned directory."""
from pathlib import Path
import random
from PIL import Image, ImageDraw


def generate(directory, count=6):
    root = Path(directory)
    root.mkdir(mode=0o700, parents=True, exist_ok=False)
    paths = []
    for i in range(count):
        rng = random.Random(3401+i)
        image = Image.new('RGB', (1440,960))
        pixels = image.load()
        palettes = [(105,176,206),(192,147,153),(141,185,162),(121,157,195),(211,180,120),(172,161,197)]
        base = palettes[i % len(palettes)]
        for y in range(960):
            for x in range(1440):
                noise = rng.randrange(-5,6)
                pixels[x,y] = tuple(max(0,min(255, int(v + 36*(1-y/960)+noise))) for v in base)
        d = ImageDraw.Draw(image)
        for layer in range(4):
            points = [(0,960)] + [(x, 440+layer*100+rng.randrange(-140,90)) for x in range(0,1500,110)] + [(1440,960)]
            d.polygon(points, fill=(40+layer*14+i*3,82+layer*17,95+layer*14))
        for j in range(12):
            x, y = rng.randrange(1440), rng.randrange(700,950)
            d.ellipse((x,y,x+15,y+4), fill=(187,211,186))
        path = root / f'landscape_{i+1:02d}.png'
        image.save(path)
        paths.append(path)
    return tuple(paths)


def generate_media(directory):
    """Eight seconds: 16 synthetic RGB frames at 2 fps and mono 8 kHz PCM WAV."""
    import hashlib, json, math, struct, wave
    root=Path(directory)
    root.mkdir(mode=0o700,parents=True,exist_ok=False)
    frames=[]
    for i in range(16):
        image=Image.new('RGB',(480,270),(28,98,125))
        draw=ImageDraw.Draw(image)
        draw.rectangle((0,175,480,270),fill=(58,151,115))
        draw.rectangle((18+i*22,110,68+i*22,170),fill=(245,215,90))
        draw.text((18,20),f'Synthetic motion study / frame {i+1:02d}',fill='white')
        path=root/f'frame_{i:02d}.png';image.save(path)
        frames.append(dict(name=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    pcm=b''.join(struct.pack('<h',int(7000*math.sin(2*math.pi*(330 if i//8000%2==0 else 440)*i/8000))) for i in range(64000))
    audio=root/'tone.wav'
    with wave.open(str(audio),'wb') as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(8000);out.writeframes(pcm)
    manifest=dict(version='ews.media_fixture.v01',kind='SYNTHETIC_FRAME_SEQUENCE_AND_PCM_WAV',duration_seconds=8,fps=2,
        width=480,height=270,frames=frames,audio=dict(name='tone.wav',sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),
        pcm_sha256=hashlib.sha256(pcm).hexdigest(),sample_rate=8000,channels=1,sample_width=2,samples=64000),
        content='Moving rectangle with alternating tones; no recorded speech or physical sound claim.')
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return root
