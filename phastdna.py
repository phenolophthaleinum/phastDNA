import pandas as pd
import sys
from loguru import logger
from argparse import ArgumentParser
from pathlib import Path
from timeit import default_timer as timer

from learning import Optimizer, Classifier
from utils import default_threads, fasta_extensions, log, format_time


# this is probably not ideal; possibly should be rewritten
def parse_range(argument):
    if isinstance(argument, list):
        if len(tuple(argument)) == 1:
            argument, = argument
        elif len(tuple(argument)) >= 2:
            if isinstance(argument[0], str):
                return tuple(argument)
            return tuple([float(e) for e in argument])
        else:
            raise f'To many positional arguments {argument}'
    if isinstance(argument, float) or (isinstance(argument, str) and argument.isnumeric()):
        return float(argument)
    else:
        return argument
    
def unhandled_error(*exc_info):
    print(exc_info)
    # logger.exception(f'Unhandled error', exc_info=(exc_info[0], exc_info[1], exc_info[2]))
    logger.opt(exception=exc_info).error(f'Unhandled error')

sys.excepthook = unhandled_error


if __name__ == "__main__":

    logger.remove()
    logger.add(sys.stderr, format='<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {level: ^7} | <level>{message}</level>', level='INFO')
    # logger.add(sys.stderr, backtrace=True, level='ERROR')

    parser = ArgumentParser(description='fastDNA - build models for phage-host recognition '
                                        'based on similarity of semantically embedded k-mer composition '
                                        'of short sequence samples simulating sequencing reads.')
    parser.add_argument("-O", "--output", required=True,
                        help="Path to folder with result files. <train> <predict>")
    parser.add_argument("-C", "--classifier", required=False,
                        help="Path to pre-trained phastdna classifier (skips training, classifies sequences in \"-H\" host folder)")
    parser.add_argument("-H", "--hosts", required=False,
                        help="Directory with host genomes. <train>")
    parser.add_argument("-V", "--trainvir", required=False,
                        help="Directory with training viral genomes. <train>")
    parser.add_argument("-v", "--viruses", required=False,
                        help="Directory with viral genomes for prediction. <predict>")
    parser.add_argument("-r", "--lrate", required=False, nargs='+', default=-1, type=float,
                        help="EXPONENT for the Learning rate (default [0.1]). <train>")
    parser.add_argument("-u", "--ulr", required=False, nargs='+', default=100, type=float,
                        help="EXPONENT for update dynamics of the the learning rate (default [100]). <train>")
    parser.add_argument("-d", "--dim", required=False, nargs='+', default=100, type=int,
                        help="Dimensionality of k-mer embedding (default [100]). <train>")
    parser.add_argument("-n", "--noise", required=False, nargs='+', default=0, type=int,
                        help="Mutation rate (divergence) between phage and host sequences (/100,000, default [0]). <train>")
    parser.add_argument("-f", "--fraglen", required=False, nargs='+', default=200, type=int,
                        help="Length of simulated read sequences (default [200]). <train>")
    parser.add_argument("-s", "--samples", required=False, nargs='+', default=100, type=int,
                        help="Number simulated read sequences (default [100]). <train>")
    parser.add_argument("--minn", required=False, nargs='+', default=7, type=int,
                        help="Minimum k-mer size (default [7], no more than 15!). <train>")
    parser.add_argument("--maxn", required=False, nargs='+', default=8, type=int,
                        help="Maximum k-mer size (default [8], no more than 15!). <train>")
    parser.add_argument("-e", "--epochs", required=False, nargs='+', default=20, type=int,
                        help="Number of epochs (each added epoch increases runtime significantly, default [20]). <train>")
    parser.add_argument("-l", "--loss", required=False, nargs='+', default='softmax',
                        choices=['ns', 'hs', 'softmax'],
                        help="Loss function used by fastDNA algorithm (default ['softmax']). <train>")
    parser.add_argument("-p", "--preiter", required=False, nargs='+', default=15, type=int,
                        help="Number of pre-samples for Bayesian optimisation of hyper-parameters (default [15]). <train>")
    parser.add_argument("-i", "--iter", required=False, nargs='+', default=25, type=int,
                        help="Number of iterations of Bayesian optimisation of hyper-parameters. <train>")
    parser.add_argument("-c", "--considered", required=False, nargs='+', default=50, type=int,
                        help="Maximal number of hosts to include in fastDNA prediction step (default [50]). <predict> <train>")
    parser.add_argument("--examples", required=False, nargs='+', default=1, type=int,
                        help="Maximum number genomes from each \"XXX\" taxon to use in training (default [1]). <train>")
    parser.add_argument("--examples_from", required=False, nargs='+', default='species',
                        choices=["phylum", "class", "order", "family", "genus", "species"], # is it working?
                        help="Taxonomy level to which genomes should be filtered (default ['species']). <train>")
    parser.add_argument("--labels", required=False, nargs='+', default='species',
                        choices=["phylum", "class", "order", "family", "genus", "species"], # is it working?
                        help="Taxonomy level used to label genomes. This level will be predicted by classifier (default ['species']). <train>") 
    parser.add_argument("--fastdna", required=False, default='./fastDNA/fastdna',
                        help="Path to fastDNA executable (default [./fastDNA/fastdna']). <train> <predict>")
    parser.add_argument("--performance_metric", required=False, default='accordance', choices=["accordance", "top", "top3"],
                        help="Performance metric used for the trained model (default ['accordance']). <train>")
    parser.add_argument("-t", "--threads", required=False, default=default_threads, type=int,
                        help="Number of threads to use (default [all but one]). <train> <predict>")



    args = parser.parse_args()
    print(args)
    print(tuple(args.loss))
    for arg in vars(args):
        setattr(args, arg, parse_range(getattr(args, arg)))
    
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True) # shouldn't it check if exists? This throws exception if dir is already made
    log.file(output_dir.joinpath('PHastDNA_old.log'))
    logger.add(output_dir.joinpath("PHastDNA.log"), format='<green>{time:YYYY-MM-DD HH:mm:ss:SSS}</green> | {level: ^7} | <level>{message}</level>', level='INFO')
    fastdna_exe = Path(args.fastdna).resolve()
    assert fastdna_exe.is_file(), f'fastDNA executable not found at {fastdna_exe}'
    # logger.add(output_dir.joinpath("PHastDNA.log"), backtrace=True, level='ERROR')



    assert args.classifier or (args.hosts and args.trainvir), f'Either pre-trained phastdna model or training data must be specified\nPARSED ARGUMENTS: {args}'


    # fastdna_exe = Path(args.fastdna).resolve()
    # assert fastdna_exe.is_file(), f'fastDNA executable not found at {fastdna_exe}'
    # output_dir = Path(args.output).resolve()
    # output_dir.mkdir(parents=True)
    # log.file(output_dir.joinpath('PHastDNA.log'))

    # Classify based on pre-trained model
    print("loguru msg:")
    # logger.info(args)
    print(type(args.iter))
    print(type(args.preiter))
    print(type(args.lrate))
    print(type(args.ulr))
    print(type(args.threads))

    if args.classifier:
        start = timer()
        logger.info('Starting phastDNA in pre-trained prediction mode')
        virus_dir = Path(args.viruses).resolve() # resolve is painful to use
        assert any([f.suffix in fasta_extensions for f in virus_dir.iterdir()]), f'No fasta files found in {virus_dir}'
        model_file = Path(args.classifier)

        classifier = Classifier.load(model_path=model_file, fastdna_path=fastdna_exe)
        host_ranking = classifier.predict(virus_dir)
        # Save results
        results_file = output_dir.joinpath('predictions.csv')
        # json.dump(host_ranking, open(results_file, 'w'), indent=4)
        # save host ranking as a table  
        results_df = pd.DataFrame.from_dict(host_ranking, orient='columns')
        results_df = results_df.rename_axis("Host").reset_index()
        results_df_melted = results_df.melt(id_vars=["Host"], var_name="Virus", value_name="Score")
        results_df_sorted = results_df_melted.groupby('Virus').apply(lambda x: x.sort_values(by='Score', ascending=False)).reset_index(drop=True)
        results_df_sorted.to_csv(results_file, index=False)
        logger.info(f'Results saved to {results_file}')
        end = timer()
        runtime = end - start
        logger.info(f"Prediction executed successfully in {format_time(runtime)}")


    # Train a new model and optimize hyperparameters
    elif args.hosts:
        logger.info('Starting phastDNA in training mode')
        virus_dir = Path(args.trainvir).resolve()
        host_dir = Path(args.hosts).resolve()
        optimizer = Optimizer(pre_iterations=args.preiter,
                              iterations=args.iter,
                              working_dir=output_dir,
                              host_dir=host_dir,
                              virus_dir=virus_dir,
                              minn=args.minn,
                              maxn=args.maxn,
                              lr=args.lrate,
                              lr_update=args.ulr,
                              dim=args.dim,
                              noise=args.noise,
                              frag_len=args.fraglen,
                              epochs=args.epochs,
                              loss=args.loss,
                              threads=args.threads,
                              considered_hosts=args.considered,
                              n_examples=args.examples,
                              examples_from=args.examples_from,
                              labels=args.labels,
                              samples=args.samples,
                              fastdna_exe=fastdna_exe)
        optimizer.optimize()

    logger.success('Finished!')

