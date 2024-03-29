import argparse
import optuna
import os


parser = argparse.ArgumentParser()
parser.add_argument("-i", help="paths to optuna studies")
parser.add_argument("-o", help="output file path for combined optuna studies")
args = parser.parse_args()

input = args.i
out = args.o


def parse_input(input: str) -> list:
    files = []
    if os.path.isdir(input):
        for root, dirs, files in os.walk(input):
            for file in files:
                if file.endswith('.db'):
                    studies.append(os.path.join(root, file))
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