import argparse
import subprocess


parser = argparse.ArgumentParser()
parser.add_argument("-s", help="slurm script")
parser.add_argument("--taxfile", help="file with the taxnames")
parser.add_argument("--output", help="master output dir")
args = parser.parse_args()

filename = args.taxfile
out = args.output
script = args.s

with open(filename, 'r') as file:
    data = file.readlines()
    data = data[0].strip().split(',')

for tax in data:
    subprocess.run(['sbatch', script, tax, out])

# cp --parents ./*/*.xlsx all_reports - copies files of given types with dirs to a new dir