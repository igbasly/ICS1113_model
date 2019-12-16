from gurobipy import (Model, GRB, quicksum, GurobiError)
from maker import load_data
import json


sets, params = load_data()


# Conjuntos
T = list(range(1, sets["T"]))
I = list(range(sets["I"]))
L = list(range(sets["L"]))
J = list(range(sets["J"]))
K = list(range(sets["K"]))


# Parametros
s = params["s"]
d = params["d"]
q = params["q"]
p = params["p"]
e = params["e"]
m = params["m"]
n = params["n"]
vl = params["l"]
u = params["u"]
beta = params["beta"]


# Crear Modelo
model = Model("Optimizacion logistica de insumos en hospitales")


# Variables
#model.addVar()

x = {}  # Cantidad de producto l encargado a compañia i en periodo t.
y = {}  # Cantidad de producto l transportado desde compañıa i a bodega k en periodo t.
z = {}  # Cantidad de producto l transportado desde bodega k a hospital j en periodo t.
b = {}  # Cantidad de producto l almacenado en la bodega k en el periodo t.
w = {}  # 1 Si bodega k abastece a hospital j en el perido t, 0 EOC.

for t in T:
    for i in I:
        for l in L:
            x[l, i, t] = model.addVar(vtype=GRB.INTEGER, name=f"x_{l}_{i}_{t}")
            for k in K:
                y[l, i, k, t] = model.addVar(vtype=GRB.INTEGER, name=f"y_{l}_{i}_{k}_{t}")

for t in T:
    for l in L:
        for k in K:
            b[l, k, t] = model.addVar(vtype=GRB.INTEGER, name=f"b_{l}_{k}_{t}")
            for j in J:
                z[l, k, j, t] = model.addVar(vtype=GRB.INTEGER, name=f"z_{l}_{k}_{j}_{t}")

for t in T:
    for j in J:
        for k in K:
            w[k, j, t] = model.addVar(vtype=GRB.BINARY, name=f"w_{k}_{j}_{t}")


# Llama a update para agregar las variables al modelo
model.update()


# Funcion objetivo
model.setObjective(
    quicksum(x[l,i,t]*p[l,i] for t in T for i in I for l in L) +
    quicksum(y[l,i,k,t]*e[l,k] for t in T for k in K for i in I for l in L) +
    quicksum(m[l,i,k]*y[l,i,k,t] for l in L for i in I for k in K for t in T) +
    quicksum(n[l,k,j]*z[l,k,j,t] for l in L for k in K for j in J for t in T) +
    quicksum(c[l,k]*b[l,k,t] for l in L for k in K for t in T),
    GRB.MINIMIZE
)

# Restriciones

model.addConstrs(
    (quicksum(x[l,i,t] for l in L) <= s[i] for i in I for t in T),
    "R1"
)

model.addConstrs(
    (quicksum(z[l,k,j,t] for k in K) >= d[l,j,t] for l in L for j in J for t in T),
    "R2"
)

model.addConstrs(
    (x[l,i,t] == quicksum(y[l,i,k,t+2] for k in K) for l in L for i in I for t in T[:-2]),
    "R3-1"
)

model.addConstrs(
    (y[l,i,k,t] == 0 for l in L for i in I for k in K for t in [1,2]),
    "R3-2"
)

model.addConstrs(
    (x[l,i,t] == 0 for l in L for i in I for t in [T[-2],T[-1]]),
    "R3-3"
)

model.addConstrs(
    (b[l,k,t-1] + quicksum(y[l,i,k,t] for i in I) == quicksum(z[l,k,j,t] for j in J) + b[l,k,t]\
         for l in L for k in K for t in T[1:]),
    "R4-1"
)

model.addConstrs(
    (b[l,k,1] == beta[k,l] + y[l,i,k,1] for l in L for k in K for i in I),
    "R4-2"
)

model.addConstrs(
    (quicksum(b[l, k, t] for l in L) <= q[k] for k in K for t in T),
    "R5"
)

model.addConstrs(
    (quicksum(z[l,k,j,t] for l in L) >= vl[k]*w[k,j,t] for k in K for j in J for t in T),
    "R6-1"
)

model.addConstrs(
    (quicksum(z[l,k,j,t] for l in L) <= u[k]*w[k,j,t] for k in K for j in J for t in T),
    "R6-2"
)

model.addConstrs(
    (quicksum(w[k,j,t] for k in K) <= 1 for j in J for t in T),
    "R7"
)


try:
    helper = {
        "x": ("l", "i", "t"),
        "y": ("l", "i", "k", "t"),
        "z": ("l", "k", "j", "t"),
        "b": ("l", "k", "t"),
        "w": ("k", "j", "t")
    }
    model.optimize()
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


except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))

except AttributeError:
    print('Encountered an attribute error')
