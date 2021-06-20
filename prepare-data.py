import sys
import random

maps = {} # dictionary that contains each attribute as key and their own mapping dictionary as value
attributes_list = [] # list of all atributes
seed = "54198" # default seed for random module


# Check if user has provided the correct arguments when executing the script
def check_arguments():
    # Show correct usage if there aren't enough arguments
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        print("Not enough aguments provided, correct use:")
        print("\tpython3 " + sys.argv[0] + " original_data.csv  train_file.arff test_file.arff (random_seed)")
        exit()

    # Open provided files
    data = []
    with open(sys.argv[1]) as original_data:
        data = original_data.readlines()

    train_file = open(sys.argv [2], "w")
    test_file = open(sys.argv [3], "w")

    # Get seed for random module from arguments if it was provided
    if len(sys.argv) == 5:
        global seed
        seed = sys.argv[4]

    return data, train_file, test_file


# Create dictionaries for each attribute to later store their real value to discrete value mapping
def generate_empty_maps(data):
    global attributes_list

    # get all atributes from the first line of the csv
    attributes_list = data[0].split(",") 

    # remove the newline caracter (\n) from the end of each line
    attributes_list[-1] = attributes_list[-1].strip() 

    # create an empty dictionary for each attribute
    for att in attributes_list:
        maps[att] = {}  


# prepare the data in the csv file before writing the arff files, 
# mapping all real values to discrete values for each attribute
def prepare_data(data):
    # for each line:
    for line in data[1:]:
        split_line = line.split(",")
        split_line[-1] = split_line[-1].rstrip("\n")

        # for each attribute value in the line:
        for i in range(len(split_line)):
            # get the corresponding attribute dictionary
            attribute_map = maps.get(attributes_list[i])

            # map the value to themselves if it's a discrete value 
            # or else map it to 0
            if i == len(split_line)-1:
                attribute_map[split_line[i]] = int(split_line[i])
            else:
                attribute_map[split_line[i]] = 0

    # update all values that were mapped to 0 to another number
    map_real_to_discrete_values()


# for each map, assign a better mapping value to those that were 0
# the new values will be an ascending order list for example
# the dictionary for Na should be:
# {'13.64': 1, '13.89': 2, '13.53': 3, '13.21': 4, '13.27': 5, ...}
def map_real_to_discrete_values():
    for attr in attributes_list[:-1]:
        attr_map = maps.get(attr)
        discrete_value = 1
        for key in attr_map.keys():
            attr_map[key] = discrete_value
            discrete_value += 1


# write the corresponding header in the arff files
def write_header(arff_file):
    # write @RELATION line
    arff_file.write("@RELATION glass\n\n")

    # we treat each attribute as a nominal in oder to use bayes in weka
    #for each attribute:
    for attr in attributes_list:
        attr_map = maps.get(attr)
        attr_keys = attr_map.keys()
       
        # get all possible values for each atribute to list them in the header
        values = ""
        for key in attr_keys:
            values += str(attr_map[key]) + ","
        values = values[:-1]

        # write @ATTRIBUTE line
        arff_file.write("@ATTRIBUTE " + attr +" {"+ values +"}\n")


# write the data in the arff files replacing all the real values with their mapped values
# for example in the Na case:
# 13.64 -> 1
def write_data(data, train_file, test_file):
    # set the limit of data lines for each file
    lim_75 = int(len(data) * 0.75)
    lim_25 = int(len(data) * 0.25)

    # create a data lines counter for each file
    count_75 = 0
    count_25 = 0

    # set the random module seed
    random.seed(seed)

    # write @DATA line in each file
    train_file.write("\n@DATA\n")
    test_file.write("\n@DATA\n")

    # for each line in the original csv data
    for line in data[1:]:
        split_line = line.split(",")
        split_line[-1] = split_line[-1].rstrip("\n")

        # get a random number in the range [0.0,1.0]
        r = random.random()

        # if r is less than 0.75 and we haven't reached the limit for training lines set above
        # or if r is more than 0.75 but reached the limit for testing lines
        if (r < 0.75 and count_75 < lim_75) or (r >= 0.75 and count_25 > lim_25):
            lim_75 += 1
            # write the current line in the train file
            write_line(train_file, split_line)
        else:
            lim_25 += 1
            # write the current line in the test file
            write_line(test_file, split_line)
    
    # close files
    train_file.close()
    test_file.close()


# write a line from the original data file mapped to descrete values in a file
def write_line(file, original_line):
    output_line = ""

    #for each attribute value in the line:
    for i in range(len(original_line)):
        # get the corresponding attribute map
        attribute_map = maps.get(attributes_list[i])

        # replace the original value to the mapped one
        attr_discrete_value = attribute_map.get(original_line[i])

        # concatenate with the previous values to create the line
        output_line += str(attr_discrete_value) + ","
    
    # remove last "," added
    output_line = output_line[:-1]

    # set newline caracter at the end of the line
    output_line += "\n"

    # write the line
    file.write(output_line)    
        

# print all the mappings for all the attributes
def print_maps():
    for attr in attributes_list:
        attr_map = maps.get(attr)
        print("Attribute " + attr +": " + str(len(attr_map)))
        print(attr_map)
        print()


if __name__ == "__main__":
    data, train_file, test_file = check_arguments()
    generate_empty_maps(data)
    prepare_data(data)
    write_header(train_file)
    write_header(test_file)
    write_data(data, train_file, test_file)
    # print_maps() # uncoment to see all the mappings of the real values to discrete values