"""Deterministic PNG previews; no RAW development or source writes."""
import base64
from io import BytesIO
import struct
import zlib
from PIL import Image, ImageEnhance, ImageOps
from . import contracts_v01 as c


def load_media(directory):
    import json, wave
    from pathlib import Path
    root=Path(directory).resolve()
    manifest=json.loads((root/'manifest.json').read_bytes())
    c.exact(manifest,('version','kind','duration_seconds','fps','width','height','frames','audio','content'),'media_manifest')
    c.require(manifest['version']=='ews.media_fixture.v01' and manifest['kind']=='SYNTHETIC_FRAME_SEQUENCE_AND_PCM_WAV', 'media_format')
    for name,expected in (('duration_seconds',8),('fps',2),('width',480),('height',270)):
        c.require(type(manifest[name]) is int and manifest[name]==expected,'media_'+name)
    c.require(type(manifest['frames']) is list and len(manifest['frames'])==16,'media_frames')
    paths=[]
    for i,row in enumerate(manifest['frames']):
        c.exact(row,('name','sha256'),'media_frame_shape')
        c.require(row['name']==f'frame_{i:02d}.png','media_frame_path')
        path=root/row['name'];c.require(path.is_file() and not path.is_symlink(),'media_regular_file')
        b=path.read_bytes();c.require(c.digest(b)==row['sha256'] and preview_dimensions(b)==(480,270),'media_frame_binding')
        paths.append(path)
    audio=manifest['audio']
    c.exact(audio,('name','sha256','pcm_sha256','sample_rate','channels','sample_width','samples'),'media_audio_shape')
    c.require(audio['name']=='tone.wav','media_audio_path')
    path=root/audio['name'];c.require(path.is_file() and not path.is_symlink(),'media_audio_regular')
    c.require(c.digest(path.read_bytes())==audio['sha256'],'media_audio_binding')
    with wave.open(str(path),'rb') as stream:
        c.require(stream.getparams()[:4]==(1,2,8000,64000) and stream.getcomptype()=='NONE','media_audio_encoding')
        pcm=stream.readframes(64000)
    c.require(c.digest(pcm)==audio['pcm_sha256'] and all(type(audio[k]) is int and audio[k]==v for k,v in
        dict(sample_rate=8000,channels=1,sample_width=2,samples=64000).items()),'media_pcm_binding')
    return dict(manifest=manifest,frames=tuple(paths),audio=path)


def media_plan(material):
    c.exact(material,('contract','media','photo_work','audio_source'),'media_plan_input')
    contract=material['contract'];obligations=contract['media'];manifest=material['media']
    c.require(contract['source_write'] is False and contract['publication'] is False and contract['save']=='selected_only', 'media_hard_boundary')
    c.require(obligations['video'] is True and obligations['audio_policy'] in ('SILENT_CONTINUE','REQUIRE_AUDIO'), 'media_obligations')
    c.require(len(manifest['frames'])==manifest['fps']*manifest['duration_seconds']==16 and manifest['audio']['samples']==64000,'media_finite_batch')
    c.require(material['audio_source']['available'] is True or obligations['audio'] is False,'media_initial_audio_unavailable')
    return dict(frame_sha256s=[r['sha256'] for r in manifest['frames']],pcm_sha256=manifest['audio']['pcm_sha256'],
        duration_seconds=manifest['duration_seconds'],fps=manifest['fps'],sample_rate=manifest['audio']['sample_rate'],
        audio=obligations['audio'],audio_policy=obligations['audio_policy'],speech_review=obligations['speech_review'],
        photo_work_ref=c.identity('retained_photo',material['photo_work']),audio_source_ref=c.identity('audio_source',material['audio_source']))


def privacy_policy(value):
    c.require(type(value) is str and value in ('preview_only', 'preview_without_metadata'), 'privacy_policy')
    return value


def preview_dimensions(png):
    c.require(type(png) is bytes and len(png) <= 5_000_000 and png.startswith(b'\x89PNG\r\n\x1a\n'), 'derived_png')
    # Only pixel-bearing PNG chunks are permitted, including in the looser mode.
    offset, chunks = 8, []
    while offset < len(png):
        c.require(offset + 12 <= len(png), 'derived_png_chunk')
        length, kind = struct.unpack_from('>I4s', png, offset)
        end = offset + 12 + length
        c.require(end <= len(png) and kind in (b'IHDR', b'IDAT', b'IEND'), 'derived_png_metadata_forbidden')
        c.require((kind != b'IHDR' or length == 13) and (kind != b'IEND' or length == 0), 'derived_png_chunk_length')
        crc = struct.unpack_from('>I', png, end - 4)[0]
        c.require(crc == zlib.crc32(png[offset + 4:end - 4]), 'derived_png_crc')
        chunks.append(kind)
        offset = end
    c.require(len(chunks) >= 3 and chunks[0] == b'IHDR' and chunks[-1] == b'IEND'
        and all(kind == b'IDAT' for kind in chunks[1:-1]), 'derived_png_structure')
    with Image.open(BytesIO(png)) as image:
        c.require(image.format == 'PNG' and image.mode == 'RGB' and not image.info
            and 0 < image.width <= 1200 and 0 < image.height <= 800, 'derived_pixel_limits')
        dimensions = image.size
        image.verify()
    return dimensions


def validate_transfer(value, minimize, fields):
    privacy_policy(minimize)
    c.exact(value, tuple(fields) + (('derived',) if minimize == 'preview_only' else ()), 'privacy_transfer_fields')
    c.require(type(value['png']) is str and type(value['sha256']) is str, 'derived_transfer_types')
    png = base64.b64decode(value['png'], validate=True)
    c.require(c.digest(png) == value['sha256'], 'derived_bytes_binding')
    width, height = preview_dimensions(png)
    if minimize == 'preview_only':
        derived = value['derived']
        c.exact(derived, ('width', 'height', 'exposure', 'crop', 'preview'), 'privacy_derived_fields')
        c.require(type(derived['width']) is int and type(derived['height']) is int
            and (derived['width'], derived['height']) == (width, height), 'derived_dimensions')
        c.command(dict(op='EXPOSURE', value=derived['exposure']), ('EXPOSURE',))
        c.command(dict(op='CROP', value=derived['crop']), ('CROP',))
        c.require(type(derived['preview']) is str and derived['preview'] in ('fit', 'contain'), 'derived_preview')
    return png


def render(source_bytes, exposure, crop, preview='fit'):
    c.require(type(source_bytes) is bytes and len(source_bytes) <= 8_000_000, 'source_limit')
    c.command(dict(op='EXPOSURE', value=exposure), ('EXPOSURE',))
    c.command(dict(op='CROP', value=crop), ('CROP',))
    c.require(type(preview) is str and preview in ('fit', 'contain'), 'preview_mode')
    with Image.open(BytesIO(source_bytes)) as source:
        c.require(source.format in ('PNG','JPEG') and source.width*source.height <= 12_000_000, 'image_format_limit')
        image = ImageOps.exif_transpose(source).convert('RGB')
    ratio = {'SQUARE': 1, 'WIDE': 16/9}.get(crop)
    if ratio:
        width, height = image.size
        if width/height > ratio:
            w = int(height*ratio)
            image = image.crop(((width-w)//2,0,(width+w)//2,height))
        else:
            h = int(width/ratio)
            image = image.crop((0,(height-h)//2,width,(height+h)//2))
    image = ImageEnhance.Brightness(image).enhance(2**(exposure/10))
    image.thumbnail((1200,800) if preview == 'fit' else (960,640), Image.Resampling.LANCZOS)
    # RGB conversion can retain EXIF in image.info; a fresh pixel image cannot.
    image = Image.frombytes('RGB', image.size, image.tobytes())
    output = BytesIO()
    image.save(output, format='PNG', optimize=False)
    png = output.getvalue()
    preview_dimensions(png)
    return png
