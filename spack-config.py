import yaml
import os
from datetime import date
import calendar
import subprocess
from shutil import copyfile
import create_lcg_package_specs

def parse_env_variables():
    with open('spack-config.yaml', 'r') as cfile:
        return yaml.load(cfile)


def setup_env_variables():
    config = parse_env_variables()
    if 'FCC_VERSION' not in config:
        config['FCC_VERSION'] = 'stable'
    config['CURRENT_DIR'] = os.path.dirname(os.path.realpath(__file__))

    TOOLSPATH = '/cvmfs/fcc.cern.ch/sw/0.8.3/tools/'
    command = 'python {}/hsf_get_platform.py --compiler {} --buildtype '\
            .format(TOOLSPATH, config['COMPILER'])

    if 'Release' in config['BUILDTYPE']:
        command += 'opt'
    else:
        command += 'dbg'

    config['PLATFORM'] = subprocess.check_output(command.split()).rstrip()

    if 'gcc73' in config['PLATFORM']:
        config['PLATFORM'] = config['PLATFORM'].replace('gcc73', 'gcc7')

    command = 'python {}/hsf_get_platform.py --get os'.format(TOOLSPATH)
    config['OS'] = subprocess.check_output(command.split()).rstrip()

    config['WEEKDAY'] = calendar.day_name[date.today().weekday()][:3]

    config['SPACKDIR'] = config['WORKSPACE'] + '/spack'
    config['SPACK_HOME'] = config['WORKSPACE']
    config['HOME'] = config['SPACK_HOME'] #!!!!!!!

    config['SPACK_CONFIG'] = config['HOME'] + "/.spack"
    config['HEP_REPO'] = config['SPACKDIR'] + '/var/spack/repos/hep-spack'
    config['FCC_REPO'] = config['SPACKDIR'] + '/var/spack/repos/fcc-spack'

    return config

config = setup_env_variables()

def clone_repo(clone_dir, pkg_name):
    print("Cloning {} repository...".format(pkg_name))
    if not os.path.isdir(clone_dir):
        subprocess.check_output('git clone https://github.com/{}.git {}'\
                .format(pkg_name, clone_dir).split())
    print("Done.")


def clone_spack_dependencies():
    clone_repo(config['SPACKDIR'], 'LLNL/spack')
    clone_repo(config['HEP_REPO'], 'HEP-SF/hep-spack')
    clone_repo(config['FCC_REPO'], 'JavierCVilla/fcc-spack')
    

def source_compiler():
    return


def source_spack():
    return


def configure_compiler():
    src = '{}/config/compiler-{}-{}.yaml'.format(config['CURRENT_DIR'],\
            config['OS'], config['COMPILER'])
    dst = '{}/linux/compilers.yaml'.format(config['SPACK_CONFIG'])
    copyfile(src, dst)


def create_packages():
    if config['LCG_VERSION'].startswith('LCG_'):
        config['LCG_externals'] = '/cvmfs/sft.cern.ch/lcg/releases/{}/'\
                'LCG_*_{}.txt'.format(config['LCG_VERSION'],
                        config['PLATFORM'])
    else:
        config['LCG_externals'] = '/cvmfs/sft.cern.ch/lcg/nightlies/{}/{}/'\
                'LCG_*_{}.txt'.format(config['LCG_VERSION'],
                        config['weekday'], config['PLATFORM'])

    print('Using LCG externals from: {}'.format(config['LCG_externals']))
    modification_date = subprocess.Popen('stat {} | grep Modify |'\
            ' tr -s " " | cut -d" " -f2,3'.format(config['LCG_externals']),
            shell=True, stdout=subprocess.PIPE)
    print('Modification date: {}'.format(modification_date.stdout.read()\
            .rstrip()))

    args = ['--blacklist', '{}/config/packages-{}.yaml'\
            .format(config['CURRENT_DIR'], config['FCC_VERSION']),
            config['LCG_externals']]
    create_lcg_package_specs.main(args)


if __name__ == "__main__":
    clone_spack_dependencies()
    configure_compiler()
    create_packages()
