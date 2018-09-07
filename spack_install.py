from spack_config import *
import sys
import argparse
import errno

def copy_patchelf_config():
    src = '{}/config/patchelf.yaml'.format(config['CURRENT_DIR'])
    dst = '{}/linux/packages.yaml'.format(config['SPACK_CONFIG'])

    with open(dst, 'a') as dst_file:
        with open(src) as src_file:
            dst_file.write(src_file.read())


def create_spack_config():
    src = '{}/config/config.tpl'.format(config['CURRENT_DIR'])
    dst = '{}/linux/config.yaml'.format(config['SPACK_CONFIG'])
    copyfile(src, dst)

    with open(dst) as f:
        config_text = f.read()
        config_text = config_text.replace('{{PREFIX_PATH}}', config['PREFIX'])

    with open(dst, "w") as f:
        f.write(config_text)


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

    copy_compiler_config()
    create_spack_config()


if __name__ == "__main__":
    main(sys.argv[1:])
