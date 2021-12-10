import time
import json
from os import path
from RSA.prime_tools import *


def write_to_file(to_save, filename="data/data.json"):
    data = {}
    if not path.exists(filename):
        with open(filename, "w") as file:
            json.dump(data, file)
    with open(filename, "r") as file:
        data = json.load(file)
    for k, v in to_save.items():
        if k not in data:
            data[k] = {"total": 0, "count": 0, "average": 0, "min": 0, "max": 0}
        data[k]["total"] += v
        data[k]["count"] += 1
        data[k]["average"] = data[k]["total"] / data[k]["count"]
        if data[k]["min"] > v:
            data[k]["min"] = v
        if data[k]["max"] < v:
            data[k]["max"] = v
    with open(filename, "w") as file:
        json.dump(data, file)


def old_timed(method, args=(), kwargs=None, result_method="file"):
    if kwargs is None:
        kwargs = {}
    start_time = time.perf_counter_ns()
    method(*args, **kwargs)
    run_time = time.perf_counter_ns() - start_time
    if result_method == "file":
        write_to_file({f"{method.__name__}{'_' if len(args) > 0 else ''}{'_'.join([str(arg) for arg in args])}": run_time})
    elif result_method == "print":
        print(f"{method.__name__}: {run_time/1000000000}seconds")
    return run_time


def timed(method, args=(), kwargs=None, runs=1, name="", ret_val=False):
    if kwargs is None:
        kwargs = {}
    total_time = 0
    method_ret_val = None
    for _ in range(runs):
        start_time = time.perf_counter_ns()
        method_ret_val = method(*args, **kwargs)
        run_time = time.perf_counter_ns() - start_time
        total_time += run_time
    results = {f"{method.__name__}{'_' if name else ''}{name}": {"total_time_ns": total_time,
                                                                 "average_time_ns": total_time / runs,
                                                                 "total_time": total_time / 1000000000,
                                                                 "average_time": (total_time / runs) / 1000000000,
                                                                 "runs": runs
                                                                 }}
    if ret_val:
        return method_ret_val, results
    else:
        return results
