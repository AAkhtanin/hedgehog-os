"""Strict domain values; none of these records grants execution authority."""
import hashlib
import json

VERSION = 'ews.photo.v01'
MIXED_VERSION = 'ews.mixed.v01'
CLASSES = ('MediaSourceNeedle', 'RenderEngineNeedle', 'DisplayGatewayNeedle',
           'ControlSurfaceNeedle', 'AudioSinkNeedle', 'SidecarWriteNeedle')
BASE = ('NEXT', 'PREVIOUS', 'RATE', 'SELECT')
EDIT = ('EXPOSURE', 'CROP')
REQUEST_A = ('Set up a temporary workspace for these photographs. Show previews on the large display '
    'and give me phone controls to browse, rate, select, adjust exposure and crop. Do not change '
    'originals or publish anything. Save the selected ratings and preview parameters only after '
    'I separately confirm, then close everything.')
REQUEST_B = ('I only want to browse, rate and select these photographs. I do not need editing, video '
    'or sound. Keep the same source, publication and separate-save restrictions.')
REQUEST_MIXED = ('Browse, rate and select the photographs, adjust exposure and crop, and review the '
    'short video with audio. If audio becomes unavailable, continue the visual work silently. '
    'Never modify sources or publish. Save selected ratings and preview parameters only after separate confirmation.')
REQUEST_SPEECH = ('Browse, rate and select the photographs and review the video to check speech '
    'intelligibility. Audio is essential: without it pause the speech review. Never modify sources '
    'or publish. Save only after separate confirmation.')


def require(value, reason):
    if not value:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def digest(value):
    return hashlib.sha256(value if type(value) is bytes else canonical(value)).hexdigest()


def identity(kind, value):
    return 'ews:' + kind + ':' + digest(value)


def exact(value, keys, reason='closed_keys'):
    require(type(value) is dict and set(value) == set(keys), reason)


def command(value, allowed):
    exact(value, ('op', 'value'))
    op, v = value['op'], value['value']
    require(type(op) is str and op in allowed, 'operation_not_allowed')
    if op in ('OPEN', 'NEXT', 'PREVIOUS', 'REQUEST_SAVE', 'END', 'PLAY', 'PAUSE', 'REVIEW_MEDIA'):
        require(v is None, 'unexpected_command_value')
    elif op == 'RATE':
        require(type(v) is int and 0 <= v <= 5, 'rating_range')
    elif op == 'SELECT':
        require(type(v) is bool, 'selection_type')
    elif op == 'EXPOSURE':
        require(type(v) is int and -20 <= v <= 20, 'exposure_tenths_range')
    elif op == 'CROP':
        require(type(v) is str and v in ('ORIGINAL', 'SQUARE', 'WIDE'), 'crop_mode')
    elif op == 'SAVE':
        require(type(v) is str and v.startswith('ews:approval:'), 'separate_approval_required')
    elif op == 'SEEK':
        require(type(v) is int and 0 <= v <= 7, 'seek_seconds_range')
    else:
        raise ValueError('unknown_operation')
    return value
