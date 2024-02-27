from collections import defaultdict
from HashDict import HashDict 
from functools import reduce

def term_subsume(LHS:HashDict,RHS:HashDict) -> bool:
    """
    Return True if the LHS term subsumes the RHS term
    (RHS implies LHS)
    """
    for varName,states in LHS.items():
        if varName not in RHS: #If X-literal doesn't exist in RHS, it's \top
            return False
        else:
            statesRHS = RHS[varName]
            if not statesRHS.issubset(states): 
                return False #Every X-literal of RHS needs to be a subset of that in LHS
    return True

# def terms_appended(terms:list[dict[str,set[int]]]) -> dict[str,set[int]]:
#     """
#     Given a list of terms, return a term that is the result of appending all terms.
#     """
#     appended = defaultdict(list)
#     for term in terms:
#         for varName, states in term.items():
#             appended[varName].append(states)
#     res = {varName: reduce(set.intersection, sets) for varName, sets in appended.items()}
#     return res

def terms_appended(terms:tuple[HashDict]) -> HashDict:
    """
    Given a tuple of terms, return a term that is the result of appending all terms.
    """
    appended = defaultdict(list)
    for term in terms:
        for varName, states in term.items():
            appended[varName].append(states)
    res = HashDict({varName: reduce(frozenset.intersection, sets) for varName, sets in appended.items()})
    return res

# def term_remove_subsumed(terms: list[dict[str, set[int]]]) -> list[dict[str, set[int]]]:
#     """
#     Given a list of terms, remove terms that are subsumed by any other term.
#     """
#     subsumed_indices = set()
#     for i, termA in enumerate(terms):
#         for j, termB in enumerate(terms):
#             if i != j and term_subsume(termA, termB):
#                 subsumed_indices.add(j)
#     return [term for i, term in enumerate(terms) if i not in subsumed_indices]


def clause_subsume(LHS:dict[str,set[int]],RHS:dict[str,set[int]]) ->bool:
    """
    Return True if the LHS clause subsumes the RHS clause
    (LHS implies RHS)
    """
    for varName,states in LHS.items():
        if varName not in RHS: #If X-literal doesn't exist in RHS, it's \bot
            return False
        else:
            statesRHS = RHS[varName]
            if not states.issubset(statesRHS): 
                return False #Every X-literal of RHS needs to be a superset
    return True


def clauses_appended(clauses:list[dict[str,set[int]]]):
    """
    Given a list of clauses, return a term that is the result of appending all terms.
    """
    appended = defaultdict(list)
    for clause in clauses:
        for varName, states in clause.items():
            appended[varName].append(states)
    res = {varName: reduce(set.union, sets) for varName, sets in appended.items()}
    return res

def clause_remove_subsumed(clauses: list[dict[str, set[int]]]) -> list[dict[str, set[int]]]:
    """
    Given a list of clauses, remove clauses that are subsumed by any other clause.
    """
    subsumed_indices = set()
    for i, clauseA in enumerate(clauses):
        for j, clauseB in enumerate(clauses):
            if i != j and clause_subsume(clauseA, clauseB):
                subsumed_indices.add(j)
    return [clause for i, clause in enumerate(clauses) if i not in subsumed_indices]

