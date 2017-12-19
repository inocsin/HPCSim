#!/bin/bash
SIMULATION_HOME=/home/zhangyi/omnetpp-5.1.1/samples/hpcsimulator
SCRIPT_HOME=/home/zhangyi/HPCSim
echo "SIMUALTION_HOME is ${SIMULATION_HOME}"
echo "SCRIPT_HOME is ${SCRIPT_HOME}"
InjectionRate=(0.1 0.2 0.3 0.4 0.5 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95 1.0)
Traffic=(0 1)

for t in ${Traffic[@]}
do
    for injection in ${InjectionRate[@]}
    do
        cd $SCRIPT_HOME
        python $SCRIPT_HOME/SimpleRouterAuto.py --injection_rate=$injection --freq=3500000000 --traffic=$t --hotspot=5.0
        rm $SIMULATION_HOME/topoconfig.h $SIMULATION_HOME/tianhe_router.ned $SIMULATION_HOME/omnetpp.ini
        mv $SCRIPT_HOME/result/topoconfig.h $SCRIPT_HOME/result/tianhe_router.ned $SCRIPT_HOME/result/omnetpp.ini $SIMULATION_HOME
        cd $SIMULATION_HOME
        make MODE=release CONFIGNAME=gcc-release all
        ./hpcsimulator -r 0 -u Cmdenv -c TianheRouter --debug-on-errors=true omnetpp.ini
        mv results/TianheRouter-#0.sca $SCRIPT_HOME/data/"SimpleRouter_t${t}_i${injection}.sca"
    done
done
