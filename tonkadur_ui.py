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

args = parser.parse_args()
state = tonkadur.Tonkadur(args.world_file)

#try:
while True:
    result = state.run()
    result_category = result['category']

    if (result_category == "end"):
        print("Program ended")
        break
    elif (result_category == "display"):
        print(result['content'])
    elif (result_category == "assert"):
        print("Assert failed at line " + str(result['line']) + ":" + str(result['message']))
    elif (result_category == "resolve_choices"):
        current_choice = 0;

        for choice in result['choices']:
            print(str(current_choice) + ". " + ''.join(choice[0]['content']))
            current_choice += 1

        user_choice = input("Your choice? ")
        state.resolve_choice_to(result['choices'][int(user_choice)][1])
    elif (result_category == "event"):
        print("Unhandled event:" + str(result))

#except Error:
#    print("failed.\n")
print(str(state.memory))
