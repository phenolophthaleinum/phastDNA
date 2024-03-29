import argparse
import optuna
import os
import pathlib as pl
from glob import glob



parser = argparse.ArgumentParser()
parser.add_argument("-i", help="paths to optuna studies")
parser.add_argument("-o", help="output file path for combined optuna studies")
args = parser.parse_args()

input = args.i
out = args.o


def parse_input(input: str) -> list:
    files = []
    print(pl.Path(input).absolute().is_dir())
    if pl.Path(input).absolute().is_dir():
        input: pl.Path = pl.Path(input).absolute().as_posix()
        
        # files.extend([str(file) for file in input.rglob('.db')])
        files.extend([str(file) for file in glob(f'{input}/**/*.db', recursive=True)])
    elif os.path.isfile(input):
        with open(input, 'r') as file:
            paths = file.readlines()
            paths = paths[0].strip().split(',')
        files.extend(paths)
    else:
        files.extend(input.split(','))
    return files

optuna_studies = parse_input(input)
print(optuna_studies)

# for study in optuna_studies:
#     print(f'Combining {study}')
#     study = optuna.load_study(study, storage=f'sqlite:///{study}')
#     study_name = study.study_name
#     if not os.path.exists(out):
#         os.makedirs(out)
#     study.trials_dataframe().to_csv(f'{out}/{study_name}.csv', index=False)
#     print(f'Finished combining {study_name}')