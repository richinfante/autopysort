import glob
import os.path
import sys
import traceback
from typing import List, Optional, Set, Tuple, Union

import libcst
import pyflakes.api
from libcst import matchers as m


class AlphabeticalTransformer(libcst.CSTTransformer):
  def __init__(self) -> None:
    self.coroutine_stack: List[bool] = []
    self.required_imports: Set[str] = set()

  def visit_Module(self, node: libcst.Module) -> None:
    # for item in node.body:
    #   if isinstance(item, libcst.FunctionDef):
    #     print(item.name)
    #     print(item.leading_lines)
    pass

  def leave_Module(
    self,
    node: libcst.Module,
    updated_node: libcst.Module
  ) -> libcst.Module:

    functions = [x for x in node.body if isinstance(x, libcst.FunctionDef)]
    classes = [x for x in node.body if isinstance(x, libcst.ClassDef)]
    other = [x for x in node.body if not isinstance(x, (libcst.FunctionDef, libcst.ClassDef))]

    functions.sort(key=lambda x: x.name.value)
    classes.sort(key=lambda x: x.name.value)

    outclasses = []
    for clazz in classes:
      class_body = clazz.body
      other = [x for x in class_body.body if not isinstance(x, libcst.FunctionDef)]
      classfuncs = [x for x in class_body.body if isinstance(x, libcst.FunctionDef)]

      classfuncs.sort(key=lambda x: x.name.value)
      outbody = []
      outbody.extend(other)
      outbody.extend(classfuncs)
      outclasses.append(clazz.with_changes(
        body=clazz.body.with_changes(body=outbody)
      ))

    print("new ordering: \n  - %s" % "\n  - ".join([x.name.value for x in outclasses]))
    print("new ordering: \n  - %s" % "\n  - ".join([x.name.value for x in functions]))

    body = []
    body.extend(other)
    body.extend(outclasses)
    body.extend(functions)

    return node.with_changes(
      body=body
    )


def reorder_file(filename: str, ignore_file_check=False):
  transformer = AlphabeticalTransformer()
  with open(filename, "r") as python_file:
    python_source = python_file.read()

  try:
    source_tree = libcst.parse_module(python_source)
  except Exception as e:
    print("Error: failed to run parser on {}: {}".format(filename, str(e)))
    return

  try:
    transformed_cst = source_tree.visit(transformer)
  except Exception as e:
    print("Error: failed to modify on {}: {}".format(filename, str(e)))
    traceback.print_exc()
    return

  if not transformed_cst.deep_equals(source_tree):
    potential_code = transformed_cst.code
    warnings = pyflakes.api.check(potential_code, filename)

    # check for warnings
    if warnings > 0 and not ignore_file_check:
      print("ignoring - got %s warnings, may break things. %s" % (warnings, filename))

    # if code is non-empty, write it:
    elif potential_code:
      with open(filename, "w") as python_file:
        print("syntax check OK - writing file: %s" % filename)
        python_file.write(potential_code)

def main():
  ignore_file_check = False
  for keyword in sys.argv[1:]:
    # Allow ignoring of syntax errors caught by pyflakes
    if keyword == "--ignore-syntax-errors":
      ignore_file_check = True
      continue

    # Reorder each file in the glob
    for file in glob.glob(os.path.expanduser(keyword), recursive=True):
      reorder_file(file, ignore_file_check=ignore_file_check)


if __name__ == "__main__":
  main()
