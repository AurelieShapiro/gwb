import shutil
import subprocess
from pathlib import Path

import ipyvuetify as v

from component.message import cm
from component import parameter as cp

def run_gwb_process(process, raster, params_list, title, output, offset):
    """
    run all the processes of the GWB suit according to the io
    The input and output folder will be created on the fly and deleted right afterward
    The result will be saved in the result_dir of the parameter component
    The log will be displayed to the end user and then removed
    
    Args: 
        io (GWBIo): any io inheriting from the GWBIo object
        
    Return:
        (pathlib.Path) : the path to the final .image
        (pathlib.Path) : the path to the final .csv
    """
    
    # create the tmp directories 
    tmp_dir = cp.get_tmp_dir()
    in_dir = tmp_dir.joinpath('input')
    in_dir.mkdir()
    out_dir = tmp_dir.joinpath('output')
    out_dir.mkdir()
    
    # fill the tmp dir with the raster 
    shutil.copy(raster, in_dir)
    
    # create the input file
    parameter_file = in_dir.joinpath(f'{process}-parameters.txt')
    with parameter_file.open('w') as f:
        offset_lines = ['\n' for i in range(offset-1)]
        params_lines = [str(p) + '\n' for p in params_list]
        finish_lines = ['\n']
        f.writelines(offset_lines + params_lines +finish_lines)
            
    # create the command 
    command = [
        f'GWB_{process.upper()}',
        f'-i={in_dir}',
        f'-o={out_dir}'
    ]
    
    # set the argument of the process
    kwargs = {
        'args' : command,
        'cwd' : Path('~').expanduser(), # launch from home to avoid permissions bugs
        'stdout' : subprocess.PIPE,
        'stderr' : subprocess.PIPE,
        'universal_newlines' : True
    }
    
    # start the process 
    output.add_live_msg(cm.gwb.start.format(process.upper()))
    
    with subprocess.Popen(**kwargs) as p:
        for line in p.stdout:
            output.append_msg(line)
            
    # file in the output directory
    folder = cp.gwb[process]["folder"]
    if folder == '':
        out_log = list(out_dir.glob(f'*.log'))
        out_files = [f for f in out_dir.glob("*.*") if not f.stem == '.log']
    else:
        out_log = list(out_dir.glob(f'*.log'))
        out_files = next(out_dir.glob(f'{raster.stem}_{folder}*/')).glob('*.*') 
    
    
    # if log is not there, the comutation didn't even started 
    # I let the display in its current state and change the color of the output to red
    if len(out_log) == 0:
        output.type = 'error'
        return []
    
    # if the log file is the only file then it has crashed
    
    # read the log 
    with open(out_log[0]) as f:
        log = f.read()
        
    # copy the files in the result directory 
    files = []
    for f in out_files:
        final_f = shutil.copy(f, cp.get_result_dir(process))
        files.append(Path(final_f))
        
    # display the final log 
    output.add_live_msg(v.Html(tag='pre', class_='success--text d-inline', children=[log]), 'success')
    
    return files
        
    
    