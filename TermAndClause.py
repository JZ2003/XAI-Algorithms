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

def clause_subsume(LHS:HashDict,RHS:HashDict) ->bool:
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

def clauses_appended(clauses:tuple[HashDict]) ->HashDict:
    """
    Given a tuple of clauses, return a clause that is the result of appending all clauses.
    """
    appended = defaultdict(list)
    for clause in clauses:
        for varName, states in clause.items():
            appended[varName].append(states)
    res = HashDict({varName: reduce(frozenset.union, sets) for varName, sets in appended.items()})
    return res
