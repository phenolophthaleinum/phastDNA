#!/usr/bin/env python3
"""
author: Jakub Barylski
Created on 10.12.2021 (v0.0.1)
"""

import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Any, Union
from loguru import logger

import joblib
import numpy as np
import pandas as pd

from utils import Parallel, log, default_threads

PathLike = Union[Path, str]

# selected only consistent ranks annotated in all prokaryotic lineages
TAXONOMIC_RANKS = ['species',
                   'genus',
                   'family',
                   'order',
                   'class',
                   'phylum',
                   'superkingdom']


def sample_taxon(host_data: Dict[str, Dict[str, Any]],
                 sampled_rank: str = 'species',
                 labeled_rank: str = 'species',
                 max_representatives: int = 1,
                 leave_out_label: str = None,
                 use_names: bool = True) -> Tuple[List[str], List[str]]:
    """ todo

    :param host_data:
    :param sampled_rank:
    :param labeled_rank:
    :param max_representatives:
    :param leave_out_label:
    :param use_names:
    :return:
    """
    # filtering all hosts by a chosen level annd
    assert TAXONOMIC_RANKS.index(labeled_rank) >= TAXONOMIC_RANKS.index(sampled_rank), f'Selecting {max_representatives} for {sampled_rank} and' \
                                                                                       f'labeling them with {labeled_rank} does not make any sense'
    searched_field = 'lineage_names' if use_names else 'lineage'
    genomes_in_taxons = defaultdict(list)
    taxon_labels = {}
    for host, host_metadata in host_data.items():
        lineage = get_lineage(host_metadata,
                              searched_field=searched_field,
                              lowest_rank=sampled_rank)
        sampled_taxon, taxon_label = lineage[sampled_rank], lineage[labeled_rank]
        if taxon_label != leave_out_label:  # exclude certain taxonomic label
            genomes_in_taxons[sampled_taxon].append(host)
            if sampled_taxon not in taxon_labels:
                taxon_labels[sampled_taxon] = taxon_label

    # random sampling of {max_representatives} host from a level
    selected_host = {taxon: random.sample(ids, max_representatives) if len(ids) > max_representatives else ids for taxon, ids in genomes_in_taxons.items()}

    # flattening the dict to one level label and file list
    genome_ids, labels = [], []
    for sampled_taxon, genome_batch in selected_host.items():
        label = taxon_labels[sampled_taxon]
        genome_ids.extend(genome_batch)
        labels.extend([label for _ in genome_batch])

    return genome_ids, labels


def get_lineage(metadata_dict,
                searched_field,
                lowest_rank: str = 'species') -> Dict[str, str]:
    """
    Todo
    WARNING! This will return a taxonomic level HIGER than lowest_rank if linage doesn't contain requested one
    :param metadata_dict:
    :param searched_field:
    :param lowest_rank:
    :return:
    """
    truncated_ranks = TAXONOMIC_RANKS[TAXONOMIC_RANKS.index(lowest_rank):]

    lineage = {rank: tax_id for rank, tax_id in zip(metadata_dict['lineage_ranks'], metadata_dict[searched_field]) if rank in truncated_ranks}

    truncated_ranks.reverse()
    one_up = 'root'
    for rank in truncated_ranks:
        if rank not in lineage or not lineage[rank]:
            lineage[rank] = f'UNCLASSIFIED_{one_up}'
        one_up = lineage[rank]

    return lineage


def taxonomic_distance(linage0: Dict[str, str],
                       linage1: Dict[str, str],
                       base_rank: str = 'species') -> int:
    """
    Score taxonomic relation between two species.
    If the both are identical return 0.
    Otherwise, return number of taxonomic levels
    one need to go up to find a common taxon.
    E.g. species = 0, genus = 1, family = 2 etc.
    @return: taxonomic similarity score
    """
    truncated_ranks = TAXONOMIC_RANKS[TAXONOMIC_RANKS.index(base_rank):]
    distance = None
    for distance, rank in enumerate(truncated_ranks):
        if linage0[rank] == linage1[rank]:
            return distance
    return distance + 1


class DistanceMatrix:
    """
    Dictionary-like object with species -> genome distances
    :param master_host_dict: dictionary of host metadata stored in 'host.json'
    :return: {'species_id_0': {'genome0': distance0, (...) 'genomeN': distanceN}, species_id_1 ...}
    """

    def __init__(self,
                 master_host_dict: Dict[str, Dict[str, Any]],
                 rank: str = 'species',
                 use_names: bool = True):
        searched_field = 'lineage_names' if use_names else 'lineage'
        self.rank = rank
        self.taxonomy = {}
        for genome_id, metadata_dict in master_host_dict.items():
            lineage = get_lineage(metadata_dict,
                                  searched_field=searched_field,
                                  lowest_rank=rank)
            self.taxonomy[lineage[rank]] = lineage

        remaining_taxa = list(self.taxonomy)
        self.taxa_indices = {taxon: i for i, taxon in enumerate(remaining_taxa)}
        n_species = len(remaining_taxa)

        self.matrix = np.empty([n_species, n_species], dtype=np.int16)
        np.fill_diagonal(self.matrix, 0)

        # log.set_task('creating distance matrix', remaining_taxa)
        logger.info('EVENT: Creating distance matrix')
        while remaining_taxa:
            query_taxid = remaining_taxa.pop(0)
            query_lineage, qi = self.taxonomy[query_taxid], self.taxa_indices[query_taxid]
            for target_taxid in remaining_taxa:
                target_lineage = self.taxonomy[target_taxid]
                ti = self.taxa_indices[target_taxid]
                self.matrix[qi][ti] = self.matrix[ti][qi] = taxonomic_distance(query_lineage, target_lineage, base_rank=rank)
            # log.update()

    def __repr__(self):
        return f'DistanceMatrix with ({len(self.taxa_indices)} {self.rank} entries e.g. {list(self.taxonomy.keys())[:3]})'

    def get_distance(self, species_id_0, species_id_1):
        """
        Retrieve a taxonomic distance between two species
        :param species_id_0: e.g. NC_017548
        :param species_id_1:
        :return:
        """
        return self.matrix[self.taxa_indices[species_id_0]][self.taxa_indices[species_id_1]]

    def save(self,
             path: PathLike,
             compress_param: Union[int, bool, Tuple[str, int]]):
        """
        Serialize the matrix for further use
        :param compress_param: todo
        :param path:
        :return:
        """
        path = Path(path)
        with path.open('wb') as out:
            joblib.dump(self, out, compress=compress_param)

    def to_excel(self,
                 path: PathLike):
        path = Path(path)
        taxids = list(self.taxa_indices.keys())
        df = pd.DataFrame(index=taxids, columns=taxids, data=self.matrix)
        df.to_excel(path.as_posix())

    @staticmethod
    def load(path: PathLike) -> 'DistanceMatrix':
        path = Path(path)
        with path.open('rb') as out:
            matrix = joblib.load(out)
        return matrix


class TaxonomicEvaluation:

    def __init__(self,
                 sorted_predictions: Dict[str, List[Tuple[str, float]]],
                 distances: DistanceMatrix,
                 master_virus_dict: Dict[str, Dict[str, Any]],
                 description: str = None,
                 use_names: bool = True,
                 top_n: int = 3):
        """
        Calculate a "taxonomic discordance" for provided predictions.
        This is metric that is a ration of:
        taxonomic distances between true and predicted hosts
        to
        all possible on the hierarchical taxon tree (worst of possible predictions)
        The calculated for "top_n" predictions extracted from probability-sorted prediction dict
        Weight of each is prediction adjusted inversely to its rank.
        :param sorted_predictions: {virus_id_0: [('host_id_BEST', p_BEST), (...), ('host_id_WORST', p_WORST)], virus_id_1 ...}
        :param distances: DistanceMatrix object used to infer taxonomic distances between taxons and genomes
        :param master_virus_dict: dictionary of virus metadata stored in 'virus.json'
        :param top_n: number of top prediction to assess
        :return: todo
        """

        searched_field = 'lineage_names' if use_names else 'lineage'
        truncated_ranks = TAXONOMIC_RANKS[TAXONOMIC_RANKS.index(distances.rank):]
        min_rank, second_rank = truncated_ranks[:2]
        per_taxon_hits = {rank: {i + 1: [] for i in range(top_n)} for rank in truncated_ranks}

        self.description = description
        self.n_viruses = len(sorted_predictions)
        self.position_adjusted_predictions = 0
        self.observed_shift = 0
        self.skipped = set()
        self.hit = set()
        max_unit_shift = (len(TAXONOMIC_RANKS) + 1)
        for virus_id, predictions in sorted_predictions.items():
            lineage = get_lineage(master_virus_dict[virus_id]['host'], searched_field)  # TODO Edwards notation is VERY CONFUSING (should be master_virus_dict[virus_id]['host']['species/taxid']) !!!
            true_host_taxid = lineage[distances.rank]
            if len(predictions) > top_n:
                predictions = predictions[:top_n]
            for rankin_position, (host_taxid, confidence) in enumerate(predictions, 1):
                self.position_adjusted_predictions += 1 / rankin_position
                if host_taxid in distances.taxonomy and true_host_taxid in distances.taxonomy:
                    observed_distance = distances.get_distance(host_taxid, true_host_taxid)
                    self.observed_shift += observed_distance / rankin_position
                    self.hit.add(host_taxid)
                    matched_ranks = truncated_ranks[observed_distance:]
                    [per_taxon_hits[rank][rankin_position].append(virus_id) for rank in matched_ranks]
                else:
                    skip_reason = " host_taxid not in distances.taxonomy" if not host_taxid in distances.taxonomy else f"true_host_taxid ({true_host_taxid}) not in distances.taxonomy"
                    # logger.info(f'{host_taxid} not in {distances.taxonomy}') if not host_taxid in distances.taxonomy else logger.info(f'{true_host_taxid} not in {distances.taxonomy}')
                    self.observed_shift += max_unit_shift / rankin_position
                    self.skipped.add((host_taxid, skip_reason))

        self.max_shift = self.position_adjusted_predictions * max_unit_shift

        self.accordance = 1 - (self.observed_shift / self.max_shift)
        self.scored_ranks = {}
        for rank, ranking_hits in per_taxon_hits.items():
            self.scored_ranks[rank] = {}
            all_hit = set()
            for rankin_position, hits in ranking_hits.items():
                all_hit.update(hits)
                self.scored_ranks[rank][rankin_position] = len(all_hit) / self.n_viruses
        self.metrics = {'accordance': self.accordance,
                        f'top_{min_rank}': self.scored_ranks[min_rank][1],
                        f'top3_{min_rank}': self.scored_ranks[min_rank][3],
                        f'top_{second_rank}': self.scored_ranks[second_rank][1],
                        f'top3_{second_rank}': self.scored_ranks[second_rank][3]}

    def __repr__(self):
        table_data = [(f'{rank}:', '\t'.join([f'{s:.3f}' for s in scores.values()])) for rank, scores in self.scored_ranks.items()]
        ranked_table = '\n'.join([f'{row_header: <13} {row}' for row_header, row in table_data])
        return f'accordance: {self.accordance:.3f}' \
               f'\n{ranked_table}'

    def table(self):
        return self.__repr__()

    @staticmethod
    def multi_method_evaluation(method_to_raking_dict: Dict[str, Dict[str, Dict[str, Any]]],
                                distances: DistanceMatrix,
                                master_virus_dict: Dict[str, Dict[str, Any]],
                                use_names: bool = True,
                                top_n: int = 3,
                                threads: int = default_threads) -> Tuple[List['TaxonomicEvaluation'], int]:
        """

        :param method_to_raking_dict:
        :param distances:
        :param master_virus_dict:
        :param use_names:
        :param top_n:
        :return:
        """
        inputs = list(method_to_raking_dict.items())
        jobs = Parallel(TaxonomicEvaluation.labeled_evaluation,
                        input_collection=inputs,
                        description=f'Evaluating results of {len(method_to_raking_dict)} methods',
                        kwargs={'distances': distances,
                                'master_virus_dict': master_virus_dict,
                                'use_names': use_names,
                                'top_n': top_n},
                        n_jobs=threads)
        missing_predictions = set()
        for r in jobs.result:
            missing_predictions.update(r.skipped)
        return jobs.result, missing_predictions, len(missing_predictions)

    @staticmethod
    def labeled_evaluation(name_and_ranking: Dict[str, Dict[str, Dict[str, Any]]],
                           distances: DistanceMatrix,
                           master_virus_dict,
                           use_names: bool = True,
                           top_n: int = 3):
        """

        :param name_and_ranking:
        :param distances:
        :param master_virus_dict:
        :param use_names:
        :param top_n:
        :return:
        """
        description, ranking = name_and_ranking
        return TaxonomicEvaluation(sorted_predictions=ranking,
                                   distances=distances,
                                   master_virus_dict=master_virus_dict,
                                   description=description,
                                   use_names=use_names,
                                   top_n=top_n)
