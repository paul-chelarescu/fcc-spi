#!/bin/sh

touch controlfile

export HOME=`pwd`

TOOLSPATH=/cvmfs/fcc.cern.ch/sw/0.8.3/tools/
OS=`python $TOOLSPATH/hsf_get_platform.py --get os`

THIS_DIR=$(dirname ${BASH_SOURCE[0]})
python $THIS_DIR/create_spack_config.py

source $HOME/spack/share/spack/setup-env.sh

gcc49version=4.9.3
gcc62version=6.2.0
gcc73version=7.3.0
export COMPILERversion=${COMPILER}version

source /cvmfs/sft.cern.ch/lcg/contrib/gcc/${!COMPILERversion}binutils/x86_64-${OS}/setup.sh
