"""Speculative MTP (ESP reproduction + EMA velocity) — entry point.

Training-free: only the `test` stage exists. Any config value can be
overridden from the CLI with repeated `--set dotted.key=value` flags, which
the ablation sweep scripts use to fan out from base configs.
"""

import argparse
import json
import os
import shutil
import sys
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from core import config, tools


def get_args():
    parser = argparse.ArgumentParser(description='ESP / EMA-velocity speculative MTP')
    parser.add_argument('--cfg_file', required=True, help='Path to YAML config')
    parser.add_argument('--device', type=str, default=None, help='Override device')
    parser.add_argument('--save_dir', type=str, default=None, help='Override save_root')
    parser.add_argument('--save_name', type=str, default=None, help='Override save_name')
    parser.add_argument('--set', dest='overrides', action='append', default=[],
                        metavar='KEY=VALUE',
                        help='Override any config entry, e.g. --set spec.mask.lam=0.5')
    return parser.parse_args()


def main():
    args = get_args()
    cfg = config.get_config(args.cfg_file)

    if args.device is not None:
        cfg.eval.device = args.device
    if args.save_dir is not None:
        cfg.run.save_root = args.save_dir
    if args.save_name is not None:
        cfg.run.save_name = args.save_name
    for override in args.overrides:
        key, _, value = override.partition('=')
        if not _:
            raise ValueError(f'Malformed --set override: {override}')
        config.apply_override(cfg, key, value)

    cfg.run.save_dir = os.path.join(cfg.run.save_root, cfg.run.save_name)
    tools.seed_everything(cfg.run.seed, deterministic=cfg.run.get('deterministic', False))

    import algorithms
    algo = getattr(algorithms, cfg.run.algorithm)

    for stage in cfg.run.get('stages', ['test']):
        print(f'\n{"=" * 60}')
        print(f'[STAGE={stage}]  algorithm={cfg.run.algorithm}')
        print(f'{"=" * 60}')
        if stage == 'test':
            tools.makedir_exist_ok(cfg.run.save_dir)
            shutil.copy(cfg.cfg_file, os.path.join(cfg.run.save_dir, 'cfg_base.yml'))
            with open(os.path.join(cfg.run.save_dir, 'cfg.yml'), 'w') as f:
                yaml.safe_dump(json.loads(json.dumps(cfg)), f, sort_keys=False)
            algo.test(cfg)
        elif stage == 'train':
            raise ValueError('This project is training-free; only stage "test" exists.')
        else:
            raise ValueError(f'Unknown stage: {stage}')


if __name__ == '__main__':
    main()
