import json
import os

from simu_exp_script import SimuRes, simu_base_dir
from attk_exp_script import AttkRes, attk_base_dir


def simu_avg_res(params: dict, base_dir: str):

    filename = (f'{params["cons_method"]}-s{params["scale"]}-i{params["interval"]}-d{params["delay"]}'
                f'-u{params["until"]}_avg.json')
    dir_c = os.path.join(base_dir, params["cons_method"])
    filepath = os.path.join(dir_c, filename)

    with open(filepath, 'r') as file:
        data = json.load(file)
        return SimuRes(**data)


def attk_avg_res(params: dict, base_dir: str):

    filename = (f'{params["cons_method"]}-s{params["scale"]}-i{params["interval"]}-d{params["delay"]}'
                f'-u{params["until"]}-p{params["power"]:.2f}_avg.json')
    dir_c = os.path.join(base_dir, params["cons_method"])
    filepath = os.path.join(dir_c, filename)

    with open(filepath, 'r') as file:
        data = json.load(file)
        return AttkRes(**data)


def print_simu_avg_res(col: str, data: str, params: dict):
    import prettytable

    C = ["Nakamoto", "Phantom", "ULBlockDAG", "Pikavolt"]
    S = [2 ** i for i in range(2, 8)]
    D = [_ for _ in range(10, 110, 10)]
    M = {'scale': S, 'delay': D}

    t = prettytable.PrettyTable()
    t.field_names = [data] + C

    X = M[col]
    for x in X:
        w = [f'{col}={x}']
        for c in C:
            params['cons_method'] = c
            params[col] = x
            r = simu_avg_res(params, simu_base_dir)
            w.append(f'{r[data]:.3f}')
        t.add_row(w)

    print(t.get_string())


def print_attk_avg_res(col: str, data: str, params: dict):
    import prettytable

    C = ["Nakamoto", "Phantom", "ULBlockDAG", "Pikavolt"]
    P = [i / 20 for i in range(4, 12)]
    D = [_ for _ in range(10, 110, 10)]
    M = {'power': P, 'delay': D}

    t = prettytable.PrettyTable()
    t.field_names = [data] + C

    X = M[col]
    for x in X:
        w = [f'{col}={x}']
        for c in C:
            params['cons_method'] = c
            params[col] = x
            r = attk_avg_res(params, attk_base_dir)
            w.append(f'{r[data]:.3f}')
        t.add_row(w)

    print(t.get_string())


if __name__ == '__main__':
    params1 = dict(interval=10, until=1000, scale=32, delay=50)
    # col = scale, delay
    # data = throughput, latency, distribution, cost_time
    print_simu_avg_res('delay', 'distribution', params1)

    print()

    params2 = dict(interval=10, until=1000, scale=33, delay=10, power=0.2)
    # col = power, delay
    # data = success_count, attk_depth_avg, cost_time
    # print_attk_avg_res('power', 'success_count', params2)

