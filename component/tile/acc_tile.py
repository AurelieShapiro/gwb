import json
import shutil

from sepal_ui import sepalwidgets as sw 
import ipyvuetify as v

from component.message import cm
from component import parameter as cp
from component import widget as cw
from component import scripts as cs

from .gwb_tile import GwbTile

class AccTile(GwbTile):

    def __init__(self, io): 
        
        # create the widgets
        connectivity = v.Select(
            label = cm.acc.connectivity,
            items = cp.connectivity,
            v_model = cp.connectivity[0]
        )
        res = v.TextField(
            label = cm.acc.res,
            type= 'number',
            v_model = None
        )
        thresholds = cw.Thresholds(label = cm.acc.thresholds)
        options = v.Select(
            label = cm.acc.options,
            items= cp.acc_options,
            v_model = cp.acc_options[0]['value']
        )
        
        
        # bind to the io
        self.output = sw.Alert() \
            .bind(connectivity, io, 'connectivity') \
            .bind(res, io, 'res') \
            .bind(thresholds.save, io, 'thresholds') \
            .bind(options, io, 'options')
        
        
        
        super().__init__(
            io = io, 
            output = self.output, 
            inputs = [
                connectivity,
                res,
                thresholds,
                options
            ]
        )
        
    def _on_click(self, widget, event, data):
        
        # silence the btn
        widget.toggle_loading()
        
        # check inputs 
        if not self.output.check_input(self.io.connectivity, cm.acc.no_connex): return widget.toggle_loading()
        if not self.output.check_input(self.io.res, cm.acc.no_res): return widget.toggle_loading()
        if not self.output.check_input(len(json.loads(self.io.thresholds)) or None, cm.acc.no_thres): return widget.toggle_loading()
        if not self.output.check_input(self.io.options, cm.acc.no_options): return widget.toggle_loading()
        if not self.output.check_input(self.io.bin_map, cm.bin.no_bin): return widget.toggle_loading()
        
        super()._on_click(widget, event, data)
        
        return