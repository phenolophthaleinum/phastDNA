import functools
import inspect
import json
import pickle
import random
import sys
import os
import psutil
import mmap
from loguru import logger
from collections import Counter
from functools import wraps
from itertools import chain
from multiprocessing import cpu_count
from pathlib import Path
from timeit import default_timer as timer
from datetime import timedelta
from traceback import format_tb
from typing import Any, Callable, Collection, Dict, List, Type

import joblib
import numpy as np
from pyfastx import Fasta

# DEFAULTS
default_threads = max(cpu_count() - 1, 1)
fastDNA_exe = Path('./fastDNA/fastdna')
fasta_extensions = ('.fna', '.faa', '.fnn', '.fas', '.fa', '.fasta')


class Loger:
    """
    I really hate "logging module"
    """

    def __init__(self):
        self.log_path = None
        self.log_file = None
        self.total = None
        self.done = None
        self.tile = None

    def __repr__(self):
        return f'Log at: {self.log_path.as_posix()}'

    def file(self, path: Path):
        # assert path is None or not path.is_file(), f'Logfile at {path.as_posix()} EXISTS!'
        self.log_path = path
        self.log_file = self.log_path.open('a') if self.log_path else None

    def _record(self,
                msg: str,
                newline: bool = True):

        assert self.log_path and self.log_file, f'No log file connected!' \
                                                f'\n{msg}'
        end = '\n' if newline else ''
        print(msg, end=end, flush=True)
        if self.log_file:
            self.log_file.write(msg + end)
            self.log_file.flush()

    def info(self, msg):
        self._record(f'\n{msg}\n')

    def warn(self, msg):
        self._record(f'\nWARNING:{msg}\n')

    def exception(self,
                  msg,
                  exc_type: Type[Exception]):
        if self.log_file:
            self.log_file.write(f'Traceback'
                                f'\n{exc_type.__name__}'
                                f'\n\n{msg}')
            self.log_file.flush()
        raise exc_type(msg)

    def catch(self,
              exc_type,
              exc_value,
              exc_traceback):
        formattrd_traceback = '\n'.join(format_tb(exc_traceback))
        msg = f'\nTraceback' \
              f'\n{exc_type.__name__}' \
              f'\n\n{exc_value}' \
              f'\n\n{formattrd_traceback}'

        self._record(msg)

    def close(self):
        self._record('finished')
        if self.log_file:
            self.log_file.close()

    def set_task(self, msg, total):
        self._record(f'\n{msg}')
        if type(total) in (list, tuple, dict):
            total = len(total)
        self.total = total
        self.tile = max(int(total / 50), 1)
        self.done = 0

    def update(self,
               current: int = None):
        if current is None:
            current = self.done + 1
        new_tiles = int(current / self.tile) - int(self.done / self.tile)
        if new_tiles:
            # self._record('#' * new_tiles, newline=False)
            self._record(f'{self.done}/{self.total}')
        self.done = current
        if self.done == self.total:
            self.set_task('\ndone\n', 0)


log = Loger()  # initialize main log object
# sys.excepthook = log.catch



# PARALLELIZATION
class Parallel(joblib.Parallel):
    """
    The modification of joblib.Parallel
    with a TQDM proigress bar
    according to Nth
    (https://stackoverflow.com/questions/37804279/how-can-we-use-tqdm-in-a-parallel-execution-with-joblib)
    """

    def __init__(self,
                 parallelized_function: Callable,
                 input_collection: Collection,
                 kwargs: Dict = None,
                 n_jobs: int = None,
                 backend=None,
                 description: str = None,
                 verbose=0,
                 timeout=None,
                 pre_dispatch='2 * n_jobs',
                 batch_size='auto',
                 temp_folder=None, max_nbytes='1M', mmap_mode='r',
                 prefer=None,
                 require=None):
        if description is None:
            description = parallelized_function.__name__
        if not n_jobs:
            n_jobs = default_threads
        joblib.Parallel.__init__(self, n_jobs, backend, verbose, timeout,
                                 pre_dispatch, batch_size, temp_folder,
                                 max_nbytes, mmap_mode, prefer, require)
        kwargs = {} if not kwargs else kwargs
        # log.set_task(description, input_collection)
        logger.info(description)
        self.pinstance = psutil.Process(os.getpid())
        self.total_task = len(input_collection)
        self.log_update = max(1, int(self.total_task * 0.05))
        self.result = self.__call__((joblib.delayed(parallelized_function)(e, **kwargs)) for e in input_collection)

    def print_progress(self):
        # log.update(self.n_completed_tasks)
        if self.n_completed_tasks % self.log_update == 0:
            memory_info = self.pinstance.memory_info()
            logger.info(f"Debug for {self.n_completed_tasks}/{self.total_task} ; RSS: {memory_info.rss / 1024 / 1024} MB; VMS: {memory_info.vms / 1024 / 1024} MB")
            logger.info(f'Progress: {self.n_completed_tasks}/{self.total_task}')
        if self.n_completed_tasks == self.total_task:
            logger.info('Done!')


class BatchParallel(Parallel):
    """

    """

    def __init__(self,
                 parallelized_function: Callable,
                 input_collection: Collection,
                 partitions: int = None,
                 kwargs: Dict = {},
                 n_jobs=default_threads,
                 backend=None,
                 description: str = None,
                 verbose=0,
                 timeout=None,
                 pre_dispatch='2 * n_jobs',
                 batch_size='auto',
                 temp_folder=None, max_nbytes='1M', mmap_mode='r',
                 prefer=None,
                 require=None):
        if description is None:
            description = parallelized_function.__name__

        def wrapper_function(batch):
            return tuple([parallelized_function(element, **kwargs) for element in batch])

        if partitions is None:
            partitions = n_jobs * 3
        batches = np.array_split(np.array(input_collection), partitions)

        Parallel.__init__(self,
                          parallelized_function=wrapper_function,
                          input_collection=batches,
                          n_jobs=n_jobs,
                          backend=backend,
                          verbose=verbose,
                          timeout=timeout,
                          pre_dispatch=pre_dispatch,
                          batch_size=batch_size,
                          temp_folder=temp_folder,
                          max_nbytes=max_nbytes,
                          mmap_mode=mmap_mode,
                          prefer=prefer,
                          require=require,
                          description=description)
        self.result = tuple(chain.from_iterable(self.result))


def format_time(time_delta: float):
    """
    Formats timedelta object to easily readable time string.
    """
    total_secs = timedelta(seconds=time_delta).total_seconds()
    hours, remainder = divmod(total_secs, 3600)
    mins, secs = divmod(remainder, 60)

    return f"{int(hours)}h {int(mins)}m {secs:.4f}s"


# LOGGING
def time_this(func):
    """
    Decorator which returns information about execution of decorated function.
    """

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start = timer()
        values = func(*args, **kwargs)
        end = timer()
        runtime = end - start
        if values is None:
            print(f"{func.__name__!r} execution error")
        else:
            # print(f"{func.__name__!r} executed successfully in {runtime:.6f} seconds")
            logger.info(f"{func.__name__!r} executed successfully in {format_time(runtime)}")
            return values

    return wrapper_timer

# start = timer()
# t.sleep(1.2)
# end = timer()
# runtime = end - start
# formatted_runtime = datetime.timedelta(seconds=runtime)
# formatted_runtime = datetime.time.fromisoformat(str(datetime.timedelta(seconds=runtime)))
# datetime.time(formatted_runtime)

# FILE HANDLING
def make_tax_json(host_data: Dict[str, Dict[str, Any]]):
    """ todo
    :param host_data:
    :return:
    """
    keys = list(host_data.keys())
    for key in keys:
        taxid = host_data[key]["taxid"]
        host_data[key]["ncbi_id"] = host_data[key].pop("taxid")
        host_data[key]["ncbi_id"] = key
        host_data[taxid] = host_data.pop(key)
    with open("tax.json", "w") as fh:
        json.dump(host_data, fh, indent=4)


def fasta_2_dict(fasta_path: Path) -> Dict[str, str]:
    """ todo
    :param fasta_path:
    :return:
    """
    reader = Fasta(fasta_path.as_posix())
    # following only for debug
    d = {}
    for seq in reader:
        if len(seq) > 50_000:
            d[seq.description] = seq.seq.upper()
        else:
            logger.info(f"Ommited file:{fasta_path.stem} ({len(seq)}bp). Sequence ID: {seq.id}")
    return d
    # return {seq.id: seq.seq.upper() for seq in reader if len(seq) > 2000}


def sanitize_names(metadata_dict: Dict[str, Dict[str, Any]],
                   virus: bool = False):
    offending_characters = '[]{}()!"\'#&%^/\\|'
    for record, metadata in metadata_dict.items():
        bacterium_dict = metadata['host'] if virus else metadata
        sanitized_field, field_index = {rank: (name, i) for i, (rank, name) in enumerate(zip(bacterium_dict['lineage_ranks'], bacterium_dict['lineage_names']))}['species']
        print(sanitized_field)        
        for c in offending_characters:
            sanitized_field = sanitized_field.replace(c, '')
        bacterium_dict['lineage_names'][field_index] = sanitized_field
    return metadata_dict


def reverse_complement(seq):
    """ todo

    :param seq:
    :return:
    """
    d = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    return "".join([d.get(nt, 'N') for nt in seq[::-1]])


def sample_genome(sequences: Dict[str, str],
                  window: int,
                  n: int,
                  max_ambiguities: float) -> Dict[str, str]:
    """Function reads each given fasta file, randomly samples n subsequences of a defined length, creates new records with those subsequences and puts these new records into a list (which is finally returned).

    Args:
        :param sequences: todo
        :param window: Length of a sampled subsequence
        :param n: Number of subsequences to be sampled
        :param max_ambiguities: Ambiguous nucleotide content threshold in sampled sequences (in percents)

    Returns:
        list[SeqRecord]: Returns list of newly created biopython `SeqRecord`, each contains sampled subsequences.

    """
    seq_lengths = {seq_id: len(seq) for seq_id, seq in sequences.items()}
    seq_ids, lengths = list(seq_lengths.keys()), list(seq_lengths.values())

    filtered_sample = {}

    while n:
        contig_targets = Counter(random.choices(seq_ids, weights=lengths, k=n)) if len(sequences) > 1 else Counter(seq_ids * n)
        effective_lengths = {seq_id: slen - window for seq_id, slen in seq_lengths.items()}
        for contig_id, c in contig_targets.items():
            template, ef_len = sequences[contig_id], effective_lengths[contig_id]
            starts = [random.randint(0, ef_len) for _ in range(c)]
            subsequences = {f'{contig_id}__{s}_{s + window}': template[s:s + window] for s in starts}
            filtered_subsequences = {}
            for subseq_id, subseq in subsequences.items():
                n_content = subseq.count("n")  # todo CASE?
                if n_content / window <= max_ambiguities:
                    if bool(random.getrandbits(1)):
                        filtered_subsequences[f'{subseq_id}_r'] = reverse_complement(subseq)
                    else:
                        filtered_subsequences[subseq_id] = subseq
                else:
                    print(f"Too high N content ({n_content / window}%). Sampling again")
            n -= len(filtered_subsequences)
            filtered_sample.update(filtered_subsequences)

    return filtered_sample


def sample_fasta(file: Path,
                 length: int,
                 n: int,
                 max_ambiguities: float,
                 to_dir: Path = None):
    """ todo

    :param file:
    :param length:
    :param n:
    :param max_ambiguities:
    :param to_dir:
    :return:
    """
    output = sample_genome(fasta_2_dict(file), length, n, max_ambiguities)
    if to_dir:
        out_file = to_dir.joinpath(file.name)
        with out_file.open('w') as out:
            out.write('\n'.join([f'>{definition}\n{sequence}' for definition, sequence in output.items()]))
        return out_file
    return output


def sample_fasta_dir(fasta_dir: Path,
                     length: int,
                     n_samples: int,
                     max_ambiguities: float = 0.1,
                     to_dir: Path = None,
                     n_jobs: int = None,
                     overwrite: bool = False):
    """ todo
    :param fasta_dir:
    :param length:
    :param n_samples:
    :param max_ambiguities:
    :param to_dir:
    :param n_jobs:
    :param overwrite:
    :return:
    """
    if to_dir.is_dir() and not overwrite:
        fasta_files = [f for f in to_dir.iterdir() if f.suffix in fasta_extensions]
        if fasta_files:
            print(f'Sampled sequences found at:'
                  f'\n{to_dir.as_posix()}'
                  f'\nreading existing files', flush=True)
            return fasta_files
        else:
            raise FileNotFoundError(f'Sample directory found at {to_dir.as_posix()}'
                                    f'\nbut no fasta-formatted sequences coud be identified inside')
    else:
        to_dir.mkdir(parents=True)
        fasta_files = [f for f in fasta_dir.iterdir() if f.suffix in fasta_extensions]
        jobs = BatchParallel(sample_fasta, fasta_files,
                             kwargs={'length': length,
                                     'n': n_samples,
                                     'max_ambiguities': max_ambiguities,
                                     'to_dir': to_dir},
                             description=f'Sampling sequences from {fasta_dir.as_posix()} in progress.',
                             n_jobs=n_jobs)
        return [sample for sample in jobs.result]


def labeled_fasta(files: List[Path],
                  labels: List[str],
                  path_stem: Path,
                  n_jobs: int = None):
    assert len(files) == len(labels), f'Sample file list:' \
                                      f'\n{files[:3]} ({len(files)})' \
                                      f'\nDoes NOT match label list:\n{labels[:3]} ({len(labels)})'
    fasta_lines, label_lines = [], []
    read_jobs = Parallel(fasta_2_dict, files,
                         description=f'EVENT: Labelling {len(files)} training genomes form {len(set(labels))} taxa [2]',
                         n_jobs=n_jobs)
    pinstance = psutil.Process(os.getpid())
    memory_info = pinstance.memory_info()
    out_fasta, out_labels = path_stem.parent.joinpath(f'{path_stem.name}.fasta'), path_stem.parent.joinpath(f'{path_stem.name}.labels')
    written_files = 0
    with out_fasta.open('a') as fs:
        for seq_dict, label in zip(read_jobs.result, labels):
            logger.info(f"SeqDict: {seq_dict.keys()} / Label: {label}")
            fasta_lines = [f'>{definition}\n{seq}' for definition, seq in seq_dict.items()]
            # logger.info(fasta_lines)
            # fs.write('\n'.join(fasta_lines))
            newline_char = '\n'
            fs.write(f'{newline_char.join(fasta_lines)}\n')
            label_lines.extend([label for _ in seq_dict])
            written_files += len(seq_dict)
            logger.info(f"Written {written_files} sequences from {len(files)} sequences")
            # logger.info(f'RSS: {memory_info.rss / 1024 / 1024} MB; VMS: {memory_info.vms / 1024 / 1024} MB')

    # out_fasta_obj = out_fasta.open('a')
    # out_fasta_obj.write("\n")
    # out_fasta_obj.close()
    # with out_fasta.open('r+b') as fs:
    #     mmapped_file = mmap.mmap(fs.fileno(), 0)
    #     for seq_dict, label in zip(read_jobs.result, labels):
    #         fasta_lines = [f'>{definition}\n{seq}' for definition, seq in seq_dict.items()]
    #         label_lines.extend([label for _ in seq_dict])
    #         mmapped_file.write('\n'.join(fasta_lines).encode())
            # logger.info(f'RSS: {memory_info.rss / 1024 / 1024} MB; VMS: {memory_info.vms / 1024 / 1024} MB')

    # for seq_dict, label in zip(read_jobs.result, labels):
    #     fasta_lines.extend([f'>{definition}\n{seq}' for definition, seq in seq_dict.items()])
    #     label_lines.extend([label for _ in seq_dict])
    #     logger.info(f'RSS: {memory_info.rss / 1024 / 1024} MB; VMS: {memory_info.vms / 1024 / 1024} MB')
    # out_fasta, out_labels = path_stem.parent.joinpath(f'{path_stem.name}.fasta'), path_stem.parent.joinpath(f'{path_stem.name}.labels')
    # with out_fasta.open('w') as fs:
    #     fs.write('\n'.join(fasta_lines))
    with out_labels.open('w') as ls:
        ls.write('\n'.join(label_lines))
    return out_fasta, out_labels


def flatten(d: dict):
    flat_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            flat_dict.update(flatten(v))
        elif k == 'target':
            flat_dict[k] = float(v)
        else:
            try:
                flat_dict[k] = int(v)
            except ValueError:
                flat_dict[k] = v
    return flat_dict


def serialize(picklable_object: object,
              path: Path):
    with path.open('wb'):
        joblib.dump(picklable_object,
                    path.as_posix())


def read_serialized(path: Path):
    with path.open('rb'):
        loaded_object = joblib.load(path.as_posix())
    return loaded_object


def checkpoint(funct: callable):
    """
    Simple serialization decorator
    that saves function result
    if exacted output file don't exist or is empty
    or read it if it is non-empty
    @param funct: function to wrap
    @param pickle_path: a path to an output file
    @param serialization_method: a module used for serialization (either joblib or pickle)
    @return:
    """

    signature = inspect.signature(funct)

    @wraps(funct)
    def save_checkpoint(*args, **kwargs):

        bound_args = signature.bind(*args, **kwargs)
        pickle_path = Path(bound_args.arguments.get('pickle_path',
                                                    signature.parameters['pickle_path'].default))
        print(f'\nrunning {funct.__name__}', flush=True)
        if pickle_path:
            try:
                with pickle_path.open('rb') as file_object:
                    result = pickle.load(file_object)
                print(f'\ntemporary file read from: {pickle_path.as_posix()}\n', flush=True)
                return result
            except (FileNotFoundError, IOError, EOFError):
                sys.setrecursionlimit(5000)
                result = funct(*args, **kwargs)
                with pickle_path.open('wb') as out:
                    pickle.dump(result, out)
                print(f'\ntemporary file stored at: {pickle_path.as_posix()}\n', flush=True)
                return result
