from ryu.base import app_manager
from ryu.app.wsgi import WSGIApplication, route
from ryu.controller import dpset
from ryu.lib import hub
import json

class SliceAPI(app_manager.RyuApp):
    _CONTEXTS = {"wsgi": WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SliceAPI, self).__init__(*args, **kwargs)
        wsgi = kwargs["wsgi"]
        wsgi.register(SliceAPIController, {"app": self})

    def set_slice(self, slice_type):
        # Set the slice in the controller logic
        if slice_type in ["normal", "simulation"]:
            self.current_slice = slice_type
            self.logger.info(f"Switched to {slice_type} slice.")
        else:
            self.logger.warning("Invalid slice type.")

class SliceAPIController:
    def __init__(self, req, link, data, **config):
        self.app = data["app"]

    @route("slice", "/slice", methods=["POST"])
    def change_slice(self, req, **kwargs):
        try:
            data = json.loads(req.body)
            slice_type = data.get("slice")
            self.app.set_slice(slice_type)
            return Response(status=200)
        except Exception as e:
            return Response(status=500, body=str(e))

