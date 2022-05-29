
class NODE_EDITOR_BASE(object):

    node_editor = None
    def __init__(self, node_editor):
        self.node_editor = node_editor

    def update_nodes(self):
        pass

    def add_node(self):
        pass

    def add_link(self):
        pass

    def remove_link(self):
        pass

    def get_nodes(self):
        pass
