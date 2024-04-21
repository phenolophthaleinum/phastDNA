import argparse
import os
import pathlib as pl
from glob import glob
import shutil
import typing


def report_both(study1, study2):
    pass


def report_study(study):
    pass

parser = argparse.ArgumentParser()
parser.add_argument("-i1", help="path to first optuna study")
parser.add_argument("-i2", help="path to second optuna study")
parser.add_argument("-o", help="output file path for comparison report")
args = parser.parse_args()

input1 = args.i1
input2 = args.i2
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
input2_summaries: typing.List[optuna.study.StudySummary] = optuna.study.get_all_study_summaries(f'sqlite:///{input2}')
studies_dicts1 = [summary.__dict__["study_name"] for summary in input1_summaries]
studies_dicts2 = [summary.__dict__["study_name"] for summary in input2_summaries]
# studies_names = [summary_dict["study_name"] for summary_dict in studies_dicts]
# print(*studies_dicts, sep='\n=====================\n')
all_studies = sorted(set(studies_dicts1 + studies_dicts2))
for study_name in all_studies:
    if study_name in studies_dicts1 and study_name in studies_dicts2:
        try:
            study1 = optuna.load_study(study_name=study_name, storage=f'sqlite:///{input1}')
            study2 = optuna.load_study(study_name=study_name, storage=f'sqlite:///{input2}')
        except Exception as e:
            print(f"Failed to load study {study_name}")
            print(e)
            continue
        print(f"Study Name: {study_name}")
        print("Best Parameters:")
        print(f" DB1: {study1.best_params}")
        print(f" DB2: {study2.best_params}")
        
        # Compare best values
        change = study2.best_value - study1.best_value
        print("Best Values:")
        print(f" DB1: {study1.best_value}")
        print(f" DB2: {study2.best_value} | {change}")
        print("-----------------------------")
        # print(study.trials[0].distributions)
        continue
    elif study_name in studies_dicts1:
        try:
            study1 = optuna.load_study(study_name=study_name, storage=f'sqlite:///{input1}')
            print(f"Study Name: {study_name}")
            print("Best Parameters:")
            print(f" DB1: {study1.best_params}")
            print("Best Values:")
            print(f" DB1: {study1.best_value}")
            print("-----------------------------")
        except Exception as e:
            print(f"Failed to load study {study_name} from {input1}")
            print(e)
    elif study_name in studies_dicts2:
        try:
            study2 = optuna.load_study(study_name=study_name, storage=f'sqlite:///{input2}')
            print(f"Study Name: {study_name}")
            print("Best Parameters:")
            print(f" DB2: {study2.best_params}")
            print("Best Values:")
            print(f" DB2: {study2.best_value}")
            print("-----------------------------")
        except Exception as e:
            print(f"Failed to load study {study_name} from {input2}")
            print(e)

exit()
study1 = optuna.load_study(study_name=studies_dicts[-1], storage=f'sqlite:///{input1}')
# study2 = optuna.load_study(study_name=None, storage=f'sqlite:///{input2}')
print(study1.best_params)
print(study1.trials[0].distributions)
import pandas
df = study1.trials_dataframe()
print(study1.trials[0].distributions)
print(df)
print(df.columns)
# print(study2.best_params)