import argparse
import os
import pathlib as pl
from glob import glob
import shutil
import typing


parser = argparse.ArgumentParser()
parser.add_argument("-i1", help="path to first optuna study")
# parser.add_argument("-i2", help="path to second optuna study")
parser.add_argument("-o", help="output file path for comparison report")
args = parser.parse_args()

input1 = args.i1
# input2 = args.i2
out = args.o

out = pl.Path(out).resolve()
input1 = pl.Path(input1).resolve().as_posix()
# input2 = pl.Path(input2).resolve().as_posix()
out_dir = out.parent
out_file = out.name
print(out_dir)
print(out_file)
out_dir.mkdir(parents=True, exist_ok=True)
report_path = out_dir / out_file

import optuna
input1_summaries: typing.List[optuna.study.StudySummary] = optuna.study.get_all_study_summaries(f'sqlite:///{input1}')
studies_dicts = [summary.__dict__ for summary in input1_summaries]
studies_names = [summary_dict["study_name"] for summary_dict in studies_dicts]
# print(*studies_dicts, sep='\n=====================\n')
study1 = optuna.load_study(study_name=studies_names[-1], storage=f'sqlite:///{input1}')
# study2 = optuna.load_study(study_name=None, storage=f'sqlite:///{input2}')
print(study1.best_params)
print(study1.trials[0].distributions)
import pandas
df = study1.trials_dataframe()
print(df)
# print(study2.best_params)