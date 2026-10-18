import argparse
import sys

from project.problem import Problem


class NFA:
    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        while len(lines) < 4:  # hiányzó (üres) sorok pótlása
            lines.append("")

        self.states = lines[0].split()
        self.alphabet = lines[1].split()
        self.start = lines[2].strip()
        self.finals = set(lines[3].split())

        # (állapot, jel) -> célállapotok halmaza
        self.delta = {}
        for number, line in enumerate(lines[4:], start=5):
            parts = line.split()
            if not parts:
                continue
            if len(parts) != 3:
                raise ValueError(f"{number}. sor: hibás átmenet: '{line}'")
            src, sym, dst = parts
            if src not in self.states or dst not in self.states:
                raise ValueError(f"{number}. sor: ismeretlen állapot: '{line}'")
            if sym not in self.alphabet:
                raise ValueError(f"{number}. sor: ismeretlen jel: '{line}'")
            self.delta.setdefault((src, sym), set()).add(dst)

        if self.start not in self.states:
            raise ValueError(f"ismeretlen kezdőállapot: '{self.start}'")
        for final in self.finals:
            if final not in self.states:
                raise ValueError(f"ismeretlen végállapot: '{final}'")

    def determinize(self):
        """Részhalmaz-konstrukció. Az új állapotok sorszámozása a felfedezés
        sorrendjét követi (BFS, jelek ábécé sorrendjében)."""
        symbols = sorted(self.alphabet)
        start = frozenset([self.start])
        index = {start: 0}
        order = [start]
        transitions = []  # (forrás index, jel, cél index)

        i = 0
        while i < len(order):
            current = order[i]
            for sym in symbols:
                target = set()
                for state in current:
                    target |= self.delta.get((state, sym), set())
                if not target:
                    continue  # nincs átmenet -> nincs él
                target = frozenset(target)
                if target not in index:
                    index[target] = len(order)
                    order.append(target)
                transitions.append((i, sym, index[target]))
            i += 1

        finals = [k for k, subset in enumerate(order) if subset & self.finals]
        return len(order), finals, transitions

    def to_text(self):
        count, finals, transitions = self.determinize()
        lines = [
            " ".join(f"s{k}" for k in range(count)),
            " ".join(self.alphabet),
            "s0",
            " ".join(f"s{k}" for k in finals),
        ]
        for src, sym, dst in transitions:
            lines.append(f"s{src} {sym} s{dst}")
        return "\n".join(lines)


class DeterminizeProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--det', help='determinize the automaton',
                            action='store_true')

    def is_chosen_problem(self, args):
        return bool(getattr(args, "det", False))

    def run(self, args):
        try:
            nfa = NFA(args.input)
        except ValueError as error:
            print(f"Hiba a bemenetben: {error}", file=sys.stderr)
            sys.exit(1)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(nfa.to_text())