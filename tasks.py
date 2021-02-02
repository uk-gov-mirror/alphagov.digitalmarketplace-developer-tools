from dmdevtools.invoke_tasks import library_tasks as ns


# currently we have no unit tests
ns["test"].pre.remove(ns["test-python"])
