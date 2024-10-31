import os, json
from dataclasses import dataclass, asdict

from ditto.runs import run_simulation

simu_base_dir = 'simu_exp'
if not os.path.exists(simu_base_dir):
    os.makedirs(simu_base_dir)


@dataclass
class SimuRes:
    exp_index: int
    num_of_blocks: int
    throughput: float
    latency: float
    distribution: float
    cost_time: float

    def __getitem__(self, item):
        return getattr(self, item)

    def __str__(self):
        return (f"{self.exp_index}, {self.num_of_blocks}, {self.throughput}, "
                f"{self.latency}, {self.distribution}, {self.cost_time}\n")

    @staticmethod
    def from_string(data: str):
        l = data.split(',')
        return SimuRes(int(l[0]), int(l[1]), float(l[2]), float(l[3]), float(l[4]), float(l[5]))


def simu_exps(times: int = 100, params: dict = None):
    if params is None:
        params = {"cons_method": 'Nakamoto', "scale": 4, "interval": 10, "delay": 10, "until": 10000}

    param_c = params['cons_method'] if 'cons_method' in params else 'Nakamoto'
    param_s = params['scale'] if 'scale' in params else 4
    param_i = params['interval'] if 'interval' in params else 10
    param_d = params['delay'] if 'delay' in params else 10
    param_u = params['until'] if 'until' in params else 10000

    filename = f'{param_c}-s{param_s}-i{param_i}-d{param_d}-u{param_u}.csv'
    dir_c = os.path.join(simu_base_dir, param_c)
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
        srd = run_simulation(cons_method=param_c, scale=param_s, interval=param_i,
                             delay=param_d, until=param_u, is_print=False)
        res = SimuRes(i, srd.get_total_created_blocks(), srd.compute_throughput(),
                      srd.compute_latency(), srd.compute_change_dist(),
                      run_simulation.last_elapsed_time)

        print(repr(res))
        with open(filepath, 'a') as file:
            file.write(str(res))

    return filepath


def simu_stats(filepath: str):
    res_list = []
    with open(filepath, 'r') as file:
        lines = file.readlines()
        for line in lines:
            res_list.append(SimuRes.from_string(line))

    total_num = len(res_list)
    res_avg = SimuRes(total_num, 0, 0, 0, 0, 0)
    for i in range(total_num):
        res_avg.num_of_blocks += res_list[i].num_of_blocks
        res_avg.throughput += res_list[i].throughput
        res_avg.latency += res_list[i].latency
        res_avg.distribution += res_list[i].distribution
        res_avg.cost_time += res_list[i].cost_time

    res_avg.num_of_blocks /= total_num
    res_avg.throughput /= total_num
    res_avg.latency /= total_num
    res_avg.distribution /= total_num
    res_avg.cost_time /= total_num

    avg_file_name = os.path.splitext(filepath)[0] + '_avg.json'
    with open(avg_file_name, 'w') as file:
        json.dump(asdict(res_avg), file, indent=4)


def main(params: dict):
    print("Simulation Experiments with params: ", params)
    f = simu_exps(times=100, params=params)
    simu_stats(f)
    print("Simu Exp Done!")


if __name__ == '__main__':

    params = dict(interval=10, until=1000,
                  # The main control variables
                  cons_method='Pikavolt',
                  scale=4, delay=30)

    for s in [2 ** i for i in range(2, 8)]:
        for c in ["Nakamoto", "Phantom", "ULBlockDAG", "Pikavolt"]:
            for d in range(10, 110, 10):
                params['scale'] = s
                params['cons_method'] = c
                params['delay'] = d
                main(params)
