import argparse
import re
import sys
from collections import Counter

from project.problem import Problem

# A feladatleírásban javasolt kifejezés (logcat sor):
#   1: dátum+idő, 2: időbélyeg, 3: PID, 4: TID, 5: szint, 6: tag, 7: üzenet
LOG = re.compile(
    r'(([0-9-]+ [0-9:.]+) +([0-9]+) +([0-9]+) ([IDVEFAW]) (.+?):(?: (.+))?)')

# Egy logcat sor eleje: "10-15 10:18:51.254   601   601 "
HDR = r'^[0-9-]+ [0-9:.]+ +[0-9]+ +[0-9]+ '

# 1. feladat: alpontonként egy kifejezés, mindegyikre a találó sorok száma
PATTERNS = [
    r'^10-15 ',                                      # 10. hó 15-én
    r'^10-15 10:18:51\.',                            # 10-15 10:18:51
    r'^[0-9-]+ [0-9]+:[0-9]+:51\.',                  # bármely perc, 51 mp
    HDR + r'[IDVEFAW] lowmemorykiller *:',           # lowmemorykiller tag
    r'^[0-9-]+ 10:18:51\.[0-9]+ +221 ',              # 10:18:51, PID 221
    HDR + r'E ',                                     # hibák
    HDR + r'W PackageManager *:',                    # PackageManager warning
    HDR + r'D .*ExoPlayer',                          # ExoPlayer debug (a sorban bárhol)
    HDR + r'[EW] .*\.java:[0-9]+',                  # .java pozíció E/W sorban
    HDR + r'[IDVEFAW] [^:]+:.*Thread',               # Thread az üzenetben
]


def read_lines(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()


def task1(lines):
    compiled = [re.compile(p) for p in PATTERNS]
    return [str(sum(1 for line in lines if p.search(line))) for p in compiled]


def task2(lines):
    """Az E szintű bejegyzések (a fejléces sor és a hozzá tartozó, fejléc
    nélküli folytatósorok) .java állományneveit gyűjti, előfordulási sorrendben."""
    result = []
    in_error = False
    for line in lines:
        m = LOG.match(line)
        if m:
            in_error = m.group(5) == 'E'
        if in_error:
            result.extend(re.findall(r'([\w$]+\.java):[0-9]+', line))
    return result


def task3(lines):
    seen = []
    for line in lines:
        m = LOG.match(line)
        if m and m.group(3) not in seen:
            seen.append(m.group(3))
    return seen


def task4(lines):
    errors = Counter()
    for line in lines:
        m = LOG.match(line)
        if m and m.group(5) == 'E':
            errors[m.group(3)] += 1
    if not errors:
        return []
    pid, count = errors.most_common(1)[0]  # döntetlennél az első előfordulás
    return [f"PID={pid} ({count} errors)"]


def task5(lines):
    count = 0
    for line in lines:
        m = LOG.match(line)
        if m and m.group(5) == 'E' and m.group(3) == m.group(4):
            count += 1
    return [str(count)]


TASKS = {1: task1, 2: task2, 3: task3, 4: task4, 5: task5}


class RegexProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        parser.add_argument('--rgx', type=int,
                            help='regex task number (1-5)')

    def is_chosen_problem(self, args):
        return getattr(args, "rgx", None) is not None

    def run(self, args):
        task = TASKS.get(args.rgx)
        if task is None:
            print(f"Hiba: ismeretlen feladatszám: {args.rgx}", file=sys.stderr)
            sys.exit(1)

        try:
            lines = read_lines(args.input)
        except OSError as error:
            print(f"Hiba a bemeneti fájl olvasásakor: {error}", file=sys.stderr)
            sys.exit(1)

        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(task(lines)))