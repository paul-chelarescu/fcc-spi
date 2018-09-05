from spack_config import *
import sys
import argparse
import errno

def main(main_args):
    parser = argparse.ArgumentParser(formatter_class=argparse
            .ArgumentDefaultsHelpFormatter)
    parser.add_argument('--branch', type=str, help='fcc-spack branch')
    args = parser.parse_args(main_args)

    if 'TMPDIR' not in config:
        config['TMPDIR'] = '/tmp/fcc/spackinstall'
        try:
            os.makedirs(config['TMPDIR'])
        except OSError as e:
            if e.errno == errno.EEXIST and os.path.isdir(config['TMPDIR']):
                pass
            else:
                raise

    config['SPACK_ROOT'] = config['TMPDIR'] + '/spack'
    config['SPACK_HOME'] = 'TMPDIR'
    config['HOME'] = config['SPACK_HOME'] #!!!!!
    config['SPACK_CONFIG'] = config['HOME'] + '/.spack'

    config['HEP_REPO'] = config['SPACK_ROOT'] + '/var/spack/repos/hep-spack'
    config['FCC_REPO'] = config['SPACK_ROOT'] + '/var/spack/repos/fcc-spack'

    clone_repo(config['SPACK_ROOT'], 'JavierCVilla/spack', '-b buildcache_fix')
    clone_repo(config['HEP_REPO'], 'HEP-SF/hep-spack', '')
    clone_repo(config['FCC_REPO'], 'JavierCVilla/fcc-spack',
            '--branch ' + args.branch)


if __name__ == "__main__":
    main(sys.argv[1:])
