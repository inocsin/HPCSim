#!/bin/bash
SIMULATION_HOME =
SCRIPT_HOME = `pwd`
echo "SIMUALTION_HOME is ${SIMULATION_HOME}"
echo "SCRIPT_HOME is ${SCRIPT_HOME}"
PassThroughLatency=(100 200)
InjectionRate=(0.1 0.3 0.5 0.7 0.9 1.0 1.3)
for latency in ${PassThroughLatency[@]}
do
    for injection in ${InjectionRate[@]}
    do
        #echo $latency
        #echo $injection
        python $SCRIPT_HOME/FatTreeAuto.py --injection_rate=$injection --pass_through_latency=$latency
        rm $SIMUALTION_HOME/fat_tree.h $SIMUALTION_HOME/topoconfig.h $SIMUALTION_HOME/fat_tree.ned
        mv $SCRIPT_HOME/result/fat_tree.h $SCRIPT_HOME/result/topoconfig.h $SCRIPT_HOME/result/fat_tree.ned $SIMULATION_HOME
        cd $SIMULATION_HOME
        make MODE=debug CONFIGNAME=gcc-debug all
        ./hpcsimulator -r 0 -u Cmdenv -c FatTree --debug-on-errors=true omnetpp.ini
        mv results/FatTree-#0.sca $SCRIPT_HOME/result/"FatTree_i${injection}_l${latency}.sca"
    done
done
