#!/bin/bash
SIMULATION_HOME=/home/zhangyi/omnetpp-5.1.1/samples/hpcsimulator 
SCRIPT_HOME=/home/zhangyi/HPCSim 
echo "SIMUALTION_HOME is ${SIMULATION_HOME}"
echo "SCRIPT_HOME is ${SCRIPT_HOME}"
PassThroughLatency=(100 500)
#PassThroughLatency=(100)
InjectionRate=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3)
#InjectionRate=(0.1)
for latency in ${PassThroughLatency[@]}
do
    for injection in ${InjectionRate[@]}
    do
        #echo $latency
        #echo $injection
		echo "cd $SCRIPT_HOME"
		cd $SCRIPT_HOME
		echo "python $SCRIPT_HOME/FatTreeAuto.py --injection_rate=$injection --pass_through_latency=$latency"
        python $SCRIPT_HOME/FatTreeAuto.py --injection_rate=$injection --pass_through_latency=$latency
        echo "rm $SIMULATION_HOME/fat_tree.h $SIMULATION_HOME/topoconfig.h $SIMULATION_HOME/fat_tree.ned"
        rm $SIMULATION_HOME/fat_tree.h $SIMULATION_HOME/topoconfig.h $SIMULATION_HOME/fat_tree.ned $SIMULATION_HOME/omnetpp.ini
        echo "mv $SCRIPT_HOME/result/fat_tree.h $SCRIPT_HOME/result/topoconfig.h $SCRIPT_HOME/result/fat_tree.ned $SIMULATION_HOME"
        mv $SCRIPT_HOME/result/fat_tree.h $SCRIPT_HOME/result/topoconfig.h $SCRIPT_HOME/result/fat_tree.ned $SCRIPT_HOME/result/omnetpp.ini $SIMULATION_HOME
        echo "cd $SIMULATION_HOME"
        cd $SIMULATION_HOME
        echo "make MODE=release CONFIGNAME=gcc-release all"
        make MODE=release CONFIGNAME=gcc-release all
        echo "./hpcsimulator -r 0 -u Cmdenv -c FatTree --debug-on-errors=true omnetpp.ini"
        ./hpcsimulator -r 0 -u Cmdenv -c FatTree --debug-on-errors=true omnetpp.ini
        echo "mv results/FatTree-#0.sca $SCRIPT_HOME/result/"FatTree_l${latency}_i${injection}.sca""
        mv results/FatTree-#0.sca $SCRIPT_HOME/data/"FatTree_i${injection}_l${latency}.sca"
    done
done
