#!/bin/sh -u
# This script sets up the commonly used software for FCC software projects:
# - Linux machines at CERN:  The software is taken from afs.
# - MacOS / Linux elsewhere: We assume the software is installed locally and their environment is set.

# Add the passed value only to path if it's not already in there.
function add_to_path {
    if [ -z "$1" ] || [[ "$1" == "/lib" ]]; then
        return
    fi
    path_name=${1}
    eval path_value=\$$path_name
    path_prefix=${2}
    case ":$path_value:" in
      *":$path_prefix:"*) :;;        # already there
      *) path_value=${path_prefix}:${path_value};; # or prepend path
    esac
    eval export ${path_name}=${path_value}
}

platform='unknown'
unamestr=`uname`


if [[ "$unamestr" == 'Linux' ]]; then
    platform='Linux'
    echo "Platform detected: $platform"
    if [[ -d /afs/cern.ch/sw/lcg ]] && [[ `dnsdomainname` = 'cern.ch' ]] ; then
        export LCGPATH=/afs/cern.ch/sw/lcg/views/LCG_83/x86_64-slc6-gcc49-opt
        # Set up Gaudi + Dependencies
        source /afs/cern.ch/lhcb/software/releases/LBSCRIPTS/LBSCRIPTS_v8r5p7/InstallArea/scripts/LbLogin.sh --cmtconfig x86_64-slc6-gcc49-opt
        # The LbLogin sets VERBOSE to 1 which increases the compilation output. If you want details set this to 1 by hand.
        export VERBOSE=
        source $LCGPATH/setup.sh
        # This path is used below to select software versions
        export FCCSWPATH=/afs/cern.ch/exp/fcc/sw/0.7
        echo "Software taken from $FCCSWPATH and LCG_83"
        # If podio or EDM not set locally already, take them from afs
        if [ -z "$PODIO" ]; then
            export PODIO=$FCCSWPATH/podio/0.3/x86_64-slc6-gcc49-opt
        else
            echo "Take podio: $PODIO"
        fi
        if [ -z "$FCCEDM" ]; then
            export FCCEDM=$FCCSWPATH/fcc-edm/0.3/x86_64-slc6-gcc49-opt
        else
            echo "Take fcc-edm: $FCCEDM"
        fi
        export DELPHES_DIR=$FCCSWPATH/Delphes/3.3.2/x86_64-slc6-gcc49-opt
        export PYTHIA8_DIR=/afs/cern.ch/sw/lcg/releases/LCG_80/MCGenerators/pythia8/212/x86_64-slc6-gcc49-opt
        export PYTHIA8_XML=/afs/cern.ch/sw/lcg/releases/LCG_80/MCGenerators/pythia8/212/x86_64-slc6-gcc49-opt/share/Pythia8/xmldoc
        export PYTHIA8DATA=/afs/cern.ch/sw/lcg/releases/LCG_80/MCGenerators/pythia8/212/x86_64-slc6-gcc49-opt/share/Pythia8/xmldoc
        export HEPMC_PREFIX=$LCGPATH
        
        # add DD4hep
        export inithere=$PWD
        cd $FCCSWPATH/DD4hep/20152311/x86_64-slc6-gcc49-opt
        source bin/thisdd4hep.sh
        cd $inithere
        
        # add Geant4 data files
        source /afs/cern.ch/sw/lcg/external/geant4/10.2/setup_g4datasets.sh
    fi
    add_to_path LD_LIBRARY_PATH $FCCEDM/lib
    add_to_path LD_LIBRARY_PATH $PODIO/lib
    add_to_path LD_LIBRARY_PATH $PYTHIA8_DIR/lib
    add_to_path PYTHONPATH $PODIO/python
elif [[ "$unamestr" == 'Darwin' ]]; then
    platform='Darwin'
    echo "Platform detected: $platform"
    add_to_path DYLD_LIBRARY_PATH $FCCEDM/lib
    add_to_path DYLD_LIBRARY_PATH $PODIO/lib
    add_to_path DYLD_LIBRARY_PATH $PYTHIA8_DIR/lib
    add_to_path PYTHONPATH $PODIO/python
fi

add_to_path CMAKE_PREFIX_PATH $FCCEDM
add_to_path CMAKE_PREFIX_PATH $PODIO
add_to_path CMAKE_PREFIX_PATH $PYTHIA8_DIR
if [ "$DELPHES_DIR" ]; then
    add_to_path CMAKE_PREFIX_PATH $DELPHES_DIR
fi
