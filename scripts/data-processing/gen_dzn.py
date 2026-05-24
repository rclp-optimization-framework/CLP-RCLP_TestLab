from pathlib import Path
from core.converter.core.data_loader import DataLoader
from core.converter.core.converter_engine import ConverterEngine
from core.converter.core.experiment_config import ExperimentConfig

ROOT = Path(__file__).resolve().parents[2]
input_folder=ROOT / "external" / "jits2022" / "Code" / "data" / "cork-1-line"
json_file=input_folder/"buses_input_20_0.json"
distances,n=DataLoader.load_distances(input_folder)
print("Loaded distances entries:", len(distances), "station_count:", n)
cfg=ExperimentConfig()
out=ROOT / "experiments" / "instances" / "generated" / "cork-1-line_battery-java20_0_generated.dzn"
out.parent.mkdir(parents=True, exist_ok=True)
success,msg=ConverterEngine.convert_json_to_dzn(json_file,out,variant_name="20_0",config=cfg,distances_dict=distances,output_format="java")
print(success, msg)
