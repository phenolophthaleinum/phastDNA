import json
import scoring
from collections import defaultdict, Counter
from copy import deepcopy
from itertools import count
from pathlib import Path
from shutil import rmtree
from subprocess import Popen, PIPE
from numpy import log10
from typing import Any, Dict, List, Tuple
from loguru import logger

import pandas as pd
from bayes_opt import BayesianOptimization

from scoring import score_and_rank
from taxonomy import sample_taxon, DistanceMatrix, TaxonomicEvaluation
from utils import (Parallel, default_threads,
                   sample_fasta_dir, labeled_fasta,
                   serialize, read_serialized,
                   fastDNA_exe, time_this,
                   log, sanitize_names)


class Classifier:
    """
    Complete phastDNA phage-host classifier
    fit to the training sets of host and virus fasta files.
    """

    def __init__(self,
                 working_dir: Path,
                 minn: int,
                 maxn: int,
                 labels: str = 'species',
                 lr: float = 0.1,
                 lr_update: float = 100,
                 dim: int = 100,
                 noise: int = 0,
                 frag_len: int = 200,
                 epoch: int = 20,
                 loss: str = 'softmax',
                 threads: int = default_threads,
                 considered_hosts: int = 10,
                 samples: int = 200,
                 fastdna_exe: Path = fastDNA_exe,
                 debug=False,
                 performance_metric: str = 'accordance'):
        """
        Initializer for the fastDNA-based phage-host classifier.

        :param working_dir: path to temporary directory used to store required fies
        :param minn: Minimum size of a k-mer to use during the training process.
        :param maxn: Maximum size of a k-mer to use during the training process
               (it is advised to be kept the same as `minn` and **less than 15, otherwise fastDNA fails**).
        :param epoch: Number of training epochs
               (each added epoch increases runtime significantly, but in most cases increases model quality).
        :param dim: Dimensionality of fastDNA the sequence embeddings.
        :param frag_len: Length of genome fragments to be used during the training process.
        :param considered_hosts:
        :param threads: Number of CPU threads to be used during training process
        :param samples:
        :param fastdna_exe: Path to fastDNA executable
        :param debug: is the classifier created for debugging purposes
                     (skips the cleanup of temporary files and writes additional vector file after fitting)
        """
        self.minn = minn
        self.maxn = maxn
        self.labels = labels
        self.lr = lr
        self.lr_update = lr_update
        self.dim = dim
        self.noise = noise
        self.frag_len = frag_len
        self.epochs = epoch
        self.loss = loss
        self.threads = threads
        self.samples = samples
        self.considered_hosts = considered_hosts
        self.dir = working_dir
        self.fastdna_exe = fastdna_exe
        self.dir.mkdir(parents=True)
        self.model = None
        self.scoring = None
        self.ranking = None
        self.performance = 0
        self.debug = debug
        self.metric = performance_metric
        self.name = f'model.n{self.minn}-{self.maxn}.' \
                    f'lr{self.lr:.5f}-{self.lr_update:.5f}.' \
                    f'd{self.dim}.no{self.noise}.' \
                    f'fl{self.frag_len}.e{self.epochs}.' \
                    f'lo{self.loss}.sa{samples}'

    def fit(self,
            training_host_fasta: Path,
            training_host_labels: Path,
            host_matrix: DistanceMatrix,
            virus_samples: List[Path],
            virus_metadata: Dict[str, Dict]):
        """ todo

        :param training_host_fasta:
        :param training_host_labels:
        :param host_matrix:
        :param virus_samples:
        :param virus_metadata:
        :param metric:
        :return:
        """

        logger.info(f'EVENT: Running fastDNA-supervised [4]')
        self._fastdna_train(training_host_fasta, training_host_labels)

        fastdna_pred_jobs = Parallel(Classifier._fastdna_predict,
                                     virus_samples,
                                     kwargs={'fastdna_exe': self.fastdna_exe.as_posix(),
                                             'model_path': self.model.as_posix(),
                                             'considered_hosts': self.considered_hosts},
                                     description='EVENT: Running fastDNA-predict [5]',
                                     n_jobs=self.threads)

        score_jobs = Parallel(score_and_rank,
                              fastdna_pred_jobs.result,
                              description='EVENT: Scoring results [6]',
                              n_jobs=self.threads)

        merged_rankings = defaultdict(dict)
        all_failed_scoring = []
        all_caught_warnings = []
        for file_path, (result, failed_methods, caught_warnings) in zip(virus_samples, score_jobs.result):
            virus_id = file_path.stem
            all_failed_scoring.extend(failed_methods)
            all_caught_warnings.extend(caught_warnings)
            for scoring_func, host_ranking in result.items():
                merged_rankings[scoring_func][virus_id] = host_ranking
        failed_count = Counter(all_failed_scoring)
        warning_count = Counter(all_caught_warnings)
        failed_warning = '\n'.join([f'{method} failed for {n_failed} viruses' for method, n_failed in failed_count.items()] + [f'Seen {w} ({n} times' for w, n in warning_count.items()])
        if failed_warning:
            logger.warning(f'Found {len(failed_count)} failed methods,'
                     f'\nthis happens during optimisation but usually means faulty fastDNA model'
                     f'\n{failed_warning}')

        evaluation, missing_predictions = TaxonomicEvaluation.multi_method_evaluation(method_to_raking_dict=merged_rankings,
                                                                                      distances=host_matrix,
                                                                                      master_virus_dict=virus_metadata,
                                                                                      threads=self.threads)

        logger.info(f'Found {missing_predictions} missing taxa with rank "{self.labels}" in matrix')

        self.ranking = sorted(evaluation, key=lambda e: e.metrics[self.metric], reverse=True)
        evaluation = self.ranking[0]
        self.scoring, self.performance = evaluation.description, evaluation.metrics[self.metric]

        return evaluation

    def _fastdna_train(self,
                       training_fasta: Path,
                       training_labels: Path):
        """
        Run training of the semantic sequence model
        using fastdna "supervised" module.
        :param training_fasta: fasta file with host genomes used for training
        :param training_labels: file with list of labels (taxon) for each sequence in the training fasta
               (line by line)
        """

        self.model = self.dir.joinpath(f"{self.name}.bin")

        print(self.threads)
        save_vec = ' -saveVec' if self.debug else ''
        command = f"{self.fastdna_exe.as_posix()} supervised " \
                  f"-input {training_fasta} -labels {training_labels}" \
                  f" -output {self.model.parent.joinpath(self.model.stem)} " \
                  f"-minn {self.minn} -maxn {self.maxn} " \
                  f"-lr {self.lr} -lrUpdateRate {self.lr_update} " \
                  f"-dim {self.dim} -noise {self.noise} -length {self.frag_len} " \
                  f"-epoch {self.epochs} -loss {self.loss} -thread {self.threads}" \
                  f"{save_vec}"
        logger.info(command)
        process = Popen(command, stdout=PIPE, shell=True)
        output, error = process.communicate()  # TODO where should it go?
        if error:
            log.info(str(output))
            log.warn(error)
        assert self.model.is_file(), str(self.model) + '\t' + self.model.as_posix()

    @staticmethod
    def _fastdna_predict(fasta: str,
                         fastdna_exe: str,
                         model_path: str,
                         considered_hosts: int) -> pd.DataFrame:
        """
        Generate basic prediction for each virus fragment
        using fastdna "predict-prob" module.
        :param fasta: fasta file with phage genome for the host prediction
        """
        command = f'{fastdna_exe} predict-prob {model_path} {fasta} {considered_hosts}'

        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = process.communicate()

        fragment_predictions = eval(stdout.decode())
        for pred_set in fragment_predictions:
            faulty_records = [(k, v) for k, v in pred_set.items() if not (isinstance(k, str) and isinstance(v, (float, int)))]
            assert not faulty_records, faulty_records

        raw_result = pd.DataFrame.from_dict(fragment_predictions).fillna(1e-6)  # https://doi.org/10.1371/journal.pbio.3000106 "we estimate that there exist globally between 0.8 and 1.6 million prokaryotic OTUs"

        return raw_result

    def predict(self,
                virus_genome_dir: Path) -> Dict[str, List[Tuple[str, float]]]:
        """
        Predict hosts for each fasta file
        in provided directory
        :param virus_genome_dir: dictionary with phage fasta files for the host prediction
        :return: dictionary with rankings of the hosts: {virus: [(host_best, high_score), (...), (host_worst, low_score)]}
        """
        print(virus_genome_dir)
        sample_dir = self.dir.joinpath(f'{virus_genome_dir.name}_sample')
        virus_samples = sample_fasta_dir(virus_genome_dir,
                                         length=self.frag_len,
                                         n_samples=self.samples,
                                         n_jobs=self.threads,
                                         to_dir=sample_dir)
        
        print(len(virus_samples))
        print({'fastdna_exe': self.fastdna_exe.as_posix(),
                                             'model_path': self.model.as_posix(),
                                             'considered_hosts': self.considered_hosts})
        fastdna_pred_jobs = Parallel(Classifier._fastdna_predict,
                                     virus_samples,
                                     kwargs={'fastdna_exe': self.fastdna_exe.as_posix(),
                                             'model_path': self.model.as_posix(),
                                             'considered_hosts': self.considered_hosts},
                                     description='running fastDNA',
                                     n_jobs=self.threads)
        # print(self.scoring)
        # print(type(self.scoring))
        # print(type(getattr(scoring, self.scoring)))
        # print(callable(getattr(scoring, self.scoring)))
        # print(fastdna_pred_jobs.result)
        # print(len(fastdna_pred_jobs.result))
        score_jobs = Parallel(self.scoring if callable(self.scoring) else getattr(scoring, self.scoring), # dirty fix for ensuring that there will be a callable obj
                              fastdna_pred_jobs.result,
                              description='Scoring results',
                              n_jobs=self.threads)

        merged_rankings = defaultdict(dict)
        print(virus_samples)
        for file_path, host_ranking in zip(virus_samples, score_jobs.result):
            virus_id = file_path.stem
            print(virus_id)
            print(type(host_ranking))
            merged_rankings[virus_id] = host_ranking.sort_values(ascending=False).to_dict()

        # print(merged_rankings)    
        # print(type(merged_rankings))
        return dict(merged_rankings)

    def clean(self):
        rmtree(self.dir)


    def save(self, path: Path):
        saved_copy = deepcopy(self)
        path.mkdir(parents=True)
        model_path = path.joinpath(self.model.name)
        classifier_path = path.joinpath('classifier.pkl')
        saved_copy.model.rename(model_path)
        saved_copy.model = model_path
        saved_copy.dir = path
        serialize(saved_copy, classifier_path)
        logger.info(f'Files stored at:\n{saved_copy.model.as_posix()}\n{model_path}')
        return saved_copy

    # TODO: not necessairly here - classifier file and then object should have the fastdna binary embedded inside - easier for everybody
    @staticmethod
    def load(model_path: Path, fastdna_path: Path) -> 'Classifier':
        # wd_path.mkdir(exist_ok=True, parents=True)
        master_file = model_path.joinpath('classifier.pkl')
        classifier = read_serialized(master_file)
        assert isinstance(classifier, Classifier), f'No valid classifier file at {master_file}'
        classifier.dir = model_path
        classifier.fastdna_exe = fastdna_path
        classifier.model = classifier.dir.joinpath(f"{classifier.name}.bin")
        assert fastdna_path.exists(), f'fastDNA executable not found at {fastdna_path}'
        assert classifier.model.is_file(), f'No valid fastDNA model file at {classifier.model}'
        return classifier


class Optimizer:
    """    todo XXX
    Template for particular _Optimizer Subclasses
    used to automatically optimise particular classifier types
    XXX
    """

    def __init__(self,
                 pre_iterations: int,
                 iterations: int,
                 working_dir: Path,
                 virus_dir: Path,
                 host_dir: Path,
                 minn: int,
                 maxn: int,
                 lr: Tuple[float, float] = (0.001, 0.999),
                 lr_update: Tuple[float, float] = (-3, 3),
                 dim: Tuple[int, int] = (30, 300),
                 noise: Tuple[int, int] = (0, 1000),
                 frag_len: Tuple[int, int] = (200, 20000),
                 epochs: int = 20,
                 loss: str = ('ns', 'hs', 'softmax'),
                 threads: int = default_threads,
                 considered_hosts: Tuple[int, int] = (10, 50),
                 n_examples=1,
                 examples_from='species',
                 labels='species',
                 samples: int = 200,
                 fastdna_exe: Path = fastDNA_exe,
                 debug: bool = False):

        self.debug = debug
        self.n_examples = n_examples
        self.examples_from = examples_from
        self.labels = labels
        self.threads = threads

        self.virus_fasta_dir = virus_dir.joinpath('fasta')
        # TODO
        # assert any([f.suffix in fasta_extensions for f in self.virus_fasta_dir.iterdir()]), f'No fasta files found in {virus_dir}' # this works on windows with 3.10 py somehow but not on linux with 3.8 py
        # TODO
        # passing link in linux to folder with files does not work
        
        logger.info("EVENT: Reading metadata [0]")
        metadata_json = virus_dir.joinpath('virus.json')
        with metadata_json.open() as mj:
            self.virus_metadata = sanitize_names(json.load(mj), virus=True)

        self.dir = working_dir
        self.dir.mkdir(exist_ok=True, parents=True)

        metadata_json = host_dir.joinpath('host.json')
        with metadata_json.open() as hj:
            self.host_metadata = sanitize_names(json.load(hj))
        
        # sampling taxa
        logger.info(f"EVENT: Sampling {self.n_examples} genomes from each taxa at {self.examples_from} level [1]")
        training_genomes, genome_labels = sample_taxon(host_data=self.host_metadata,
                                                       labeled_rank=self.labels,
                                                       sampled_rank=self.examples_from,
                                                       max_representatives=self.n_examples)
        training_genome_files = [host_dir.joinpath(f'fasta/{genome_id}.fna') for genome_id in training_genomes]
        missing_fasta = [f for f in training_genome_files if not f.is_file()]
        assert not missing_fasta, f'missing fasta files:\n{missing_fasta}'

        # labelling fastas
        path_stem = self.dir.joinpath(f'Training.{self.labels}')
        self.training_fasta, self.training_labels = labeled_fasta(training_genome_files,
                                                                  genome_labels,
                                                                  path_stem=path_stem,
                                                                  n_jobs=self.threads)

        self.param_table = self.dir.joinpath('parameters_to_results.tsv') # unused
        self.pre_iterations = pre_iterations
        self.iterations = iterations
        self.iteration_counter = count(-1 * pre_iterations)
        self.continuous = {'lr_update': lr_update}
        self.discrete = {'minn': minn, 'maxn': maxn, 'dim': dim, 'noise': noise,
                         'frag_len': frag_len, 'epoch': epochs, 'considered_hosts': considered_hosts, 'samples': samples}
        self.exponential = {'lr': lr}
        self.categorical = {'loss': loss}
        self.override = {}

        # sort single value parameters into the "override category"
        to_override = {}
        for param_category in (self.discrete, self.continuous, self.exponential, self.categorical):
            to_del = set()
            for param, param_value in param_category.items():
                if not isinstance(param_value, (tuple, list)):
                    print(type(param), type(param_value))
                    print(param, param_value)
                    to_override[param] = param_value if param in self.exponential else param_value
                    to_del.add(param)
            for redundant in to_del:
                del param_category[redundant]
        print(to_override)
        self.override.update(to_override)

        print(f"optimizer threads {threads}")
        self.fastdna_exe = fastdna_exe
        self.best_classifier = Classifier(self.dir.joinpath('best_classifier'), 0, 0, '-', 0, 0, 0, 0, 0)
        self.report = pd.DataFrame()
        self.host_matrix = DistanceMatrix(self.host_metadata,
                                          rank=self.labels)
        print(str(self.host_matrix))

    def parameter_bounds(self) -> Dict[str, Tuple[float, float]]:
        """
        Represents complex parameter dict in the simple form
        digestible for BayesianOptimization module
        """

        # parameters that are continuous (no processing required)
        parameter_bounds = self.continuous
        human_readable = {param: ' - '.join([f'{b}' for b in bounds]) for param, bounds in self.continuous.items()}

        # parameters with non-linear response curve (e.g. values that denote order of magnitude - 10eX)
        for param, bounds in self.exponential.items():
            human_readable[f'{param} (exponential)'] = ' - '.join([f'{b:.2E}' for b in bounds])
            parameter_bounds[param] = (log10(bounds[0]), log10(bounds[1]))

        # parameters that can have only integer values
        for param, bounds in self.discrete.items():
            parameter_bounds[param] = (bounds[0], bounds[1] + 1)  # assure that "border values" have equal probabilities
            human_readable[f'{param} (as integer)'] = ' - '.join([f'{int(b)}' for b in bounds])

        # parameters selected from a list of options (e.g. loss functions)
        for param, variants in self.categorical.items():
            human_readable[f'{param}'] = ', '.join(variants)
            parameter_bounds[param] = (0, len(variants) - 1e-10)  # here the same is guaranteed by th python 0-based indexing

        search_space_info = '\n'.join([f'{param: <26}{value_range}' for param, value_range in human_readable.items()])
        logger.info(f'Optimiser search space:\n{search_space_info}')

        return parameter_bounds

    def parameter_decode(self,
                         iteration_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Back-translates simple numerical form of the parameters used for classifier training
        into Sklearn and human-readable dictionary.
        @param iteration_params: parameters passed by BayesianOptimization to the current iteration
        """

        try:
            decoded_parameters = {}
            for param, value in iteration_params.items():

                # parameters with non-linear response curve (e.g. values that denote order of magnitude - 10eX)
                if param in self.exponential:
                    decoded_parameters[param] = 10 ** value

                # parameter can have integer values
                elif param in self.discrete:
                    decoded_parameters[param] = int(value)

                # parameters selected from a list of options (e.g. loss functions)
                elif param in self.categorical:
                    decoded_parameters[param] = tuple(self.categorical[param])[int(value)]

                # parameters that are continuous (no processing required)
                else:
                    decoded_parameters[param] = value

            # overwrite default parameters if included
            decoded_parameters.update(self.override)

            return decoded_parameters

        except KeyError:
            param_traceback = '\n'.join(f'{k}: {v}' for k, v in self.__dict__.items())
            raise ValueError(f'Cannot parse parameters for optimizer:\n{param_traceback}')

    def optimize(self):
        """
        Run the complete bayesian optimisation procedure with set parameter bounds
        """

        bounds = self.parameter_bounds()

        opt = BayesianOptimization(self.optimisation_iteration, bounds, verbose=0)

        opt.maximize(self.pre_iterations,
                     self.iterations)

        return opt.max

    @time_this
    def optimisation_iteration(self, **iteration_params: Dict[str, Any]) -> float:
        """
        Run a single iteration of bayesian model optimisation.
        Train and test a model with a particular set of hyperparameters.
        @param iteration_params: dictionary of hyperparameters used to train a model for each family
        @return: result of the evaluation function set as "criterion"
        """
        iteration_number = next(self.iteration_counter)
        if not iteration_number:
            iteration_number = next(self.iteration_counter)  # skip 0
        
        print(f"iteration_params {iteration_params}")
        iteration_params = self.parameter_decode(iteration_params)
        print(f"after param_decode iteration_params {iteration_params}")

        logger.info(f'Iteration: {iteration_number}')

        partial_report = dict(iteration_params)

        frag_len, samples = iteration_params['frag_len'], iteration_params['samples']
        sample_dir = self.dir.joinpath('virus_samples').joinpath(f'{frag_len}_{samples}')
        virus_sample = sample_fasta_dir(self.virus_fasta_dir,
                                        length=frag_len,
                                        n_samples=samples,
                                        n_jobs=self.threads,
                                        to_dir=sample_dir)

        classifier = Classifier(**iteration_params,
                                threads=self.threads,
                                labels=self.labels,
                                working_dir=self.dir.joinpath('current_classifier'),
                                fastdna_exe=self.fastdna_exe,
                                debug=self.debug)

        evaluation = classifier.fit(training_host_fasta=self.training_fasta,
                                    training_host_labels=self.training_labels,
                                    host_matrix=self.host_matrix,
                                    virus_samples=virus_sample,
                                    virus_metadata=self.virus_metadata)

        partial_report.update(evaluation.metrics)
        partial_report['best_scoring'] = evaluation.description
        self.report = pd.concat([self.report, pd.DataFrame.from_records([partial_report])], ignore_index=True)
        if classifier.performance >= self.best_classifier.performance:
            self.best_classifier.clean()
            self.best_classifier = classifier.save(self.dir.joinpath('best_classifier'))
            logger.info(f'Better classifier found:'
                     f'\n{evaluation.table()}')

        if (not iteration_number % 10) or iteration_number == self.iterations:
            self.report.sort_values(classifier.metric, ascending=False, inplace=True)
            self.report.to_excel(self.dir.joinpath('Optimisation_report.xlsx'))

        if self.debug:
            classifier.save(self.dir.joinpath(classifier.name))
        classifier.clean()

        return classifier.performance

# class LayeredClassifier:
#
#     def __init__(self,
#                  family_model: Classifier,
#                  genus_model: Classifier,
#                  species_model: Classifier,
#                  host_metadata):
#         self.fm_model = family_model
#         self.gn_model = genus_model
#         self.sp_model = species_model
#         self.host_metadata = host_metadata


#     def fit(self,
#                 virus_genome_dir: Path):


#     def predict(self,
#                 virus_genome_dir: Path):
#         fm_pred = self.fm_model.predict(virus_genome_dir)
#         gn_pred = self.gn_model.predict(virus_genome_dir)
#         sp_pred = self.sp_model.predict(virus_genome_dir)
#         for species in self.sp_model.host_taxonomy:
#             if
#
#     def evaluate(self, ):
#
#
#
#     @staticmethod
#     def load(family_model_dir: Classifier,
#                   genus_model_dir: Classifier,
#                   species_model_dir: Classifier,
#                   host_metadata_json):
