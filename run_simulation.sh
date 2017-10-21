#!/bin/bash
SIMULATION_HOME=/home/zhangyi/omnetpp-5.1.1/samples/hpcsimulator
SCRIPT_HOME=/home/zhangyi/HPCSim 
echo "SIMUALTION_HOME is ${SIMULATION_HOME}"
echo "SCRIPT_HOME is ${SCRIPT_HOME}"
PassThroughLatency=(50 100 200 300 500 800)
#PassThroughLatency=(100)
InjectionRate=(0.1 0.2 0.3 0.4 0.5 0.6 0.65 0.7 0.75 0.8 0.85 0.9 0.95 1.0)
#InjectionRate=(0.1)
LinkLatency=(5)
Baseline=(0 1)
Buffer=(32)
Datarate=(0 16 32 64 128 256 512 1024)

for datarate in ${Datarate[@]}
do
    for injection in ${InjectionRate[@]}
    do
		echo "cd $SCRIPT_HOME"
		cd $SCRIPT_HOME
		echo "python $SCRIPT_HOME/FatTreeAuto.py  --injection_rate=$injection --pass_through_latency=0 --link_latency=5 --baseline=0 --buffer=32 --freq=3500000000 --datarate=$datarate"
        python $SCRIPT_HOME/FatTreeAuto.py  --injection_rate=$injection --pass_through_latency=0 --link_latency=5 --baseline=0 --buffer=32 --freq=3500000000 --datarate=$datarate
        echo "rm $SIMULATION_HOME/fat_tree_topo.h $SIMULATION_HOME/topoconfig.h $SIMULATION_HOME/fat_tree.ned $SIMULATION_HOME/omnetpp.ini"
        rm $SIMULATION_HOME/fat_tree_topo.h $SIMULATION_HOME/topoconfig.h $SIMULATION_HOME/fat_tree.ned $SIMULATION_HOME/omnetpp.ini
        echo "mv $SCRIPT_HOME/result/fat_tree.h $SCRIPT_HOME/result/topoconfig.h $SCRIPT_HOME/result/fat_tree.ned $SIMULATION_HOME"
        mv $SCRIPT_HOME/result/fat_tree_topo.h $SCRIPT_HOME/result/topoconfig.h $SCRIPT_HOME/result/fat_tree.ned $SCRIPT_HOME/result/omnetpp.ini $SIMULATION_HOME
        echo "cd $SIMULATION_HOME"
        cd $SIMULATION_HOME
        echo "make MODE=release CONFIGNAME=gcc-release all"
        make MODE=release CONFIGNAME=gcc-release all
        echo "./hpcsimulator -r 0 -u Cmdenv -c FatTree --debug-on-errors=true omnetpp.ini"
        ./hpcsimulator -r 0 -u Cmdenv -c FatTree --debug-on-errors=true omnetpp.ini
        echo "mv results/FatTree-#0.sca $SCRIPT_HOME/data/"FatTree_d${datarate}_i${injection}.sca""
        mv results/FatTree-#0.sca $SCRIPT_HOME/data/"FatTree_d${datarate}_i${injection}.sca"
    done
done
