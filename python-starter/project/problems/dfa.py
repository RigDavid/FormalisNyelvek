import argparse

from project.problem import Problem


class DFA:
    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()

        self.states = lines[0].split()
        self.alphabet = lines[1].split()
        self.start = lines[2].strip()
        self.finals = set(lines[3].split())

        # (állapot, jel) -> következő állapot
        self.delta = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, sym, dst = parts
                self.delta[(src, sym)] = dst

    def accepts(self, word):
        state = self.start
        for ch in word:
            key = (state, ch)
            if key not in self.delta:  # ismeretlen jel / hiányzó átmenet
                return False
            state = self.delta[key]
        return state in self.finals


class DFAProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        # Az --input és --output kapcsolót a főprogram már felveszi
        parser.add_argument('--check', help='comma separated words to check')

    def is_chosen_problem(self, args):
        return getattr(args, "check", None) is not None

    def run(self, args):
        dfa = DFA(args.input)
        words = args.check.split(",") if args.check else []
        results = ["IGEN" if dfa.accepts(w) else "NEM" for w in words]
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(results))