#! /usr/bin/env python3

# Copyright (c) 2017 Dave McCoy (dave.mccoy@cospandesign.com)
#
# NAME is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# NAME is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAME; If not, see <http://www.gnu.org/licenses/>.


import sys
import os
import argparse
import parse_hwh

from diagrams import Diagram
from diagrams import Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB



#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

NAME = os.path.basename(os.path.realpath(__file__))

DESCRIPTION = "\n" \
              "\n" \
              "usage: %s [options]\n" % NAME

EPILOG = "\n" \
         "\n" \
         "Examples:\n" \
         "\tSomething\n" \
         "\n"

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

    parser.add_argument("hwh",
                        nargs=1,
                        default=["demo"])

    parser.add_argument("-t", "--test",
                        nargs=1,
                        default=["something"])

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable Debug Messages")

    args = parser.parse_args()
    print ("Running Script: %s" % NAME)


    if args.debug:
        print ("test: %s" % str(args.test[0]))


    hwh = args.hwh[0]
    HWH_class = parse_hwh.find_architecture(hwh)
    if HWH_class is None:
        print ("No valid Architecture found")
        return
    h = HWH_class(hwh)
    print ("Dir: %s" % dir(h))

    #for mkey in h.ip_dict:
    # Create a link between AXI Cores Dictionary
    axis_dict = {}
    for it in h.root.iter('MODULE'):
        name = it.get('FULLNAME')
        print ("Key: %s" % name)
        bi = it.find('BUSINTERFACES')
        if bi is None:
            continue

        for b in bi.iter('BUSINTERFACE'):
            bus_type = b.get('VLNV')
            bus_dir = b.get('TYPE')
            bus_name = b.get('BUSNAME')
            #print ("Bus Interfaces: %s" % bus_type)

            if ":axis:" not in bus_type:
                continue

            print ("  AXIS: %s:%s" % (bus_name, bus_dir))
            if name not in axis_dict:
                axis_dict[name] = {}
                axis_dict[name]["TARGET"] = []
                axis_dict[name]["INITIATOR"] = []
                axis_dict[name]["MONITOR"] = []

            axis_dict[name][bus_dir].append(bus_name)


    print ("AXIS Dict")
    for key in axis_dict:
        print ("%s: %s" % (key, str(axis_dict[key])))

    diagram_dict = {}

    for key in axis_dict:
        diagram_dict[key] = {}
        diagram_dict[key]["TARGET"] = {}
        diagram_dict[key]["INITIATOR"] = {}
        diagram_dict[key]["MONITOR"] = {}

    for tcore_name in axis_dict:

        # Connect targets to initiators
        if len(axis_dict[tcore_name]["TARGET"]) > 0:
            for target_bus_name in axis_dict[tcore_name]["TARGET"]:
                for icore_name in axis_dict:
                    for initiator_bus_name in axis_dict[icore_name]["INITIATOR"]:
                        if target_bus_name == initiator_bus_name:
                            #print ("Found a link between: %s -> %s" % (icore_name, tcore_name))
                            diagram_dict[icore_name]["TARGET"][target_bus_name] = [tcore_name]
                            diagram_dict[tcore_name]["INITIATOR"][target_bus_name] = [icore_name]

        if len(axis_dict[tcore_name]["MONITOR"]) > 0:
             for monitor_bus_name in axis_dict[tcore_name]["MONITOR"]:
                for icore_name in axis_dict:
                    for initiator_bus_name in axis_dict[icore_name]["INITIATOR"]:
                        if monitor_bus_name == initiator_bus_name:
                            #print ("Found a link between: %s -> %s" % (icore_name, tcore_name))
                            if monitor_bus_name not in diagram_dict[icore_name]["MONITOR"]:
                                diagram_dict[icore_name]["MONITOR"][monitor_bus_name] = []

                            diagram_dict[icore_name]["MONITOR"][monitor_bus_name].append(tcore_name)
                            diagram_dict[tcore_name]["INITIATOR"][monitor_bus_name] = [tcore_name]

    #print ("Diagram Dictionary: %s" % str(diagram_dict))

    ordered_diagram_dict = {}
    core_list = diagram_dict.keys()
    ordered_core_list = []
    for name in core_list:
        if len(diagram_dict[name]["INITIATOR"]) > 0:
            ordered_core_list.append(name)
        else:
            ordered_core_list.insert(0, name)

    for name in ordered_core_list:
        ordered_diagram_dict[name] = diagram_dict[name]


    print ("Ordered Diagram Dictionary: %s" % str(ordered_diagram_dict))



    with Diagram("AXIS Map", show=False):
        CORE_TYPE = ELB
    #    MONITOR_TYPE = EC2
        for key in ordered_diagram_dict:
            ordered_diagram_dict[key]["NODE"] = CORE_TYPE(key)

        for key in ordered_diagram_dict:
            node = ordered_diagram_dict[key]["NODE"]
            targets = ordered_diagram_dict[key]["TARGET"]
            monitors = ordered_diagram_dict[key]["MONITOR"]
            if (len(targets) == 0) and (len(monitors) == 0):
                continue

            for edge_name in targets:
                for target_name in targets[edge_name]:
                    tnode = ordered_diagram_dict[target_name]["NODE"]
                    node >> Edge(label=edge_name) >> tnode

            for edge_name in monitors:
                for monitor_name in monitors[edge_name]:
                    tnode = ordered_diagram_dict[monitor_name]["NODE"]
                    node >> Edge(label=edge_name, color="firebrick", style="dashed") >> tnode



    #    #ELB("Interrconnect")
    #    #EC2("Core")
    #    #ELB("lb") >> EC2("web") >> RDS("userdb")
    #    pass

if __name__ == "__main__":
    main(sys.argv)


