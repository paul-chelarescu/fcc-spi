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
    config['WORKSPACE'] = os.getcwd()

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

def clone_repo(clone_dir, pkg_name, args):
    print("Cloning {} repository...".format(pkg_name))
    if not os.path.isdir(clone_dir):
        subprocess.check_output('git clone https://github.com/{}.git {} {}'\
                .format(pkg_name, args, clone_dir).split())
    print("Done.")


def clone_spack_dependencies():
    clone_repo(config['SPACKDIR'], 'LLNL/spack', '')
    clone_repo(config['HEP_REPO'], 'HEP-SF/hep-spack', '')
    clone_repo(config['FCC_REPO'], 'JavierCVilla/fcc-spack', '')
    

def source_compiler():
    return


def source_spack():
    return


def configure_compiler():
    src = '{}/config/compiler-{}-{}.yaml'.format(config['CURRENT_DIR'],\
            config['OS'], config['COMPILER'])
    dst = '{}/linux/compilers.yaml'.format(config['SPACK_CONFIG'])
    copyfile(src, dst)

    packages = yaml.load(read_spack_packages())
    tbb_lib = packages['packages']['intel-tbb']['paths'].values()[0] + '/lib'
    root_lib = packages['packages']['root']['paths'].values()[0] + '/lib'
    extra_libs = tbb_lib + ":" + root_lib

    with open(dst) as f:
        compilers_text = f.read()

    compilers_text = compilers_text.replace("EXTRA_LIBS", extra_libs)

    with open(dst, "w") as f:
        f.write(compilers_text)


def configure_lcg_externals():
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


def replace_lcg_package_names():
    lcg_packages_file = '{}/{}_packages.yaml'.format(config['WORKSPACE'],
            config['LCG_VERSION'])

    with open(lcg_packages_file) as f:
        lcg_packages_text = f.read()
        lcg_packages_text = lcg_packages_text.replace('tbb:', 'intel-tbb:')
        lcg_packages_text = lcg_packages_text.replace('tbb@', 'intel-tbb@')
        lcg_packages_text = lcg_packages_text.replace('xercesc:', 'xerces-c:')
        lcg_packages_text = lcg_packages_text.replace('xercesc@', 'xerces-c@')
        lcg_packages_text = lcg_packages_text.replace('java:', 'jdk:')
        lcg_packages_text = lcg_packages_text.replace('java@', 'jdk@')

    with open(lcg_packages_file, "w") as f:
        f.write(lcg_packages_text)

    return lcg_packages_text


def read_default_packages():
    packages_file = '{}/packages.yaml'.format(config['WORKSPACE'])

    with open(packages_file) as f:
        packages_text = f.readlines()

    os.remove(packages_file)
    return packages_text


def read_fcc_packages():
    fcc_version_file = '{}/config/packages-{}.yaml'.format(
            config['CURRENT_DIR'], config['FCC_VERSION'])

    with open(fcc_version_file) as f:
        fcc_version_text = f.readlines()
    return fcc_version_text


def create_lcg_packages():
    args = ['--blacklist', '{}/config/packages-{}.yaml'\
            .format(config['CURRENT_DIR'], config['FCC_VERSION']),
            config['LCG_externals']]
    create_lcg_package_specs.main(args)

    src = '{}/config/packages-default.yaml'.format(config['CURRENT_DIR'])
    dst = '{}/packages.yaml'.format(config['WORKSPACE'])
    copyfile(src, dst)


def remove_first_line(packages):
    return '\n'.join(packages.split('\n')[1:])


def get_gitpython_package():
    return """  py-gitpython:
    buildable: false
    paths: {py-gitpython@2.1.8-0%gcc@6.2.0 arch=x86_64-scientificcernslc6: \
/cvmfs/fcc.cern.ch/sw/0.8.3/gitpython/lib/python2.7/site-packages}
"""


def write_spack_packages(packages):
    spack_packages_file = '{}/linux/packages.yaml'.format(
            config['SPACK_CONFIG'])

    with open(spack_packages_file, "w") as f:
        for line in packages:
            f.write(line)

def read_spack_packages():
    spack_packages_file = '{}/linux/packages.yaml'.format(
            config['SPACK_CONFIG'])

    with open(spack_packages_file) as f:
        packages_text = f.read()

    return packages_text

def create_packages():
    configure_lcg_externals()
    create_lcg_packages()

    packages_text = read_default_packages()
    lcg_packages = replace_lcg_package_names()
    packages_text.extend(remove_first_line(lcg_packages))
    packages_text.extend(read_fcc_packages())

    if 'gcc62' in config['COMPILER']:
        packages_text.extend(get_gitpython_package())

    write_spack_packages(packages_text)
