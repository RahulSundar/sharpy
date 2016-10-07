import numpy as np

import beam.beamutils as beamutils
import beam.beamstructures as beamstructures

class Beam(object):
    def __init__(self, fem_dictionary):
        # read and store data
        # type of node
        self.num_node_elem = fem_dictionary['num_node_elem']
        # node coordinates
        self.num_node = fem_dictionary['num_node']
        self.node_coordinates = fem_dictionary['coordinates']
        # element connectivity
        self.num_elem = fem_dictionary['num_elem']
        self.connectivities = fem_dictionary['connectivities']
        # stiffness index of the elems
        self.elem_stiffness = fem_dictionary['elem_stiffness']
        # mass per unit length of elems
        self.elem_mass = fem_dictionary['elem_mass']

        # now, we are going to import the mass and stiffness
        # databases
        self.mass_db = fem_dictionary['mass_db']
        self.stiffness_db = fem_dictionary['stiffness_db']

        # generate the Element array
        self.elements = []
        for ielem in range(self.num_elem):
            self.elements.append(
                beamstructures.Element(
                       ielem,
                       self.num_node_elem,
                       self.connectivities[ielem,:],
                       self.node_coordinates[self.connectivities[ielem,:],:]))

        # now we need to add the attributes like mass and stiffness index
        for ielem in range(self.num_elem):
            dictionary = {}
            dictionary['stiffness_index'] = self.elem_stiffness[ielem]
            dictionary['mass_index'] = self.elem_mass[ielem]
            self.elements[ielem].add_attributes(dictionary)

        # import pdb; pdb.set_trace()
        self.generate_master_structure()

    def generate_master_structure(self):
        '''
        Master-slave relationships are necessary for
        later stages, as nodes belonging to two different
        elements have two different values of their rotation.
        '''
        # let's just keep the outer nodes of the element
        temp_connectivities = np.zeros((self.num_elem, 2),
                                       dtype=int)
        temp_connectivities[:,0] = self.connectivities[:,0]
        temp_connectivities[:,-1] = self.connectivities[:,-1]

        # master_elems contains the index of the master
        # element for every element
        # master_nodes contains the index of the master
        # node belongin to the master element
        # the numbering of the nodes is based on the
        # local one (0, 1 or 2) for a 3-noded element
        self.master_elems = np.zeros(self.num_elem,
                                         dtype = int) - 1
        self.master_nodes = np.zeros_like(self.master_elems,
                                          dtype = int) - 1
        for ielem in range(self.num_elem):
            # import pdb; pdb.set_trace()
            if ielem == 0:
                continue

            temp = temp_connectivities[0:ielem,:]
            elem_nodes = temp_connectivities[ielem,:]
            # case: global master elem
            # (none of the extreme nodes appear in previous
            #  connectivities)
            if not (elem_nodes[0] in temp or
                    elem_nodes[1] in temp):
                continue

            # nodes in elem ielem
            for inode in range(1, -1, -1):
                # previous elements in the list
                for iielem in range(ielem):
                    # nodes of the previous elements in the list
                    for iinode in range(1, -1, -1):
                        # connectivity already found
                        if not self.master_elems[ielem] == -1:
                            continue
                        if elem_nodes[inode] == temp_connectivities[iielem, iinode]:
                            # found a repeated connectivity
                            self.master_elems[ielem] = iielem
                            if iinode == 0:
                                self.master_nodes[ielem] = iinode
                            elif iinode == 1:
                                self.master_nodes[ielem] = self.num_node_elem


        import pdb; pdb.set_trace()

