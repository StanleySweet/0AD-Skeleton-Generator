"""Allow basic operations with XML"""
import xml.etree.ElementTree as ET
import os

COLLADA_SCHEMA_TEXT = "{http://www.collada.org/2005/11/COLLADASchema}"
INPUT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + "/input/"
OUTPUT_DIRECTORY = os.path.dirname(os.path.realpath(__file__)) + "/output/"

TREE = 0
ROOT = 0

def generate_skeletons_blender(input_dir, output_dir):
    """ Generate a skeleton for every file in the input folder """
    for file in get_dae_files():
        global TREE
        global ROOT
        global INPUT_DIRECTORY
        global OUTPUT_DIRECTORY
        INPUT_DIRECTORY = input_dir
        OUTPUT_DIRECTORY = output_dir
        TREE = ET.parse(INPUT_DIRECTORY + file)
        ROOT = TREE.getroot()
        save_skeleton_file()

def generate_skeletons():
    """ Generate a skeleton for every file in the input folder """
    for file in get_dae_files():
        global TREE
        global ROOT
        TREE = ET.parse(INPUT_DIRECTORY + file)
        ROOT = TREE.getroot()
        save_skeleton_file()

def get_dae_files():
    """ Returns a list of dae files in the input directory """
    files = []
    for file in os.listdir(INPUT_DIRECTORY):
        if ".dae" not in file:
            continue
        files.append(file)
    return files

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
    return node.attrib.get("name")

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
    if "IK" in xml_node_root.attrib['id']:
        return ""

    return ("<bone name=\"" + xml_node_root.attrib["name"].replace(get_armature_name() + '_', '')
            + "\">" + get_sub_nodes(xml_node, "./")
            + "</bone>")

def recursive_load_target(xml_node, xml_node_root):
    """Recursively load all nodes"""
    if is_a_skeleton_node(xml_node_root):
        return ""

    if "prop" in xml_node_root.attrib['id']:
        return ""
    if "IK" in xml_node_root.attrib['id']:
        return ""
    return ("<bone name=\"" + xml_node_root.attrib["name"].replace(get_armature_name() + '_', '') 
            + "\"><target>"+ xml_node_root.attrib["name"].replace(get_armature_name() + '_', '') + "</target>"
            + get_sub_nodes_target(xml_node, "./")
            + "</bone>")

def write_xml():
    """Returns the skeleton xml string"""
    string = "<?xml version='1.0' encoding='utf8'?>"
    string += "<skeletons>"
    string += "<standard_skeleton title=\""+ get_armature_name().replace("_", " ") + "\" id=\""
    string += get_armature_name().replace(" ", "_") +"\">"
    string += get_skeleton_bones(recursive_load)
    string += "</standard_skeleton>"
    string += "<skeleton title=\""+ get_armature_name().replace('_', ' ') + "\" target=\""
    string += get_armature_name().replace(" ", "_") + "\">"
    string += "<identifier><root>" + get_root_bone().replace(get_armature_name() + '_', '') + "</root></identifier>"
    string += get_skeleton_bones(recursive_load_target)
    string += "</skeleton>"
    string += "</skeletons>"
    return string

def save_skeleton_file():
    """Save the final skeleton file"""
    file_tree = ET.fromstring(write_xml())
    indent(file_tree)
    document = ET.ElementTree(file_tree)
    document.write(OUTPUT_DIRECTORY + get_armature_name() + ".xml", encoding='utf-8', xml_declaration=True, short_empty_elements=True)
    print("Done generating file: " + OUTPUT_DIRECTORY + get_armature_name() +".xml")

def get_root_bone():
    """Get the root bone """
    nodes = ROOT.findall(COLLADA_SCHEMA_TEXT + "library_visual_scenes/" +
                         COLLADA_SCHEMA_TEXT + "visual_scene/" +
                         COLLADA_SCHEMA_TEXT + "node/")

    for node in nodes:
        if is_a_skeleton_node(node):
            continue

        return node.attrib["name"]

    return ""

def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

generate_skeletons()
