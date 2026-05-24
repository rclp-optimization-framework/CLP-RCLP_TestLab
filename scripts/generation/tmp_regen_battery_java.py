from pathlib import Path
from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.experiment_config import ExperimentConfig

ROOT = Path(__file__).resolve().parents[2]
jits_path = ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'cork-1-line'
json_file = jits_path / 'buses_input_20_0.json'
output_dir = ROOT / 'experiments' / 'instances' / 'battery-java'
config_file = ROOT / 'external' / 'jits2022' / 'Code' / 'data' / 'experiment_parameters_cork1_20_0.txt'
config = ExperimentConfig(config_file=config_file) if config_file.exists() else ExperimentConfig()
print('Using config:', config.cmax, config.cmin, config.charging_rate)

success_count, failure_count, messages = ConverterEngine.batch_convert_files([json_file], output_dir, source_dir_name='cork-1-line', config=config, distances_dict=None, output_format='java')
print('Success:', success_count, 'Fail:', failure_count)
for m in messages:
    print(m)
