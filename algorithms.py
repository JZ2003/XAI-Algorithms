from NNF import *
import typing as t
import itertools


def remove_subsumed(bigSet: set[frozenset[str]]) -> set[frozenset[str]]:
    bigSet = sorted(bigSet, key=len)
    res = set()
    for s in bigSet:
        if not any(x.issubset(s) for x in res):
            res.add(s)
    return res


def cartesian_product(allSets):
    l = list(itertools.product(*allSets))
    l = [frozenset().union(*t) for t in l]
    return set(l)


def NR(formula:NNF) -> set[NNF]:
    '''
    Given a monotone NNF, return the set of all its prime implicates.
    '''
    def _NR(formula:NNF) -> set[frozenset[str]]:
        if not formula.monotone(): 
            raise ValueError('NR algorithm only works on monotone NNF')
        if isinstance(formula, Lit):
            NRs = {frozenset([str(formula)])}
        elif isinstance(formula, AND):
            NRs = set().union(*[_NR(sub) for sub in formula.subs])
            NRs = remove_subsumed(NRs)
        else: # OR case
            NRs = cartesian_product([_NR(sub) for sub in formula.subs])
            if not formula.or_decomposable():
                NRs = remove_subsumed(NRs)
        return NRs

    NRs = _NR(formula)
    NRs = {OR(subs=tuple(Lit.from_string(s) for s in x)) for x in NRs}
    return NRs

def SR(formula:NNF) -> set[NNF]:
    '''
    Given a monotone NNF, return the set of all its prime implicants.
    '''
    def _SR(formula:NNF) -> set[frozenset[str]]:
        if not formula.monotone(): 
            raise ValueError('NR algorithm only works on monotone NNF')
        if isinstance(formula, Lit):
            SRs = {frozenset([str(formula)])}
        elif isinstance(formula, OR):
            SRs = set().union(*[_SR(sub) for sub in formula.subs])
            SRs = remove_subsumed(SRs)
        else: # OR case
            SRs = cartesian_product([_SR(sub) for sub in formula.subs])
            if not formula.or_decomposable():
                SRs = remove_subsumed(SRs)
        return SRs

    SRs = _SR(formula)
    SRs = {AND(subs=tuple(Lit.from_string(s) for s in x)) for x in SRs}
    return SRs