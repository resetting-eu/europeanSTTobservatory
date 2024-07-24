from deep_translator import GoogleTranslator
import json

source_file = 'Type_of_Solution_Association.json'
en_file = 'Type_of_Solution_Association (EN).json'

with open(source_file, 'r', encoding='utf-8') as file:
    solution_types = json.loads(file.read())

en_solution_types = []
translator = GoogleTranslator(source='spanish', target='english')


def translate_sol_type(solution_type):
    if type(solution_type) == list:
        en_list = []
        for sol in solution_type:
            en_list.append(translator.translate(sol))
        return en_list
    else:
        return translator.translate(solution_type)


for sol_type in solution_types:
    sol_type['Adestic V1'] = translate_sol_type(sol_type['Adestic V1'])
    sol_type['Adestic V2'] = translate_sol_type(sol_type['Adestic V2'])

    en_solution_types.append(sol_type)

# print(json.dumps(en_solution_types, indent=4))

with open(en_file, 'w', encoding='utf-8') as file:
    file.write(json.dumps(en_solution_types, indent=4))
