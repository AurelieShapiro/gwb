import json
import shutil

from sepal_ui import sepalwidgets as sw 
import ipyvuetify as v

from component.message import cm
from component import parameter as cp
from component import widget as cw
from component import scripts as cs

class FragTile(sw.Tile):

    def __init__(self, io):
        
        # gather io 
        self.io = io 
        
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
        windows = cw.Windows(label = cm.frag.windows)
        options = v.Select(
            label = cm.acc.options,
            items= cp.fad_options,
            v_model = cp.fad_options[0]['value']
        )
        
        prescision = v.Select(
            label = cm.fad.prescision,
            items = cp.prescision,
            v_model = None
        )
        
        
        # bind to the io
        self.output = sw.Alert() \
            .bind(connectivity, self.io, 'connectivity') \
            .bind(res, self.io, 'res') \
            .bind(windows.save, self.io, 'window_size') \
            .bind(options, self.io, 'options') \
            .bind(prescision, self.io, 'prescision')
        
        # create the btn 
        btn = sw.Btn(cm.process.btn.format(io.process))
        
        super().__init__(
            self.io.tile_id,
            "Run Process",
            inputs = [
                connectivity,
                res,
                windows,
                options,
                prescision
            ],
            output = self.output,
            btn = btn
        )
        
        # link js behaviours
        btn.on_event('click', self._on_click)
        
    def _on_click(self, widget, event, data):
        
        # silence the btn
        widget.toggle_loading()
        
        # check inputs 
        if not self.output.check_input(self.io.connectivity, cm.acc.no_connex): return widget.toggle_loading()
        if not self.output.check_input(self.io.res, cm.acc.no_res): return widget.toggle_loading()
        if not self.output.check_input(len(json.loads(self.io.window_size)) or None, cm.frag.no_windows): return widget.toggle_loading()
        if not self.output.check_input(self.io.options, cm.acc.no_options): return widget.toggle_loading()
        if not self.output.check_input(self.io.prescision, cm.fad.no_prescision): return widget.toggle_loading()
        if not self.output.check_input(self.io.bin_map, cm.bin.no_bin): return widget.toggle_loading()
        
        try:
            
            # update the params list 
            self.io.update_params_list()
        
            # compute acc process 
            files = cs.run_gwb_process(
                process = self.io.process, 
                raster = self.io.bin_map, 
                params_list = self.io.params_list, 
                title = self.io.get_params_list(), 
                output = self.output,
                offset = self.io.offset
            )
            
            # add the files to the download links
            
        except Exception as e:
            self.output.add_live_msg(str(e), 'error')
        
        # remove the tmp directory 
        # whatever the result
        shutil.rmtree(cp.get_tmp_dir())
        
        # release the btn 
        widget.toggle_loading()
        
        return