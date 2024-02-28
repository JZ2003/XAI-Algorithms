from NNF import *
import typing as t
from algorithms_utils import *

Term = HashDict
Clause = HashDict


def NR_monotone(formula:NNF,check_correctness=False,use_decomposability=True) -> set[Clause]:
    '''
    Given a monotone NNF, return the set of all its prime implicates.
    '''
    
    if check_correctness:
        if not formula.monotone():
            raise ValueError('NR algorithm only works on monotone NNF')
    def _NR(formula:NNF) -> set[Clause]:
        nonlocal use_decomposability
        if isinstance(formula, Lit):
            NRs = {Clause({formula.name: formula.states})}
        elif isinstance(formula, AND):
            NRs = set().union(*[_NR(sub) for sub in formula.subs])
            if not use_decomposability or not formula.and_decomposable():
                NRs = remove_subsumed(NRs,subsume_func=clause_subsume)
        else: # OR case
            NRs = cartesian_product([_NR(sub) for sub in formula.subs],append_func=clauses_appended)
            if not use_decomposability or not formula.or_decomposable():
                NRs = remove_subsumed(NRs,subsume_func=clause_subsume)
        return NRs

    NRs = _NR(formula)
    return NRs

def SR_monotone(formula:NNF,check_correctness=False,use_decomposability=True) -> set[Term]:
    '''
    Given a monotone NNF, return the set of all its prime implicants.
    '''
    if check_correctness:
        if not formula.monotone(): 
            raise ValueError('SR algorithm only works on monotone NNF')

    def _SR(formula) -> set[Term]:
        nonlocal use_decomposability
        if isinstance(formula, Lit):
            SRs = {Term({formula.name: formula.states})}
        elif isinstance(formula, OR):
            SRs = set().union(*[_SR(sub) for sub in formula.subs])
            if not use_decomposability or not formula.or_decomposable():
                SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        else: # AND case
            # print(f"formula: {formula}, type: {type(formula)}")
            SRs = cartesian_product([_SR(sub) for sub in formula.subs],append_func=terms_appended)
            if not use_decomposability or not formula.and_decomposable():
                SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        return SRs

    SRs = _SR(formula)
    return SRs