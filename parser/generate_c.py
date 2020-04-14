from main_processing import MetaData, receiveEntry

# All these files names need to change for certain


def generate(data: MetaData):
    c = ""
    # Only focus on first function def
    mainEntry = list(
        filter(lambda x: isinstance(x, receiveEntry), data.public.values())
    )[0]
    # mainEntry = data.public[list(data.public.keys())[0]]

    c += f"int {mainEntry.name} ()" " {\n"
    for s in mainEntry.body:
        if s.which == "assignment":
            name, var = s.data
            c += f"  {var.type_.children[0]} {name} = {var.value.v};\n"
    c += "  return 0;\n}\n"
    return c
