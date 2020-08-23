import os
import sys
from pathlib import Path

this_filepath = Path(os.path.realpath(__file__))
project_root = str(this_filepath.parents[0])

# add the DataSynthesizer repo to the pythonpath
data_synthesizer_dir = os.path.join(project_root, 'DataSynthesizer/')
sys.path.append(data_synthesizer_dir)

#full synth
data_dir = os.path.join(project_root, 'data/')
data_file = os.path.join(data_dir, 'data.csv')
json_file = os.path.join(data_dir, 'data.json')
synthetic_data_file = os.path.join(data_dir, 'synthetic_data.csv')

plot_dir = os.path.join(project_root, 'plot/')

#part synth
column_data_file = os.path.join(data_dir, 'data_column.csv')