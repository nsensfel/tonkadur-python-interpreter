import sys
import argparse

import tonkadur

parser = argparse.ArgumentParser(
    description = (
        "Tonkadur Python Interpreter"
    )
)

parser.add_argument(
    '-f',
    '--file',
    dest='world_file',
    type = str,
    help = 'Wyrd JSON file to load.',
)

def display_text (text):
    str_content = ""

    if (not (text['effect'] is None)):
        str_content += "{(" + str(text['effect']) + ") "

    for c in text['content']:
        if (isinstance(c, str)):
            str_content += c
        else:
            str_content += display_text(c)

    if (not (text['effect'] is None)):
        str_content += "}"
    return str_content

args = parser.parse_args()
state = tonkadur.Tonkadur(args.world_file)

try:
    while True:
        result = state.run()
        result_category = result['category']

        if (result_category == "end"):
            print("Program ended")
            break
        elif (result_category == "display"):
            print(display_text(result['content']))
        elif (result_category == "prompt_integer"):
            while True:
                user_input = input(
                    display_text(result['label'])
                    + " "
                    + "["
                    + str(result['min'])
                    + ", "
                    + str(result['max'])
                    + "] "
                )
                user_input = int(user_input)
                if (
                    (user_input >= result['min'])
                    and (user_input <= result['max'])
                ):
                    break
                else:
                    print("Value not within range.")
            state.store_integer(user_input)

        elif (result_category == "prompt_string"):
            while True:
                user_input = input(
                    display_text(result['label'])
                    + " "
                    + "["
                    + str(result['min'])
                    + ", "
                    + str(result['max'])
                    + "] "
                )
                if (
                    (len(user_input) >= result['min'])
                    and (len(user_input) <= result['max'])
                ):
                    break
                else:
                    print("Input size not within range.")
            state.store_string(user_input)

        elif (result_category == "assert"):
            print(
                "Assert failed at line "
                + str(result['line'])
                + ":"
                + str(display_text(result['message']))
            )
            print(str(state.memory))
        elif (result_category == "resolve_choice"):
            current_choice = 0;

            for choice in result['options']:
                if (choice["category"] == "option"):
                    print(
                        str(current_choice)
                        + ". "
                        + display_text(choice["label"])
                    )
                current_choice += 1

            user_choice = input("Your choice? ")
            state.resolve_choice_to(int(user_choice))

except:
    print("failed at line " + str(state.program_counter) + ".\n")
    print(str(state.memory))
    raise
print(str(state.memory))
