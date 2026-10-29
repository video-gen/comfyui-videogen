"""VideoGen nodes for the ComfyUI V3 API."""
import hashlib
from pathlib import Path
from comfy_api.latest import ComfyExtension, InputImpl, io
from .client import download_export, start_storyboard, wait_for_export


class VideoGenStartStoryboard(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id='VideoGenStartStoryboard',
            display_name='VideoGen: Start Storyboard Video',
            category='VideoGen',
            inputs=[
                io.String.Input('scene_1', multiline=True, default='A reusable bottle on a clean kitchen counter in morning light.'),
                io.String.Input('scene_2', multiline=True, default='A hand placing the reusable bottle into a bag.'),
                io.Boolean.Input('approve_credit_spend', default=False),
            ],
            outputs=[io.String.Output('workflow_run_id')],
        )

    @classmethod
    def execute(cls, scene_1, scene_2, approve_credit_spend):
        import comfy.model_management
        comfy.model_management.throw_exception_if_processing_interrupted()
        run_id = start_storyboard([scene_1, scene_2], approve_credit_spend)
        return io.NodeOutput(run_id)


class VideoGenWaitForVideo(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id='VideoGenWaitForVideo',
            display_name='VideoGen: Wait for Video',
            category='VideoGen',
            inputs=[
                io.String.Input('workflow_run_id'),
                io.Int.Input('timeout_seconds', default=900, min=30, max=1800),
            ],
            outputs=[io.Video.Output('video'), io.String.Output('download_url')],
        )

    @classmethod
    def execute(cls, workflow_run_id, timeout_seconds):
        import comfy.model_management
        import folder_paths
        url = wait_for_export(
            workflow_run_id, timeout_seconds,
            comfy.model_management.throw_exception_if_processing_interrupted,
        )
        folder = Path(folder_paths.get_output_directory()) / 'videogen'
        folder.mkdir(parents=True, exist_ok=True)
        filename = hashlib.sha256(workflow_run_id.encode()).hexdigest() + '.mp4'
        path = download_export(url, folder / filename)
        return io.NodeOutput(InputImpl.VideoFromFile(path), url)


class VideoGenExtension(ComfyExtension):
    async def get_node_list(self):
        return [VideoGenStartStoryboard, VideoGenWaitForVideo]


async def comfy_entrypoint():
    return VideoGenExtension()
