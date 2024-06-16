import argparse
import ollama
import time
import sys
import os
import re

sys.path.insert(1, os.path.join(os.path.dirname(__file__), "CompetitionTemplate", "command_generator"))
import gpsr_commands
import generator as generator_utils

def postprocess_generated(task):
    if task.count('"') == 2:
        return task.split('"')[1]
    
    return task

def get_numlines(path):
    if not os.path.exists(path):
        return 0
    
    with open(path, "r") as f:
        return f.read().count("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--output",
        help = "File to append tasks to",
        required = True,
        type = os.path.abspath
    )
    parser.add_argument(
        "-n", "--numtasks",
        help = "Number of tasks to create",
        required = True,
        type = int
    )
    parser.add_argument(
        "-oh", "--ollamahost",
        help = "IP address of the computer running ollama",
        default = "127.0.0.1",
        type = str
    )     
    args = vars(parser.parse_args())

    ollama_api_url = "%s:11434" % args["ollamahost"]

    model_name = "instructionrephraser:" + str(int(time.time()))
    client = ollama.Client(host = "http://%s" % ollama_api_url)

    for mn in [m["name"] for m in client.list()["models"]]:
        if mn.startswith("instructionrephraser"):
            client.delete(mn)

    with open("Modelfile", "r") as f:
        client.create(model = model_name, modelfile = f.read())

    names_file_path = os.path.join(os.path.dirname(__file__), "CompetitionTemplate", "names", "names.md")
    locations_file_path = os.path.join(os.path.dirname(__file__), "CompetitionTemplate", "maps", "location_names.md")
    rooms_file_path = os.path.join(os.path.dirname(__file__), "CompetitionTemplate", "maps", "room_names.md")
    objects_file_path = os.path.join(os.path.dirname(__file__), "CompetitionTemplate", "objects", "test.md")

    names_data = generator_utils.read_data(names_file_path)
    names = generator_utils.parse_names(names_data)

    locations_data = generator_utils.read_data(locations_file_path)
    location_names, placement_location_names = generator_utils.parse_locations(locations_data)

    rooms_data = generator_utils.read_data(rooms_file_path)
    room_names = generator_utils.parse_rooms(rooms_data)

    objects_data = generator_utils.read_data(objects_file_path)
    object_names, object_categories_plural, object_categories_singular = generator_utils.parse_objects(objects_data)

    generator = gpsr_commands.CommandGenerator(names, location_names, placement_location_names, room_names, object_names, object_categories_plural, object_categories_singular)

    while get_numlines(args["output"]) < args["numtasks"]:
        task = generator.generate_command_start(cmd_category="")
        print('Original: "%s"' % task)
        rephrased = postprocess_generated(client.generate(model = model_name, prompt = task)["response"])
        print('\nRephrased: "%s"' % rephrased)

        if input("\nIs this a valid rephrasing? <y/n>: ").strip().lower() == "y":
            with open(args["output"], "a") as f:
                f.write("%s\t%s\n" % (task, rephrased))
        print("======")