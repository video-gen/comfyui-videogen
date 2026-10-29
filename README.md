# VideoGen for ComfyUI

Create product videos through the [VideoGen API](https://videogen.io/videogen-api), then connect the native `VIDEO` output to ComfyUI's Save Video or other video-processing nodes.

## Install

Requires a current ComfyUI release with the V3 node API. Clone this repository into `ComfyUI/custom_nodes/comfyui-videogen` and restart ComfyUI. No additional Python dependencies are installed by this node pack.

Set `VIDEOGEN_API_KEY` in the environment that launches ComfyUI. Create your key at https://app.videogen.io/api. Keys are never node widgets and do not enter shared workflow JSON.

## Nodes

1. **VideoGen: Start Storyboard Video** accepts two editable scene prompts. Starting requires `approve_credit_spend=true`; generation uses your VideoGen account credits. It requests portrait video, high quality, two remix actions and automatic MP4 export. Returns `workflow_run_id` immediately. A failed POST is not retried automatically.
2. **VideoGen: Wait for Video** polls that run, downloads its completed MP4 to `ComfyUI/output/videogen/` and returns native `VIDEO` plus the signed download URL. It checks ComfyUI cancellation between polls. Connect it to Save Video to preview/save the result.

If waiting times out, reuse the existing run id with the Wait node. Do not start a fresh workflow merely to resume polling. Shared workflow files must not include API keys, private run ids or signed download URLs.

## Validation

The HTTP client and credit guard are covered by offline mocked tests. Python compilation is checked. Full ComfyUI host execution and paid VideoGen generation have not been run for this initial release; those remain integration validation steps. No generated-media examples or claims of live execution are included.

[VideoGen](https://videogen.io/) · [Documentation](https://docs.videogen.io/) · [MCP setup](https://videogen.io/videogen-mcp)

MIT source. Maintained by VideoGen with AI assistance.
