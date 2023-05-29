from argparse import ArgumentParser
from pathlib import Path

from learning import Optimizer, Classifier
from utils import default_threads, fasta_extensions, log

def parse_range(argument):
    if isinstance(argument, list):
        if len(tuple(argument)) == 1:
            argument, = argument
        elif len(tuple(argument)) == 2:
            return tuple([float(e) for e in argument])
        else:
            raise f'To many positional arguments {argument}'
    if isinstance(argument, float) or (isinstance(argument, str) and argument.isnumeric()):
        return float(argument)
    else:
        return argument


if __name__ == "__main__":

    parser = ArgumentParser(description='fastDNA - build models for phage-host recognition '
                                        'based on similarity of semantically embedded k-mer composition '
                                        'of short sequence samples simulating sequencing reads.')
    parser.add_argument("-O", "--output", required=True,
                        help="Path to folder with result files")
    parser.add_argument("-C", "--classifier", required=False,
                        help="Path to pre-trained phastdna classifier (skips training, classifies sequences in \"-H\" host folder)")
    parser.add_argument("-H", "--hosts", required=False,
                        help="Directory with host genomes.")
    parser.add_argument("-V", "--trainvir", required=False,
                        help="Directory with training viral genomes.")
    parser.add_argument("-v", "--viruses", required=False,
                        help="Directory with viral genomes for prediction.")
    parser.add_argument("-r", "--lrate", required=False, nargs='+', default=-1,
                        help="EXPONENT for the Learning rate (default [-1] = 1e-1 = 0.1)")
    parser.add_argument("-u", "--ulr", required=False, nargs='+', default=2,
                        help="EXPONENT for update dynamics of the the learning rate (default [2] = 1e2 = 100)")
    parser.add_argument("-d", "--dim", required=False, nargs='+', default=100, type=int,
                        help="Dimensionality of k-mer embedding (default [100])")
    parser.add_argument("-n", "--noise", required=False, nargs='+', default=0,
                        help="Mutation rate (divergence) between phage and host sequences (/100,000, default [0])")
    parser.add_argument("-f", "--fraglen", required=False, nargs='+', default=200, type=int,
                        help="Length of simulated read sequences (default [200])")
    parser.add_argument("-s", "--samples", required=False, nargs='+', default=100, type=int,
                        help="Number simulated read sequences (default [100])")
    parser.add_argument("--minn", required=False, nargs='+', default=7, type=int,
                        help="Minimum k-mer size (default [7], no more than 15!)")
    parser.add_argument("--maxn", required=False, nargs='+', default=8, type=int,
                        help="Maximum k-mer size (default [8], no more than 15!)")
    parser.add_argument("-e", "--epochs", required=False, nargs='+', default=20, type=int,
                        help="Number of epochs (each added epoch increases runtime significantly)")
    parser.add_argument("-l", "--loss", required=False, nargs='+', default='softmax',
                        choices=['ns', 'hs', 'softmax'],
                        help="Taxonomy level to which genomes should be filtered. Choosing 'none' implies no taxonomy filtering.")
    parser.add_argument("-p", "--preiter", required=False, nargs='+', default=15, type=int,
                        help="Number of pre-samples for Bayesian optimisation of hyper-parameters")
    parser.add_argument("-i", "--iter", required=False, nargs='+', default=25, type=int,
                        help="Number of iterations of Bayesian optimisation of hyper-parameters")
    parser.add_argument("-c", "--considered", required=False, nargs='+', default=50, type=int,
                        help="Maximal number of hosts to include in fastDNA prediction step")
    parser.add_argument("--nreps", required=False, nargs='+', default=1, type=int,
                        help="Maximum number of representatives from the filtered group. Default value is 1.")  # TODO not implemented
    parser.add_argument("--filter", required=False, nargs='+', default='species',
                        choices=["phylum", "class", "order", "family", "genus", "species", "none", 'hybrid', 'debug', 'general'], # is it working?
                        help="Taxonomy level to which genomes should be filtered. Choosing 'none' implies no taxonomy filtering.")  # TODO not implemented - must be implemented, since species take up to an hour
    parser.add_argument("--fastdna", required=False, default='./fastDNA/fastdna',
                        help="Path to fastDNA execuable")
    parser.add_argument("-t", "--threads", required=False, default=default_threads,
                        help="Number of threads to use (default [all but one])")



    args = parser.parse_args()
    for arg in vars(args):
        setattr(args, arg, parse_range(getattr(args, arg)))
    

    fastdna_exe = Path(args.fastdna).resolve()
    assert fastdna_exe.is_file(), f'fastDNA executable not found at {fastdna_exe}'
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True) # shouldn't it check if exists? This throws exception if dir is already made
    log.file(output_dir.joinpath('PHastDNA.log'))



    assert args.classifier or (args.hosts and args.trainvir), f'Either pre-trained phastdna model or training data must be specified\nPARSED ARGUMENTS: {args}'


    # fastdna_exe = Path(args.fastdna).resolve()
    # assert fastdna_exe.is_file(), f'fastDNA executable not found at {fastdna_exe}'
    # output_dir = Path(args.output).resolve()
    # output_dir.mkdir(parents=True)
    # log.file(output_dir.joinpath('PHastDNA.log'))

    # Classify based on pre-trained model
    print(type(args.iter))

    if args.classifier:
        log.info('Starting PHastDNA in pre-trained mode')
        virus_dir = Path(args.viruses).resolve() # resolve is painful to use
        assert any([f.suffix in fasta_extensions for f in virus_dir.iterdir()]), f'No fasta files found in {virus_dir}'
        model_file = Path(args.classifier)

        classifier = Classifier.load(path=model_file)
        host_ranking = classifier.predict(virus_dir)




    # Train a new model and optimize hyperparameters
    elif args.hosts:
        log.info('Starting PHastDNA in training mode')
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
                              samples=args.samples,
                              fastdna_exe=fastdna_exe,
                              rank=args.filter)
        optimizer.optimize()

    log.close() #  close log after successful run

