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


import platform
import signal
import sys
import os
import subprocess
import argparse
from os.path import dirname
from pathlib import Path
import numpy as np
import json
import copy
import sys


import dearpygui.dearpygui as dpg

# Tempory, this needs to be selectable
from node_controller_demo import NODE_EDITOR_DEMO

VIEWPORT_TITLE="Node Demo 1"
VIEWPORT_SIZE = (1700, 1000)

MAIN_TITLE      = "Main"
MAIN_SIZE       = (VIEWPORT_SIZE[0] / 4, VIEWPORT_SIZE[1])

EDITOR_TITLE    = "Node Editor"
EDITOR_SIZE     = ((VIEWPORT_SIZE[0] - MAIN_SIZE[0]), VIEWPORT_SIZE[1])


NPE_POS = (370, 30)

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

class DPG_GRAPH:

    nodes_list = []
    links_dict = {}
    panel_coordinates = [0, 0]
    mouse_dragging_deltas = [0, 0]
    forwarders: subprocess.Popen
    node_selector: int
    node_editor = None
    main_window = None
    start_graph_button_id = None
    end_graph_button_id = None
    node_tree = None
    node_editor_tabs = []

    def __init__(self):
        dpg.create_context()

        # Main Window
        with dpg.window(label=MAIN_TITLE, width=MAIN_SIZE[0], height=MAIN_SIZE[1], pos = [0, 0]) as self.main_window:
            dpg.set_primary_window(self.main_window, True)
 
            with dpg.menu_bar(label='Menu Bar'):
                with dpg.menu(label='File'):
                    dpg.add_menu_item(label='New',  callback=self.clear_editor)
                    #dpg.add_menu_item(label='Save', callback=self.save_graph)
                    #dpg.add_menu_item(label='Load', callback=self.load_graph)
                with dpg.menu(label='Operations'):
                    dpg.add_menu_item(label="Add New Folder", callback=self.demo1_callback)

            with dpg.tab_bar(tag="main_bar"):
                with dpg.tab(label="Main View", tag="main_tab"):
                    dpg.add_text("Main")
 
                with dpg.tab(label="Nodes", tag="node_tab"):
                    with dpg.group(horizontal=False):
                        with dpg.group(horizontal=True):
                            self.start_graph_button_id   = dpg.add_button(label="Start Graph",   callback=self.on_start_graph)
                            self.end_graph_button_id     = dpg.add_button(label="End Graph",     callback=self.on_end_graph)
                  
                            with dpg.node_editor(label='Node Editor##Editor',
                                 callback=self.on_link,
                                 delink_callback=self.delete_link) as self.node_editor:
                                 #width = EDITOR_SIZE[0],
                                 #height = EDITOR_SIZE[1] - 100) as self.node_editor:
                                pass
                  
        # Button and mouse callback registers
        with dpg.handler_registry():
            dpg.add_key_press_handler(key=46, callback=self.on_del_pressed)
            dpg.add_mouse_drag_handler(callback=self.on_drag)
            dpg.add_mouse_release_handler(callback=self.on_mouse_release)
              
        self.update_control_graph_buttons(False)
        #self.node_selector = self.create_node_selector_window()
        dpg.set_value("main_bar", "node_tab")
        mb = dpg.get_value("main_bar")

    def add_node_window(self, node_editor_controller):
        mb = dpg.get_item("main_bar")

    '''
    Callbacks
    '''
    def on_mouse_release(self, sender, app_data, user_data):
        self.mouse_dragging_deltas = [0, 0]

    def on_del_pressed(self, sender, key_value):
        indices_to_remove = []
        for node in dpg.get_selected_nodes(node_editor=self.node_editor):
            node_name = dpg.get_item_label(node)
            for i in np.arange(len(nodes_list) - 1, -1, -1):
                if nodes_list[i].name == node_name:
                    indices_to_remove.append(i)

        for i in indices_to_remove:
            node = nodes_list[i]
            for link in node.links_list:
                delete_link(None, link)
            nodes_list[i].remove_from_editor()
            del nodes_list[i]

        for link in dpg.get_selected_links(node_editor=node_editor):
            delete_link(None, link)

    def on_drag(self, sender, data, user_data):
        """
        When mouse is dragged and a node is selected then update that node's coordinates
        When mouse is dragged on the canvas with no node selected then move all nodes by the mouse movement and
        update their coordinates
        :param sender: Not used (the editor window)
        :param data: The mouse drag amount in x and y
        :param user_data: Not used
        :return: Nothing
        """
        #global panel_coordinates
        #global mouse_dragging_deltas

        data = np.array(data)

        # If resizing the node_editor_window then resize the node_editor itself
        height = dpg.get_item_height(node_editor_window)
        width = dpg.get_item_width(node_editor_window)
        dpg.set_item_height(node_editor, height - 40)
        dpg.set_item_width(node_editor, width - 20)

        # If moving a selected node, update the node's stores coordinates
        if np.sum(np.abs(data)) > 0 and len(nodes_list) > 0:
            for sel in dpg.get_selected_nodes(node_editor=node_editor):
                for n in nodes_list:
                    if n.id == sel:
                        n.coordinates = dpg.get_item_pos(sel)

        # If dragging on the canvas with Ctrl pressed then move all nodes and update their stored coordinates
        if len(dpg.get_selected_nodes(node_editor=node_editor)) == 0 and dpg.is_key_down(17):
            move = [data[1] - self.mouse_dragging_deltas[0], data[2] - self.mouse_dragging_deltas[1]]
            self.panel_coordinates = [0, 0]
            self.panel_coordinates[0] = self.panel_coordinates[0] + move[0]
            self.panel_coordinates[1] = self.panel_coordinates[1] + move[1]
            self.mouse_dragging_deltas = [data[1], data[2]]

            for n in nodes_list:
                dpg.set_item_pos(n.id, [n.coordinates[0] + int(move[0]), n.coordinates[1] + int(move[1])])
                n.coordinates = dpg.get_item_pos(n.id)



    def update_control_graph_buttons(self, is_graph_running):
        """
        Used to enable and disable (grey out) the Start Graph or the End Graph according to whether the Graph is running or
        not
        :param is_graph_running: Is the graph running bool
        :return: Nothing
        """
        with dpg.theme() as theme_active:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 50, 180, 255], category=dpg.mvThemeCat_Core)

        with dpg.theme() as theme_non_active:
            with dpg.theme_component(0):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [150, 150, 150, 255], category=dpg.mvThemeCat_Core)

        if is_graph_running:
            dpg.configure_item(self.start_graph_button_id, enabled=False)
            dpg.bind_item_theme(self.start_graph_button_id, theme_non_active)
            dpg.configure_item(self.end_graph_button_id, enabled=True)
            dpg.bind_item_theme(self.end_graph_button_id, theme_active)
        else:
            dpg.configure_item(self.start_graph_button_id, enabled=True)
            dpg.bind_item_theme(self.start_graph_button_id, theme_active)
            dpg.configure_item(self.end_graph_button_id, enabled=False)
            dpg.bind_item_theme(self.end_graph_button_id, theme_non_active)


    def on_end_graph(self, sender, data):
        pass

    def on_start_graph(self, sender, data):
        if self.nodes_list:
            path_to_com = "base"

    def demo1_callback(self):
        pass

    # callback runs when user attempts to connect attributes
    def link_callback(self, sender, app_data):
        # app_data -> (link_id1, link_id2)
        dpg.add_node_link(app_data[0], app_data[1], parent=sender)

    # callback runs when user attempts to disconnect attributes
    def delink_callback(self, sender, app_data):
        # app_data -> link_id
        dpg.delete_item(app_data)


    def on_link(self, sender, link):
        global links_dict

    def delete_link(self, sender, link):
        global links_dict



    '''
    Sub Functions
    '''
    def generate_node_tree(self):
        """
        The function that looks into the Heron/Operations path and creates a list of tuples of
        directories where the first element in the tuple is a dir and the second is
        its parent dir. All names for the dirs are generated (using ## to separate the different
        parts of the node_name) in such a way that can be used by dearpygui (i.e. they are
        unique and the first part before the first ## - which is the one that shows on a widget - is
        descriptive of the dir or the file).
        So one tuple would be ('Transforms##Operations##', 'Vision##Transforms##Operations##') which
        would mean that a dir called Vision (with real node_name Vision##Transforms##Operations##) has as
        its parent dir a dir called Transforms (with real node_name Transforms##Operations##). The list does not include
        the directories that house the actual code (each operation must have its own directory into which any
        python files must exist).
        The returned list can be used in a tree_node widget.
        :return: The list of tuples (parent dir, dir)
        """
        node_dirs = []
        dir_ids = {}
        dir_id = 100000
        return node_dirs


    def create_node_selector_window(self):
        with dpg.window(label='Node Selector', pos=[10, 60], width=300, height=890) as node_selector:
            # Create the window of the Node selector
 
            node_tree = self.generate_node_tree()
            #base_id = node_tree[0][0]
            #base_name = node_tree[0][1]
            #with dpg.tree_node(label=base_name, parent=node_selector, default_open=True, id=base_id, open_on_arrow=True):
 
            #    # Read what *_com files exist in the Heron/Operations dir and sub dirs and create the correct
            #    # tree_node widget
            #    for parent_id, parent, node_id, node in node_tree:
            #        with dpg.tree_node(label=node, parent=parent_id, default_open=True, id=node_id):
            #            for op in operations_list:
            #                if node == op.parent_dir:
            #                    colour = gu.choose_color_according_to_operations_type(node)
            #                    button = dpg.add_button(label=op.name, width=200, height=30, callback=on_add_node)
            #                    with dpg.theme() as theme_id:
            #                        with dpg.theme_component(0):
            #                            dpg.add_theme_color(dpg.mvThemeCol_Button, colour, category=dpg.mvThemeCat_Core)
            #                            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
 
            #                    dpg.bind_item_theme(button, theme_id)
            return node_selector

    # TODO: Add a UI asking the user if they are sure (and that all link will be lost)
    def clear_editor(self):
        """
        Clear the editor of all nodes and links
        :return: Nothing
        """
        if dpg.get_item_children(self.node_editor, slot=1):
            for n in dpg.get_item_children(self.node_editor, slot=1):
                dpg.delete_item(n)
            for a in dpg.get_aliases():
                dpg.remove_alias(a)
        self.nodes_list = []

    def start(self):
        dpg.create_viewport(title=VIEWPORT_TITLE, width=VIEWPORT_SIZE[0], height=VIEWPORT_SIZE[1])
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

def main(argv):
    #Parse out the commandline arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )

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

    g = DPG_GRAPH()
    g.start()

if __name__ == "__main__":
    main(sys.argv)


