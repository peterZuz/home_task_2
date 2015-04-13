import sys
import time
from xml.etree.ElementTree import ElementTree
import c_module

def get_data_from_xml(xml_file_name):
    with open(xml_file_name, 'r') as xml_file:
        elem_tree = ElementTree()
        elem_tree.parse(xml_file)

    num_net = len(elem_tree.getroot().findall('net'))
    start_matrix = [[float('inf') for j in range(num_net)] for i in range(num_net)]

    for d in elem_tree.getroot().findall('diode'):
            i = int(d.attrib['net_from']) - 1
            j = int(d.attrib['net_to']) - 1
            start_matrix[i][j] = 1/(1/start_matrix[i][j] + 1/float(d.attrib['resistance']))
            start_matrix[j][i] = 1/(1/start_matrix[j][i] + 1/float(d.attrib['reverse_resistance']))

    for r in elem_tree.getroot().findall('resistor'):
            i = int(r.attrib['net_from']) - 1
            j = int(r.attrib['net_to']) - 1
            start_matrix[i][j] = 1/(1/start_matrix[i][j] + 1/float(r.attrib['resistance']))
            start_matrix[j][i] = 1/(1/start_matrix[j][i] + 1/float(r.attrib['resistance']))

    for c in elem_tree.getroot().findall('capactor'):
            i = int(c.attrib['net_from']) - 1
            j = int(c.attrib['net_to']) - 1
            start_matrix[i][j] =  1/(1/start_matrix[i][j] + 1/float(c.attrib['resistance']))
            start_matrix[j][i] =  1/(1/start_matrix[j][i] + 1/float(c.attrib['resistance']))

    return num_net, start_matrix


def resist_calculation(num_net, start_matrix):
    final_matrix = [[float('inf') for j in range(num_net)] for i in range(num_net)]
    for i in range(num_net):
        final_matrix[i][i] = 0

    for i in range(num_net):
        for j in range(num_net):
            try:
                final_matrix[i][j] = 1/(1/final_matrix[i][j] + 1/start_matrix[i][j])
            except ZeroDivisionError:
                if start_matrix[i][j] == 0 or final_matrix[i][j] == 0:
                    final_matrix[i][j] = 0

    for k in range(num_net):
        for i in range(num_net):
            for j in range(num_net):
                try:
                    final_matrix[i][j] = 1/(1/final_matrix[i][j] + 1/(final_matrix[i][k] + final_matrix[k][j]))
                except ZeroDivisionError:
                    if final_matrix[i][j] == 0 or final_matrix[i][k] == 0 or final_matrix[k][j] == 0:
                        final_matrix[i][j] = 0

    return final_matrix


def c_resist_calculation(num_net, start_matrix):
    final_matrix = [[float('inf') for j in range(num_net)] for i in range(num_net)]
    for i in range(num_net):
        final_matrix[i][i] = 0

    for i in range(num_net):
        for j in range(num_net):
            try:
                final_matrix[i][j] = 1/(1/final_matrix[i][j] + 1/start_matrix[i][j])
            except ZeroDivisionError:
                if start_matrix[i][j] == 0 or final_matrix[i][j] == 0:
                    final_matrix[i][j] = 0

    final_matrix = c_module.calc(final_matrix)

    return final_matrix



def export_data_to_csv(csv_file_name, size, matrix):
    with open(csv_file_name, 'w') as csv_file:
        for i in range(size):
            for j in range(size):
                print("%.6f" % (matrix[i][j]), end=',', file=csv_file)
            print('\n', end='', file=csv_file)
    return


def clear_py_calc(file_input, file_output):
    start_t = time.time()

    num_net, start_matrix = get_data_from_xml(file_input)
    final_matrix = resist_calculation(num_net, start_matrix)
    export_data_to_csv(file_output, num_net, final_matrix)

    finish_t = time.time()

    return (finish_t - start_t)


def calc_with_c(file_input, file_output):
    start_t = time.time()

    num_net, start_matrix = get_data_from_xml(file_input)
    final_matrix = c_resist_calculation(num_net, start_matrix)
    export_data_to_csv(file_output, num_net, final_matrix)

    finish_t = time.time()

    return (finish_t - start_t)

def main(file_input, file_output):
    py_time = clear_py_calc(file_input, file_output)
    c_time = calc_with_c(file_input, file_output)

    if (c_time == 0 and py_time == 0):
        return 1
    elif(py_time == 0):
        return float('inf')

    return c_time/py_time


if __name__ == "__main__":
    output = main(sys.argv[1],sys.argv[2])
    print(output)
