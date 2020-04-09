import argparse

from evaluate.score import *
from infcomp import NameParser
from utilities.config import load_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', help='filepath to config json', type=str, default='config/UNNAMED_SESSION.json')
    parser.add_argument('--name', help='name to parse', nargs='?', default='Dr. Wood, Frnnk Donald', type=str)
    parser.add_argument('--true_posterior', help='whether to sample from p(z|x) or q(z|x)', nargs='?', default=True,
                        type=bool)
    parser.add_argument('--num_particles', help='# of particles to use for SIS', nargs='?', default=15, type=int)
    parser.add_argument('--num_samples', help='# samples', nargs='?', default=10, type=int)
    parser.add_argument('--parse', help='only parse instead of denoising and parsing', nargs='?', default=False, type=bool)
    args = parser.parse_args()

    config = load_json(args.config)
    name_parser = NameParser(config['rnn_num_layers'], config['rnn_hidden_size'], config['rnn_hidden_size'], peak_prob=1-1e-4)
    name_parser.load_checkpoint(filename=f"{config['session_name']}")
    name_parser.test_mode()

    if args.true_posterior:
        sample_traces = get_importance_traces(args.name, name_parser, args.num_samples, args.num_particles)
    else:
        sample_traces = get_guide_traces(args.name, name_parser, args.num_samples)

    for j, sample in enumerate(sample_traces):
        print("Trace Log Probability: %.5f" % sample.log_prob_sum())
        if args.parse:
            print(f"Parsed Result: {get_parse_result(sample)}")
        else:
            print(f"Trace Result:  {get_full_result(sample, name_parser)}")
