"""VideoGen HTTP boundary. Credentials stay in the local ComfyUI environment."""
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


def request(path, body=None):
    key = os.environ.get('VIDEOGEN_API_KEY', '').strip()
    if not key:
        raise ValueError('Set VIDEOGEN_API_KEY in the environment running ComfyUI.')
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(
        'https://api.videogen.io' + path,
        data=data,
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json'},
        method='GET' if body is None else 'POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError('VideoGen request failed with HTTP ' + str(error.code)) from None


def start_storyboard(scene_prompts, approve_credit_spend):
    if not approve_credit_spend:
        raise ValueError('Approve credit spending before starting a VideoGen video.')
    if not scene_prompts or any(not prompt.strip() for prompt in scene_prompts):
        raise ValueError('Provide a non-empty prompt for each scene.')
    result = request('/v1/workflows/storyboard-to-video', {
        'scenes': [{'prompt': prompt} for prompt in scene_prompts],
        'aspectRatio': {'width': 9, 'height': 16},
        'quality': 'HIGH', 'autoExport': True,
        'remixActions': [{'type': 'ENABLE_CAPTIONS'}, {'type': 'CONVERT_IMAGES_TO_VIDEOS'}],
    })
    run_id = result.get('workflowRunId')
    if not isinstance(run_id, str) or not run_id:
        raise RuntimeError('Unexpected start response. Check existing runs before starting another video.')
    return run_id


def wait_for_export(run_id, timeout_seconds, check_interrupted):
    from urllib.parse import quote
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        check_interrupted()
        result = request('/v1/workflows/runs/' + quote(run_id, safe=''))
        status = result.get('status')
        if status in ('failed', 'cancelled'):
            raise RuntimeError('VideoGen workflow did not complete. Run: ' + run_id)
        if status == 'succeeded' and isinstance(result.get('downloadUrl'), str):
            return result['downloadUrl']
        time.sleep(5)
    raise TimeoutError('Resume the existing VideoGen run instead of creating another: ' + run_id)


def download_export(url, destination):
    if not url.startswith('https://'):
        raise ValueError('Expected a signed HTTPS download URL from VideoGen.')
    destination = Path(destination)
    temporary = destination.with_suffix('.part')
    with urllib.request.urlopen(url, timeout=120) as response, temporary.open('wb') as output:
        while chunk := response.read(1024 * 1024):
            output.write(chunk)
    temporary.replace(destination)
    return str(destination)
