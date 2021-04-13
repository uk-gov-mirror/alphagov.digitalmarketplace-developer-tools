from dmdevtools.invoke_tasks import library_tasks as ns

# test with mypy
ns["test"].pre.insert(-1, ns["test-mypy"])
