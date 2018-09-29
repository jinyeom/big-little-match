import csv
from collections import defaultdict
from typing import Mapping, Sequence

from fire import Fire


def gale_shapley_cap(hospital_prefs: Mapping[str, Sequence[str]],
                     resident_prefs: Mapping[str, Sequence[str]],
                     capacities: Mapping[str, int]) -> Mapping[str, Sequence[str]]:
    r"""Gale-Shapley algorithm for solving the college admissions problem. 
    Note that this algorithm is different from Gale-Shapley algorithm for 
    solving the stable marriage problem.
    
    Args:
        hospital_prefs: a dict for preferences of each hospital
        resident_prefs: a dict for preferences of each resident
        capacities: a dict for capacities of each hospital
        
    Returns:
        a dict that maps each hospital with a list of residents
    """
    # preprocess preferences to pretend that both hospitals and residents each has a full
    # list of preferences of the other side
    hs = set(hospital_prefs.keys())
    rs = set(resident_prefs.keys())
    for h, rprefs in hospital_prefs.items():
        hospital_prefs[h].extend(list(rs - set(rprefs)))
    for r, hprefs in resident_prefs.items():
        resident_prefs[r].extend(list(hs - set(hprefs)))
    
    matches = defaultdict(list)
    unmatched_residents = list(resident_prefs.keys())
    while unmatched_residents:
        resident = unmatched_residents[0]
        hospital = resident_prefs[resident][0]
        matches[hospital].append(resident)
        
        if len(matches[hospital]) > capacities[hospital]:
            # if the hospital is matched with more residents than it can hold,
            # remove the least preferred resident from its matches
            least_pref = max(i for i, r in enumerate(hospital_prefs[hospital]) if r in matches[hospital])
            matches[hospital].remove(hospital_prefs[hospital][least_pref])
            
        if len(matches[hospital]) == capacities[hospital]:
            least_pref = max(i for i, r in enumerate(hospital_prefs[hospital]) if r in matches[hospital])
            for resident in hospital_prefs[hospital][least_pref+1:]:
                hospital_prefs[hospital].remove(resident)
                if hospital in resident_prefs[resident]:
                    resident_prefs[resident].remove(hospital)
                
        # update the unmatched residents
        unmatched_residents = [r for r in resident_prefs if resident_prefs[r] and 
                               not any([r in rs for rs in matches.values()])]
        
    return matches


def read_bigs_csv(filename):
    prefs = {}
    capacities = {}
    with open(filename, "r") as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader) # skip the header
        for row in csv_reader:
            prefs[row[1]] = row[3:6]
            capacities[row[1]] = int(row[2])
    return prefs, capacities


def read_littles_csv(filename):
    prefs = {}
    with open(filename, "r") as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader) # skip the header
        for row in csv_reader:
            prefs[row[1]] = row[2:5]
    return prefs


def main(bigs_filename: str, littles_filename: str):
    if not bigs_filename.endswith(".csv") or not littles_filename.endswith(".csv"):
        raise ValueError("both argument files must be .csv files")
    big_prefs, capacities = read_bigs_csv(bigs_filename)
    little_prefs = read_littles_csv(littles_filename)

    print("==== Bigs ====")
    for big, lprefs in big_prefs.items():
        lprefs_str = ", ".join(lprefs)
        print(f"\x1B[1m{big}\x1B[0m ({capacities[big]}) - {lprefs_str}")
    print()

    print("==== Littles ====")
    for little, bprefs in little_prefs.items():
        bprefs_str = ", ".join(bprefs)
        print(f"\x1B[1m{little}\x1B[0m - {bprefs_str}")
    print() 

    matches = gale_shapley_cap(big_prefs, little_prefs, capacities)

    print("MATCHED ᕕ(⌐■_■)ᕗ ♪♬")
    for big, littles in matches.items():
        littles_str = ", ".join(littles)
        print(f"\x1B[1m{big}\x1B[0m - {littles_str}")
    print() 


if __name__ == "__main__":
    Fire(main)