import yaml
import os
from datetime import date
import calendar
import subprocess
from shutil import copyfile

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

def clone_repo(clone_dir, pkg_name):
    print("Cloning {} repository...".format(pkg_name))
    if not os.path.isdir(clone_dir):
        subprocess.check_output('git clone https://github.com/{}.git {}'\
                .format(pkg_name, clone_dir).split())
    print("Done.")

def clone_spack_dependencies():
    config = setup_env_variables()
    clone_repo(config['SPACKDIR'], 'LLNL/spack')
    clone_repo(config['HEP_REPO'], 'HEP-SF/hep-spack')
    clone_repo(config['FCC_REPO'], 'JavierCVilla/fcc-spack')

def source_compiler():
    return

def source_spack():
    return

def configure_compiler():
    config = setup_env_variables()
    src = '{}/config/compiler-{}-{}.yaml'.format(config['CURRENT_DIR'],\
            config['OS'], config['COMPILER'])
    dst = '{}/linux/compilers.yaml'.format(config['SPACK_CONFIG'])
    copyfile(src, dst)

if __name__ == "__main__":
    clone_spack_dependencies()
    configure_compiler()