import copy
import json
import math
import random

class Tonkadur:
    def generate_instance_of (self, typedef):
        if (typedef['category'] == "boolean"):
            return False
        elif (typedef['category'] == "float"):
            return 0.0
        elif (typedef['category'] == "int"):
            return 0
        elif (typedef['category'] == "rich_text"):
            result = dict()
            result['content'] = []
            result['effect'] = None
            return result
        elif (typedef['category'] == "string"):
            return ""
        elif (typedef['category'] == "list"):
            return dict()
        elif (typedef['category'] == "pointer"):
            return []
        elif (typedef['category'] == "structure"):
            return copy.deepcopy(self.types[typedef['name']])

    def __init__ (self, json_file):
        self.memory = dict()
        self.types = dict()
        self.sequences = dict()
        self.code = []
        self.program_counter = 0
        self.allocated_data = 0
        self.available_choices = []

        with open(json_file, 'r') as f:
            json_content = json.load(f)

            #### INITIALIZE TYPES ##############################################
            for typedef in json_content['structure_types']:
                new_type = dict()

                for field in typedef['fields']:
                    new_type[field['name']] = self.generate_instance_of(field['type'])

                self.types[typedef['name']] = new_type

            #### INITIALIZE VARIABLES ##########################################
            for vardef in json_content['variables']:
                self.memory[vardef['name']] = self.generate_instance_of(vardef['type'])

            #### INITIALIZE SEQUENCES ##########################################
            for seqdef in json_content['sequences']:
                self.sequences[seqdef['name']] = seqdef['line']

            #### INITIALIZE CODE ###############################################
            self.code = json_content['code']


    def compute (self, computation):
        computation_category = computation['category']

        if (computation_category == "add_rich_text_effect"):
            effect = dict()
            effect['name'] = computation['effect']
            effect['parameters'] = []

            for c in computation['parameters']:
                effect['parameters'].append(self.compute(c))

            result = dict()
            result['content'] = []
            result['effect'] = effect

            for c in computation['content']:
                result['content'].append(self.compute(c))

            return result
        elif (computation_category == "cast"):
            origin_type = computation['from']['category']
            target_type = computation['to']['category']
            content = self.compute(computation['content'])

            if (target_type == "string"):
                return str(content)
            elif (target_type == "float"):
                return float(content)
            elif (target_type == "boolean"):
                if (origin_type == "string"):
                    return (content == "true")
                elif (origin_type == "int"):
                    return (content != 0)
            elif (target_type == "int"):
                if (origin_type == "float"):
                    return math.floor(content)
                else:
                    return int(content)
        elif (computation_category == "constant"):
            target_type = computation['type']['category']
            content = computation['value']

            if (target_type == "string"):
                return content
            elif (target_type == "float"):
                return float(content)
            elif (target_type == "boolean"):
                return (content == "true")
            elif (target_type == "int"):
                return int(content)
            else:
                print("Unknown Constant type '" + str(target_type) + "'")
                raise "error"
        elif (computation_category == "if_else"):
            cond = self.compute(computation['condition'])

            if (cond):
                return self.compute(computation['if_true'])
            else:
                return self.compute(computation['if_false'])
        elif (computation_category == "new"):
            address = ".alloc." + str(self.allocated_data)
            self.allocated_data += 1
            self.memory[address] = self.generate_instance_of(computation['target'])
            #print("Allocated " + str(address) + " = " + str(self.memory[address]))

            return [address]
        elif (computation_category == "operation"):
            operator = computation['operator']
            x = self.compute(computation['x'])
            y = self.compute(computation['y']) if ('y' in computation) else None
            if (operator == "divide"):
                if (isinstance(x, int)):
                    return x // y
                else:
                    return x / y
            elif (operator == "minus"):
                return x - y
            elif (operator == "modulo"):
                return x % y
            elif (operator == "plus"):
                return x + y
            elif (operator == "power"):
                return x ** y
            elif (operator == "rand"):
                return random.randint(x, y)
            elif (operator == "times"):
                return x * y
            elif (operator == "and"):
                return x and y
            elif (operator == "not"):
                return not x
            elif (operator == "less_than"):
                return x < y
            elif (operator == "equals"):
                return x == y
            else:
                print("unknown operator " + operator)

        elif (computation_category == "address"):
            result = self.compute(computation['address'])
            if (isinstance(result, list)):
                return result
            else:
                return [result]
        elif (computation_category == "relative_address"):
            base = self.compute(computation['base']).copy()
            base.append(self.compute(computation['extra']))
            return base
        elif (computation_category == "rich_text"):
            result = dict()
            result['effect'] = None
            result['content'] = []
            for c in computation['content']:
                result['content'].append(self.compute(c))

            return result
        elif (computation_category == "newline"):
            result = dict()
            result['effect'] = None
            result['content'] = ['\n']

            return result
        elif (computation_category == "size"):
            target = self.memory
            access = self.compute(computation['reference'])

            for addr in access:
                target = target[addr]

            return len(target)
        elif (computation_category == "value_of"):
            target = self.memory
            access = self.compute(computation['reference'])
            for addr in access:
                #print("Reading " + str(addr) + " of " + str(target))
            #    print("addr = " + str(addr))
                target = target[addr]
            #    if (isinstance(target, list)):
            #        print("That's a list.")
            return target

    def resolve_choice_to (self, line):
        self.available_choices = []
        self.program_counter = line

    def run (self):
        while True:
            #print("\nmemory: " + str(self.memory))
            #print("\nline: " + str(self.program_counter))
            instruction = self.code[self.program_counter]
            instruction_category = instruction['category']
            #print("instruction:" + str(instruction))

            if (instruction_category == "add_choice"):
                self.available_choices.append(
                    [
                        self.compute(instruction['label']),
                        self.compute(instruction['address'])
                    ]
                )
                self.program_counter += 1
            elif (instruction_category == "assert"):
                condition = self.compute(instruction['condition'])

                if (not condition):
                    result = dict()
                    result["category"] = "assert"
                    result["line"] = self.program_counter
                    result["message"] = self.compute(instruction['message'])
                    self.program_counter += 1
                    return result

                self.program_counter += 1
            elif (instruction_category == "display"):
                result = dict()
                result["category"] = "display"
                result["content"] = self.compute(instruction['content'])
                self.program_counter += 1

                return result
            elif (instruction_category == "end"):
                result = dict()
                result["category"] = "end"

                return result
            elif (instruction_category == "event_call"):
                result = dict()
                result["category"] = "event"
                result["name"] = instruction["event"]
                params = []

                for param in instruction['parameters']:
                    params.append(self.compute(param))

                result["parameters"] = params

                self.program_counter += 1
                return result
            elif (instruction_category == "remove"):
                pre_val = self.memory
                current_val = pre_val
                last_access = ""

                for access in self.compute(instruction["reference"]):
                    pre_val = current_val
                    last_access = access
                    current_val = current_val[access]

                #print("Removing " + str(last_access) + " of " + str(pre_val))
                del pre_val[last_access]

                self.program_counter += 1
            elif (instruction_category == "resolve_choices"):
                result = dict()
                result["category"] = "resolve_choices"
                result["choices"] = self.available_choices

                return result
            elif (instruction_category == "set_pc"):
                self.program_counter = self.compute(instruction["value"])
            elif (instruction_category == "set_value"):
                pre_val = self.memory
                current_val = pre_val
                last_access = ""
                #print("Reference:" + str(instruction["reference"]))
                access_full = self.compute(instruction["reference"])
                #print("Writing: " + str(access_full))

                for access in access_full:
                    pre_val = current_val
                    last_access = access
                    #print("Writing " + str(access) + " of " + str(current_val))
                    if (access in current_val):
                        current_val = current_val[access]


                result = self.compute(instruction["value"])

                if (isinstance(result, list) or isinstance(result, dict)):
                    result = copy.deepcopy(result)

                pre_val[last_access] = result

                self.program_counter += 1

