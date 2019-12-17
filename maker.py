import json, csv, time
from random import randint, seed

seed(385)


def load_data(filename="parameters.json"):

    aux = {
        "s": 1,
        "d": 3,
        "q": 1,
        "p": 2,
        "e": 2,
        "n": 3,
        "m": 3,
        "l": 1,
        "u": 1,
        "c": 2,
        "beta": 2
    }

    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
    sets = dict()
    for s in data["sets"]:
        if s == "T":
            sets["T"] = list(range(1, data["sets"]["T"]))
            continue
        sets[s] = list(range(data["sets"][s]))
    
    params = data["params"]
    new_params = dict()
    for p in params:
        values = dict()
        for i in params[p]:
            if aux[p] > 1:
                param1 = params[p][i]
                for j in param1:
                    if aux[p] > 2:
                        param2 = params[p][i][j]
                        for k in param2:
                            tup = (int(i), int(j), int(k))
                            values[tup] = param2[k]
                    else:
                        tup = (int(i), int(j))
                        values[tup] = param1[j]
            else:
                tup = (int(i))
                values[tup] = params[p][i]
        new_params[p] = values
    
    return sets, new_params


def show_results(model):
    helper = {
        "x": ("l", "i", "t"),
        "y": ("l", "i", "k", "t"),
        "z": ("l", "k", "j", "t"),
        "b": ("l", "k", "t"),
        "w": ("k", "j", "t")
    }
    
    variables = {
        "x": dict(),
        "y": dict(),
        "z": dict(),
        "b": dict(),
        "w": dict()
    }
    for var in model.getVars():
        name = var.varName
        variables[name[0]][tuple(name[2:].split("_"))] = var.x
    
    print("="*10, "  MODELO OPTIMIZADO  ", "="*10,"\n\n")

    print("Valor objetivo:", model.objVal)

    inp = ""
    while True:
        print("Seleccione un tipo de variable\n - " + "\n - ".join(["x", "y", "z", "b", "w"]))
        print("Ingrese 'q' para salir")
        inp = input("> ")
        if inp == "q":
            break
        if variables.get(inp):
            print(f"\nIngrese los indices para la varibale {inp} de la forma {','.join(helper[inp])}",
            "\nIngrese all para ver todos los resulatdos")
            inp1 = input("> ")
            indexes = tuple(inp1.split(","))
            if inp1 == "all":
                print("="*20,"\nRESULTADOS:\n")
                print(f"{inp}{helper[inp]} -> valor")
                for var in variables[inp]:
                    print(f"{inp}{var} -> {variables[inp][var]}")
                print("="*20)
            else:
                if len(indexes) != len(helper[inp]):
                    print("\n  ---- Indices mal ingresados :( ----")
                else:
                    value = variables[inp].get(indexes)
                    if value is not None:
                        print("="*20,"\nRESULTADO:")
                        print(f"{inp}({','.join(indexes)}) -> {value}"+"\n"+"="*20+"\n")
                    else:
                        print("\n  --- No hay resultados para la varibale ingresada :( ---")
        else:
            print("\n --- Variable desconocida ---")


def generate_data(filename="parameters.json", changes=False, args=dict()):
    if filename == "parameters.json" and not changes:
        print("="*10, "   DATA NOT CHANGED   ", "="*10)
        return 
    sets = {
            "I": 3,
            "L": 10,
            "J": 2,
            "K": 1,
            "T": 31
        }

    aux = {
        "i": "I",
        "j": "J",
        "l": "L",
        "k": "K",
        "t": "T"
    }

    aux3 = {
        "s": [5000, 10000],
        "d": [100, 200],
        "q": [150000, 200000],
        "p": [5000, 150000],
        "e": [500, 5000],
        "n": [1000, 10000],
        "m": [1000, 10000],
        "l": [50, 100],
        "u": [2000, 3000],
        "c": [50, 5000],
        "beta": [500, 1000]
    }

    aux2 = {
        "s": ["i"],
        "d": ["l", "j", "t"],
        "q": ["k"],
        "p": ["l", "i"],
        "e": ["l", "k"],
        "n": ["l", "k", "j"],
        "m": ["l", "i", "k"],
        "l": ["k"],
        "u": ["k"],
        "c": ["l", "k"],
        "beta": ["k", "l"]
    }

    params = dict()

    for p in aux2:
        if changes and p not in args:
            continue
        index = aux2[p]

        a_dict = dict()
        i = index[0]
        for n1 in range(sets[aux[i]]):
            if len(index) > 1:
                i2 = index[1]
                a_dict_2 = dict()
                for n2 in range(sets[aux[i2]]):
                    if len(index) > 2:
                        i3 = index[2]
                        a_dict_3 = dict()
                        for n3 in range(sets[aux[i3]]):
                            if p in args:
                                a_dict_3[n3] = randint(args[p][0], args[p][1])
                            else:
                                a_dict_3[n3] = randint(aux3[p][0], aux3[p][1])
                        a_dict_2[n2] = a_dict_3
                    else:
                        if p in args:
                            a_dict_2[n2] = randint(args[p][0], args[p][1])
                        else:
                            a_dict_2[n2] = randint(aux3[p][0], aux3[p][1])
                a_dict[n1] = a_dict_2
            else:
                if p in args:
                    a_dict[n1] = randint(args[p][0], args[p][1])
                else:
                    a_dict[n1] = randint(aux3[p][0], aux3[p][1])
        params[p] = a_dict
    
    if changes:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
            for p in params:
                data["params"][p] = params[p]
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(data, file)
        print("="*10, f"  DATA CHANGED  ", "="*10) 
    else:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump({"sets": sets, "params": params}, file)
    
        print("="*10, f"  DATA CREATED IN {filename}  ", "="*10)


def generate_file_results(model, sets):
    helper = {
        "x": ("l", "i", "t"),
        "y": ("l", "i", "k", "t"),
        "z": ("l", "k", "j", "t"),
        "b": ("l", "k", "t"),
        "w": ("k", "j", "t")
    }

    with open(
        f"results_model_G69_{time.strftime('%d_%m_%Y_%H_%M_%S')}.csv",
        "w",
        encoding="utf-8"
        ) as file:

        writer = csv.writer(file)

        writer.writerow(["Valor optimo: ", model.objVal])
        writer.writerow([])

        header = ["Variable", "t:"]
        header.extend(sets["T"])
        writer.writerow(header)

        vars_aux = dict()
        for var in model.getVars():
            name = var.varName
            naml = name.split("_")
            name2 = "_".join(naml[:-1])
            if vars_aux.get(name[0]):
                var1 = vars_aux[name[0]]
                if var1.get(name2):
                    var1[name2].append((name, var.x))
                else:
                    var1[name2] = [(name, var.x)]
            else:
                vars_aux[name[0]] = {f"{name2}": [(name, var.x)]}

        for v in vars_aux:
            writer.writerow([f"{v}_" + "_".join(helper[v])])
            var = vars_aux[v]
            for v1 in var:
                var1 = var[v1]

                var1.sort(key=lambda x: int(x[0].split("_")[-1]))
                row = [v1 + "_t", ""] 
                for var2 in var1:
                    row.append(var2[1])
                writer.writerow(row)


if "__main__" == __name__:
    generate_data()