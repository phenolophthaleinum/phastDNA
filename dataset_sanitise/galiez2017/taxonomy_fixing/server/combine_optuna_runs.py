import argparse
import optuna
import os
import pathlib as pl
from glob import glob
import shutil



parser = argparse.ArgumentParser()
parser.add_argument("-i", help="paths to optuna studies - directory with .db files, or a file with paths to .db files (comma separated), or a comma separated list of paths to .db files")
parser.add_argument("-o", help="output file path for combined optuna studies")
args = parser.parse_args()

input = args.i
out = args.o


def parse_input(input: str) -> list:
    files = []
    print(pl.Path(input).resolve().is_dir())
    if pl.Path(input).resolve().is_dir():
        input: pl.Path = pl.Path(input).resolve().as_posix()
        
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
# make dir for out with pathlib
out = pl.Path(out).resolve()
out_dir = out.parent
out_file = out.name
print(out_dir)
print(out_file)
out_dir.mkdir(parents=True, exist_ok=True)
combined_study_path = out_dir / out_file
print(optuna_studies[0])
print(combined_study_path)
shutil.copy(optuna_studies[0], combined_study_path.as_posix())  
to_storage = f'sqlite:///{combined_study_path}'
# combined_study = optuna.create_study(storage=f'sqlite:///{out_dir}/{out_file}')
print(optuna_studies)
for study_path in optuna_studies[1:]:
    from_storage = f'sqlite:///{study_path}'
    study: optuna.Study = optuna.load_study(study_name=None, storage=from_storage)
    study_name = study.study_name
    optuna.copy_study(
        from_study_name=study_name,
        from_storage=from_storage,
        to_storage=to_storage
    )
    # study: optuna.Study = optuna.load_study(study_name=None, storage=f'sqlite:///{study_path}')


# for study in optuna_studies:
#     print(f'Combining {study}')
#     study = optuna.load_study(study, storage=f'sqlite:///{study}')
#     study_name = study.study_name
#     if not os.path.exists(out):
#         os.makedirs(out)
#     study.trials_dataframe().to_csv(f'{out}/{study_name}.csv', index=False)
#     print(f'Finished combining {study_name}')