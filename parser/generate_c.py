from main_processing import MetaData

# All these files names need to change for certain


def generate(data: MetaData):
    c = ""
    # Only focus on first function def
    functionDef = data.public[list(data.public.keys())[0]]

    c += f"void {functionDef.name} ()" " {\n  "
    for s in functionDef.body:
        if s.which == "assignment":
            c += f"int {s.data[0]} = {s.data[1]};\n"
    c += "}\n"
    return c
