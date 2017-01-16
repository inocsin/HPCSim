#coding:utf-8
"""
This script automaticly create ned file and header for m port n tree fat tree topology
"""

class fatTree(object):

    def __init__(self, port, level, delay, datarate):
        self.port = port  # port number
        self.level = level  # level number n
        self.processor = 2 * (port / 2) ** level  # number of processor
        self.switch = (2 * level - 1) * (port / 2) ** (level - 1)  # switch number
        self.switchTop = (port / 2) ** (level - 1)  # number of switches in the top level
        self.switchLower = self.switch - self.switchTop  # number of lower switch
        self.switchLowerEach = self.switchLower / (self.level - 1)  # number of switches in each lower layer
        self.delay = delay  # ns
        self.datarate = datarate  # Gbps

    def debugPrint(self):
        print "********************** this is debug message ******************************"
        print "port number = %d, level number = %d, processor node = %d, switch count = %d"%(self.port, self.level, self.processor, self.switch)

    def ppid2plid(self, ppid):
        idtmp = ppid
        idfinal = 0
        mul = 1
        for j in range(self.level-1):
            idfinal = idfinal + idtmp % (self.port / 2) * mul
            mul = mul * 10
            idtmp = (int) (idtmp / (self.port / 2))
        idfinal = idfinal + idtmp * mul
        return idfinal

    def plid2ppid(self, plid):
        tmp = plid
        mul = 1
        IDtmp = 0
        for j in range(self.level):
            IDtmp = IDtmp + mul * (tmp % 10)
            mul = mul * (self.port / 2)
            tmp = tmp / 10
        return IDtmp

    def swpid2swlid(self, swpid):
        # 首先判断i在哪一层
        level = 0
        find_level = False
        for j in range(self.level - 1):
            if swpid >= j * self.switchLowerEach and swpid < (j + 1) * self.switchLowerEach:
                level = j
                find_level = True
                break
        if not find_level:
            level = self.level - 1
        # 已经找到switch所在层，接下来对其进行编码
        # 先对非顶层的switch进行编码
        if level < self.level - 1:
            tmp = swpid - level * self.switchLowerEach
            IDtmp = 0
            mul = 1
            for j in range(self.level - 2):
                IDtmp = mul * (tmp % (self.port / 2)) + IDtmp
                tmp = (int) (tmp / (self.port / 2))
                mul = mul * 10
            IDtmp = IDtmp + mul * tmp
            mul = mul * 10
            IDtmp = mul * level + IDtmp  # 最前面加上它的层数
            return IDtmp
        # 接下来对顶层的switch进行操作
        else:
            tmp = swpid
            IDtmp = 0
            mul = 1
            for j in range(n-1):
                IDtmp = mul * (tmp % (self.port / 2)) + IDtmp
                tmp = (int) (tmp / (self.port / 2))
                mul = mul * 10
            IDtmp = mul * level + IDtmp
            return IDtmp

    def swlid2swpid(self, swlid):
        tmp = swlid
        level = tmp / (10 ** (self.level - 1))
        tmp = tmp % (10 ** (self.level - 1))
        IDtmp = level * self.switchLowerEach
        mul = 1
        for j in range(self.level-1):
            IDtmp = IDtmp + mul * (tmp % 10)
            mul = mul * (self.port / 2)
            tmp = tmp / 10
        return IDtmp

    def printPortId(self):
        portString = [""] * self.port
        for i in range(self.port):
            portString[i] = "inout port_" + str(i) + ';'
            #print "inout port_%d;"%i
        return portString

    def printProcessorConnection(self):
        processorString = [""] * self.processor
        for i in range(self.processor):
            ppid = i
            plid = self.ppid2plid(ppid)
            l = 0
            c = plid / 10
            k = plid % 10
            swlid = l * (10 ** self.level) + c
            swpid = self.swlid2swpid(swlid)
            #print swlid,swpid
            #print "processor[%d].port <--> Channel <--> router[%d].port_%d;"%(ppid, swpid, k)
            processorString[i] = "processor[" + str(ppid) +"].port <--> Channel <--> router[" + str(swpid) + "].port_" + str(k) + ";"
        return processorString

    def printSwitchConnection(self):
        switchString = []
        for i in range(self.switch-self.switchTop):
            swpid = i
            swlid = self.swpid2swlid(swpid)
            l = swlid / (10 ** (self.level - 1))
            l2 = l + 1
            #print swpid,swlid,l,l2
            c = swlid % (10 ** (self.level - 1))
            k2 = (c / (10 ** l)) % 10
            #print c,k2
            for j in range(self.port / 2, self.port):
                k = j
                cl2 = k - self.port / 2
                #print k,cl2
                c2 = c % (10 ** l) + cl2 * (10 ** l) + c / (10 ** (l + 1)) * (10 ** (l + 1))
                swlid2 = l2 * (10 ** (self.level - 1)) + c2
                swpid2 = self.swlid2swpid(swlid2)
                #print "swpid:%d, swlid:%d, port:%d --> swpid2:%d, swlid2:%d, port:%d"%(swpid,swlid,k,swpid2,swlid2,k2)
                #print "router[%d].port_%d <--> Channel <--> router[%d].port_%d;"%(swpid, k, swpid2, k2)
                switchString.append("router[" + str(swpid) + "].port_" + str(k) + " <--> Channel <--> router[" + str(swpid2) + "].port_" + str(k2) + ";")
        return switchString



    def createNed(self):
        nedfile = open("fat_tree_simple.ned",'w')
        # write router
        nedfile.write("simple Router\n")
        nedfile.write("{\n")
        nedfile.write("\tparameters:\n")
        nedfile.write("\n")
        nedfile.write("\tgates:\n")

        portstr = self.printPortId()
        for i in range(len(portstr)):
            nedfile.write("\t\t" + portstr[i] + "\n")

        nedfile.write("}\n")

        # write processor
        nedfile.write("simple Processor\n")
        nedfile.write("{\n")
        nedfile.write("\tparameters:\n")
        nedfile.write("\n")
        nedfile.write("\tgates:\n")
        nedfile.write("\t\tinout port:\n")
        nedfile.write("}\n")


        # writre fat_tree
        nedfile.write("network Fat_tree_simple\n")
        nedfile.write("{\n")
        nedfile.write("\ttypes:\n")
        nedfile.write("\t\tchannel Channel extends ned.DatarateChannel\n")
        nedfile.write("\t\t{\n")
        nedfile.write("\t\t\tdelay = " + str(self.delay) + "ns;\n")
        nedfile.write("\t\t\tdatarate = " + str(self.datarate) + "Gbps;\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\tsubmodules:\n")
        nedfile.write("\t\trouter[" + str(self.switch) + "]: Router {\n")
        nedfile.write("\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\t\tprocessor[" + str(self.processor) + "]: Processor{\n")
        nedfile.write("\n")
        nedfile.write("\t\t}\n")
        nedfile.write("\tconnections:\n")

        procstr = self.printProcessorConnection()
        for i in range(len(procstr)):
            nedfile.write("\t\t" + procstr[i] + "\n")

        switchstr = self.printSwitchConnection()
        for i in range(len(switchstr)):
            nedfile.write("\t\t" + switchstr[i] + "\n")

        nedfile.write("}\n")


        nedfile.close()

# main function
fattree = fatTree(4, 3, 1, 10)
fattree.createNed()
#print fattree.printPortId()
