import functools
import time
import json
from os import path


def write_to_file(to_save, filename="data.json"):
    data = {}
    if not path.exists(filename):
        with open(filename, "w") as file:
            json.dump(data, file)
    with open(filename, "r") as file:
        data = json.load(file)
    for k, v in to_save.items():
        if k not in data:
            data[k] = {"total": 0, "count": 0, "average": 0}
        data[k]["total"] += v
        data[k]["count"] += 1
        data[k]["average"] = data[k]["total"] / data[k]["count"]
    with open(filename, "w") as file:
        json.dump(data, file)


def timed(result_method="file"):
    def decorator_timed(func):
        @functools.wraps(func)
        def time_of_func(*args, **kwargs):
            start_time = time.perf_counter_ns()
            value = func(*args, **kwargs)
            run_time = time.perf_counter_ns() - start_time
            if result_method == "file":
                write_to_file({f"{func.__name__}_{'_'.join([str(arg) for arg in args])}": run_time})
            elif result_method == "print":
                print(f"{func.__name__}: {run_time}secs")
            return value
        return time_of_func
    return decorator_timed
