"""Allow basic operations with XML"""
import xml.etree.ElementTree as ET
import os

COLLADA_SCHEMA_TEXT = "{http://www.collada.org/2005/11/COLLADASchema}"
FILE_NAME = "E:\\Users\\dolci\\Desktop\\destination_arrows.dae"
TREE = ET.parse(FILE_NAME)
ROOT = TREE.getroot()

def get_bone_names():
    """ Get the name of the bones inside of the dae file. """
    bone_list = []
    node = ROOT.find(COLLADA_SCHEMA_TEXT + "library_controllers/" +
                     COLLADA_SCHEMA_TEXT + "controller/" +
                     COLLADA_SCHEMA_TEXT + "skin/"+
                     COLLADA_SCHEMA_TEXT + "source/"
                    )
    bone_list = node.text.split()
    return bone_list

def get_armature_name():
    "Gets the name of the armature"
    node = ROOT.find(COLLADA_SCHEMA_TEXT + "library_visual_scenes/" +
                     COLLADA_SCHEMA_TEXT + "visual_scene/")
    return node.attrib.get("id")

def is_a_skeleton_node(xml_node):
    """Defines wether the node belongs to the skeleton or not"""
    return not COLLADA_SCHEMA_TEXT + "node" == xml_node.tag

def get_skeleton_bones(recursive_function):
    """ Returns a string in 0ad format containing all the bones with their hierarchy"""
    current_path = (COLLADA_SCHEMA_TEXT + "library_visual_scenes/"
                    + COLLADA_SCHEMA_TEXT + "visual_scene/"
                    + COLLADA_SCHEMA_TEXT + "node/")
    string = ""
    node = ROOT.findall(current_path)
    for subnode in node:
        if is_a_skeleton_node(subnode):
            continue

        string += recursive_function(subnode.findall("./"), subnode)

    return string

def get_sub_nodes(xml_node, xml_node_path):
    """ Returns a string containing the child nodes recursively"""
    subnode_text = ""
    for xml_subnode in xml_node:
        xml_subnodes = xml_subnode.findall(xml_node_path)
        subnode_text += recursive_load(xml_subnodes, xml_subnode)
    return subnode_text

def get_sub_nodes_target(xml_node, xml_node_path):
    """ Returns a string containing the child nodes recursively"""
    subnode_text = ""
    for xml_subnode in xml_node:
        xml_subnodes = xml_subnode.findall(xml_node_path)
        subnode_text += recursive_load_target(xml_subnodes, xml_subnode)
    return subnode_text

def recursive_load(xml_node, xml_node_root):
    """Recursively load all nodes"""
    if is_a_skeleton_node(xml_node_root):
        return ""

    if "prop" in xml_node_root.attrib['id']:
        return ""

    return ("<bone name=\"" + xml_node_root.attrib["id"]
            + "\">\n" + get_sub_nodes(xml_node, "./")
            + "</bone>\n")

def recursive_load_target(xml_node, xml_node_root):
    """Recursively load all nodes"""
    if is_a_skeleton_node(xml_node_root):
        return ""

    if "prop" in xml_node_root.attrib['id']:
        return ""

    return ("<bone name=\"" + xml_node_root.attrib["id"]
            + "\"><target>"+ xml_node_root.attrib["id"] + "</target>\n"
            + get_sub_nodes_target(xml_node, "./")
            + "</bone>\n")

def write_xml():
    """Returns the skeleton xml string"""
    string = "<skeletons>\n"
    string += "<standard_skeleton title=\""+ get_armature_name() + " Skeleton\" id=\""
    string += get_armature_name().replace(" ", "_") +"\">\n"
    string += get_skeleton_bones(recursive_load)
    string += "</standard_skeleton>\n"
    string += "<skeleton title=\""+ get_armature_name() + " Skeleton\" target=\""
    string += get_armature_name() + "\">\n"
    string += "<identifier><root>" + get_root_bone() + "</root></identifier>\n"
    string += get_skeleton_bones(recursive_load_target)
    string += "</skeleton>\n"
    string += "</skeletons>\n"
    return string

def save_skeleton_file():
    """Save the final skeleton file"""
    file_handle = open("./" + get_armature_name() + ".xml", "wb")
    file_tree = ET.fromstring(write_xml())
    ET.ElementTree.write(ET.ElementTree(file_tree), file_handle)
    file_handle.close()
    print("Done generating file: " + os.getcwd() + "\\"+ get_armature_name() +".xml")

def get_root_bone():
    """Get the root bone """
    nodes = ROOT.findall(COLLADA_SCHEMA_TEXT + "library_visual_scenes/" +
                         COLLADA_SCHEMA_TEXT + "visual_scene/" +
                         COLLADA_SCHEMA_TEXT + "node/")

    for node in nodes:
        if is_a_skeleton_node(node):
            continue

        return node.attrib["id"]

    return ""

save_skeleton_file()
