import ast
import datetime
import subprocess

version = open("../debian/changelog").readlines()[0].split()[1].strip("()")
today = datetime.datetime.now().strftime("%d/%m/%Y")


def get_current_commit():
    p = subprocess.Popen(
        "git rev-parse --verify HEAD",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    stdout, stderr = p.communicate()

    current_commit = stdout.strip().decode("utf-8")
    return current_commit


current_commit = get_current_commit()


print(
    f"""---
title: App resources
template: docs
taxonomy:
    category: docs
routes:
  default: '/packaging_apps_resources'
---

Doc auto-generated by [this script](https://github.com/YunoHost/yunohost/blob/{current_commit}/doc/generate_resource_doc.py) on {today} (YunoHost version {version})

"""
)


fname = "../src/utils/resources.py"
content = open(fname).read()

# NB: This magic is because we want to be able to run this script outside of a YunoHost context,
# in which we cant really 'import' the file because it will trigger a bunch of moulinette/yunohost imports...
tree = ast.parse(content)

ResourceClasses = [
    c
    for c in tree.body
    if isinstance(c, ast.ClassDef) and c.bases and c.bases[0].id == "AppResource"
]

ResourceDocString = {}

for c in ResourceClasses:
    assert c.body[1].targets[0].id == "type"
    resource_id = c.body[1].value.value
    docstring = ast.get_docstring(c)

    ResourceDocString[resource_id] = docstring


for resource_id, doc in sorted(ResourceDocString.items()):
    doc = doc.replace("\n    ", "\n")

    print("----------------")
    print("")
    print(f"## {resource_id.replace('_', ' ').title()}")
    print("")
    print(doc)
    print("")
