import argparse
import sys

from project.problem import Problem


class DFA:
    def __init__(self, path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        while len(lines) < 4:  # hiányzó (üres) sorok pótlása
            lines.append("")

        self.states = lines[0].split()
        self.alphabet = lines[1].split()
        self.start = lines[2].strip()
        self.finals = set(lines[3].split())

        # (állapot, jel) -> állapot
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
            if self.delta.get((src, sym), dst) != dst:
                raise ValueError(f"{number}. sor: az automata nem determinisztikus: '{line}'")
            self.delta[(src, sym)] = dst

        if self.start not in self.states:
            raise ValueError(f"ismeretlen kezdőállapot: '{self.start}'")
        for final in self.finals:
            if final not in self.states:
                raise ValueError(f"ismeretlen végállapot: '{final}'")

    def reachable(self):
        seen = {self.start}
        stack = [self.start]
        while stack:
            state = stack.pop()
            for sym in self.alphabet:
                nxt = self.delta.get((state, sym))
                if nxt is not None and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return seen

    def minimize(self):
        """Partíció-finomítás. Az elérhetetlen állapotok elhagyódnak, a
        hiányzó átmenetet egy (ki nem írt) csapdaállapotnak tekintjük."""
        states = sorted(self.reachable())
        symbols = sorted(self.alphabet)

        block = {s: (s in self.finals) for s in states}  # kezdeti: végállapot / nem
        while True:
            signature = {
                s: (block[s],
                    tuple(block.get(self.delta.get((s, a))) for a in symbols))
                for s in states
            }
            ids = {}
            new_block = {}
            for s in states:
                new_block[s] = ids.setdefault(signature[s], len(ids))
            if len(set(new_block.values())) == len(set(block.values())):
                block = new_block
                break
            block = new_block

        # osztályonként a legkisebb nevű állapot lesz a képviselő
        rep = {}
        for s in states:  # states rendezett
            rep.setdefault(block[s], s)
        name = {s: rep[block[s]] for s in states}
        return name

    @staticmethod
    def rename(state):
        return "s" + state[1:]

    def to_text(self):
        name = self.minimize()
        reps = sorted(set(name.values()))
        transitions = set()
        for (src, sym), dst in self.delta.items():
            if src in name and src == name[src]:
                transitions.add((self.rename(src), sym, self.rename(name[dst])))
        finals = [self.rename(s) for s in reps if s in self.finals]

        lines = [
            " ".join(self.rename(s) for s in reps),
            " ".join(self.alphabet),
            self.rename(name[self.start]),
            " ".join(finals),
        ]
        for src, sym, dst in sorted(transitions):
            lines.append(f"{src} {sym} {dst}")
        return "\n".join(lines)


class MinimizeProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--mini', help='minimize the automaton',
                            action='store_true')

    def is_chosen_problem(self, args):
        return bool(getattr(args, "mini", False))

    def run(self, args):
        try:
            dfa = DFA(args.input)
        except ValueError as error:
            print(f"Hiba a bemenetben: {error}", file=sys.stderr)
            sys.exit(1)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write(dfa.to_text())
