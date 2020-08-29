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

def display_rich_text (rich_text):
    str_content = ""

    if (not (rich_text['effect'] is None)):
        str_content += "{(" + str(rich_text['effect']) + ") "

    for c in rich_text['content']:
        if (isinstance(c, str)):
            str_content += c
        else:
            str_content += display_rich_text(c)

    if (not (rich_text['effect'] is None)):
        str_content = "}"
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
            print(display_rich_text(result['content']))
        elif (result_category == "assert"):
            print("Assert failed at line " + str(result['line']) + ":" + str(display_rich_text(result['message'])))
            print(str(state.memory))
        elif (result_category == "resolve_choices"):
            current_choice = 0;

            for choice in result['choices']:
                print(str(current_choice) + ". " + display_rich_text(choice[0]))
                current_choice += 1

            user_choice = input("Your choice? ")
            state.resolve_choice_to(result['choices'][int(user_choice)][1])
        elif (result_category == "event"):
            print("Unhandled event:" + str(result))

except:
    print("failed.\n")
    print(str(state.memory))
    raise
print(str(state.memory))
