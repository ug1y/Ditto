import json
import os
from dataclasses import dataclass, asdict

from ditto.runs import run_with_attack

attk_base_dir = 'attk_exp'
if not os.path.exists(attk_base_dir):
    os.makedirs(attk_base_dir)


@dataclass
class AttkRes:
    exp_index: int
    success_count: int
    attk_depth_avg: float
    cost_time: float

    def __getitem__(self, item):
        return getattr(self, item)

    def __str__(self):
        return (f"{self.exp_index}, {self.success_count}, "
                f"{self.attk_depth_avg}, {self.cost_time}\n")

    @staticmethod
    def from_string(data: str):
        l = data.split(',')
        return AttkRes(int(l[0]), int(l[1]), float(l[2]), float(l[3]))


def attk_exps(times: int = 100, params: dict = None):
    if params is None:
        params = {"cons_method": 'Nakamoto', "scale": 4, "interval": 10, "delay": 10, "until": 1000, "power": 0.2}

    param_c = params['cons_method'] if 'cons_method' in params else 'Nakamoto'
    param_s = params['scale'] if 'scale' in params else 4
    param_i = params['interval'] if 'interval' in params else 10
    param_d = params['delay'] if 'delay' in params else 10
    param_u = params['until'] if 'until' in params else 1000
    param_p = params['power'] if 'power' in params else 0.2

    filename = f'{param_c}-s{param_s}-i{param_i}-d{param_d}-u{param_u}-p{param_p:.2f}.csv'
    dir_c = os.path.join(attk_base_dir, param_c)
    if not os.path.exists(dir_c):
        os.makedirs(dir_c)
    filepath = os.path.join(dir_c, filename)

    # Get the last experiment index
    index = 1
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            index = len(file.readlines()) + 1
    else:
        with open(filepath, 'w'):
            pass

    # Start experiments from the index
    for i in range(index, times + 1):
        asr = run_with_attack(cons_method=param_c, scale=param_s, interval=param_i,
                              delay=param_d, until=param_u, is_print=False, power=param_p)
        res = AttkRes(i, len(asr), sum(asr) / len(asr) if len(asr) > 0 else 0, run_with_attack.last_elapsed_time)

        print(repr(res))
        with open(filepath, 'a') as file:
            file.write(str(res))

    return filepath


def attk_stats(filepath: str):
    res_list = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines:
            res_list.append(AttkRes.from_string(line))

    total_num = len(res_list)
    res_avg = AttkRes(total_num, 0, 0, 0)
    for i in range(total_num):
        res_avg.success_count += res_list[i].success_count
        res_avg.attk_depth_avg += res_list[i].attk_depth_avg
        res_avg.cost_time += res_list[i].cost_time

    res_avg.success_count /= total_num
    res_avg.attk_depth_avg /= total_num
    res_avg.cost_time /= total_num

    avg_file_name = os.path.splitext(filepath)[0] + '_avg.json'
    with open(avg_file_name, 'w') as file:
        json.dump(asdict(res_avg), file, indent=4)


def main(params: dict):
    print("Attack Experiments with params: ", params)
    f = attk_exps(times=10, params=params)
    attk_stats(f)
    print("Attk Exp Done!")


if __name__ == '__main__':

    params = dict(interval=10, until=1000,
                  # The main control variables
                  cons_method='Pikavolt',
                  scale=32 + 1, delay=10,
                  power=0.2)

    for p in range(4, 12):
        for c in ["Nakamoto", "Phantom", "ULBlockDAG", "Pikavolt"]:
            for d in range(10, 110, 10):
                params['delay'] = d
                params['cons_method'] = c
                params['power'] = p / 20
                main(params)
