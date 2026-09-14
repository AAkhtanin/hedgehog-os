"""Three distinct semantic duties, before any service activation."""
from . import contracts_v01 as c

ROLES = ('ephemeral_workspace_orchestrator_llm', 'ephemeral_workspace_semantic_architect_llm',
         'ephemeral_workspace_privacy_boundary_reviewer_llm')
SCHEMAS = (
    {'needs': 'array of browse, rate, select, exposure, crop; only requested needs',
     'uncertainty': 'array of blocking questions, empty only if unambiguous'},
    {'preview': 'fit or contain', 'cleanup': 'on_end or on_end_and_idle',
     'save': 'selected_only', 'phases': ['preview', 'interact', 'confirm_save', 'close']},
    {'decision': 'allow or block', 'minimize': 'preview_only or preview_without_metadata',
     'conflicts': 'array of actual blocking conflicts'})


def schema(role, context):
    shape=dict(SCHEMAS[ROLES.index(role)])
    if context.get('version')==c.MIXED_VERSION:
        if role==ROLES[0]:
            shape['needs']='array of browse, rate, select, exposure, crop, video, audio, speech_review; only requested needs; audio requires video; speech_review requires audio'
        elif role==ROLES[1] and 'video' in context['bsep']['needs']:
            shape['audio_policy']='REQUIRE_AUDIO only for speech_review; otherwise SILENT_CONTINUE'
    return shape


def validate(role, value, context):
    index = ROLES.index(role)
    mixed=context.get('version')==c.MIXED_VERSION
    video=mixed and 'video' in context.get('bsep',{}).get('needs',[])
    shape=list(schema(role,context))
    c.exact(value, shape, 'semantic_closed_shape')
    if index == 0:
        needs = value['needs']
        c.require(type(needs) is list and all(type(v) is str for v in needs)
            and len(set(needs)) == len(needs) and set(needs) <= ({'browse','rate','select','exposure','crop'} |
                ({'video','audio','speech_review'} if mixed else set()))
            and 'browse' in needs, 'semantic_needs')
        c.require(('audio' not in needs or 'video' in needs) and ('speech_review' not in needs or 'audio' in needs),
            'semantic_media_dependencies')
        c.require(type(value['uncertainty']) is list and not value['uncertainty'], 'semantic_clarification_required')
    elif index == 1:
        c.require(value['preview'] in ('fit','contain') and value['cleanup'] in ('on_end','on_end_and_idle')
            and value['save'] == 'selected_only' and value['phases'] == SCHEMAS[1]['phases'], 'semantic_obligations')
        c.require('bsep' in context and 'route_acceptance' in context, 'architect_requires_accepted_bsep')
        if video:
            c.require(value['audio_policy'] in ('SILENT_CONTINUE','REQUIRE_AUDIO'), 'semantic_audio_policy')
            c.require(('speech_review' in context['bsep']['needs'])==(value['audio_policy']=='REQUIRE_AUDIO'),
                'semantic_goal_audio_conflict')
    else:
        c.require(value['decision'] in ('allow','block') and value['minimize'] in
            ('preview_only','preview_without_metadata') and type(value['conflicts']) is list
            and all(type(v) is str for v in value['conflicts']), 'privacy_shape')
        c.require(value['decision'] == 'allow' and not value['conflicts'], 'privacy_refusal')
    return value


class ControlledProvider:
    mode = 'CONTROLLED_DETERMINISTIC'
    model = 'local-semantic-rules-v01'

    def respond(self, role, context):
        if role == ROLES[0]:
            text = context['request'].lower()
            if 'better' in text and not any(v in text for v in ('rate','select','exposure','crop')):
                return dict(needs=['browse'],uncertainty=['Should this workspace only rate and select photos, or also allow manual exposure and crop previews?'])
            edits = not ('do not need editing' in text)
            needs=['browse','rate','select'] + (['exposure','crop'] if edits else [])
            if context.get('version')==c.MIXED_VERSION and not ('video or sound' in text or 'editing, video' in text):
                if 'video' in text:
                    needs+=['video']
                if 'audio' in text or 'speech' in text:
                    needs+=['audio']
                if 'speech intelligibility' in text:
                    needs+=['speech_review']
            return dict(needs=needs, uncertainty=[])
        if role == ROLES[1]:
            result=dict(preview='fit', cleanup='on_end', save='selected_only', phases=list(SCHEMAS[1]['phases']))
            if 'video' in context['bsep']['needs']:
                result['audio_policy']='REQUIRE_AUDIO' if 'speech_review' in context['bsep']['needs'] else 'SILENT_CONTINUE'
            return result
        return dict(decision='allow', minimize='preview_without_metadata', conflicts=[])


def compile_contract(responses):
    needs = responses[0]['needs']
    commands = ['NEXT','PREVIOUS']
    commands += [op for key, op in [('rate','RATE'),('select','SELECT'),('exposure','EXPOSURE'),('crop','CROP')] if key in needs]
    result=dict(version=c.VERSION, commands=sorted(commands), active_classes=list(c.CLASSES[:4]),
        dormant_classes=list(c.CLASSES[4:]), preview=responses[1]['preview'], cleanup=responses[1]['cleanup'],
        minimize=responses[2]['minimize'], save='selected_only', source_write=False, publication=False)
    if 'video' in needs:
        result.update(version=c.MIXED_VERSION,commands=sorted(commands+['PLAY','PAUSE','SEEK','REVIEW_MEDIA']),
            media=dict(video=True,audio='audio' in needs,speech_review='speech_review' in needs,audio_policy=responses[1]['audio_policy']))
        if 'audio' in needs:
            result['active_classes'].append('AudioSinkNeedle')
            result['dormant_classes'].remove('AudioSinkNeedle')
    return result
