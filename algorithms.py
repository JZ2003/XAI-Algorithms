from NNF import *
import typing as t
from algorithms_utils import *
from functools import lru_cache

CACHE_SIZE = None

def NR_monotone(formula:NNF,check_correctness=False,use_decomposability=True) -> set[Clause]:
    '''
    Given a monotone NNF, return the set of all its prime implicates.
    '''
    
    if check_correctness:
        if not formula.monotone():
            raise ValueError('NR algorithm only works on monotone NNF')
    @lru_cache(maxsize=CACHE_SIZE)
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
    @lru_cache(maxsize=CACHE_SIZE)
    def _SR(formula) -> set[Term]:
        nonlocal use_decomposability
        if isinstance(formula, Lit):
            SRs = {Term({formula.name: formula.states})}
        elif isinstance(formula, OR):
            SRs = set().union(*[_SR(sub) for sub in formula.subs])
            if not use_decomposability or not formula.or_decomposable():
                SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        else: # AND case
            SRs = cartesian_product([_SR(sub) for sub in formula.subs],append_func=terms_appended)
            if not use_decomposability or not formula.and_decomposable():
                SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        return SRs

    SRs = _SR(formula)
    return SRs

def GSR_SD(formula:NNF,check_correctness=False,use_decomposability=True,var_min=False) -> set[Term]:
    """
    Given a NNF that satisfies simple disjunt properties, return the set 
    of all its (variable minimal) prime implicants.
    """
    if check_correctness:
        if not formula.simple_disjunct(): 
            raise ValueError('GSR_SD algorithm only works on simple-disjunct NNF')
    srCount = 0
    
    @lru_cache(maxsize=CACHE_SIZE)
    def _GSR_SD(formula,ivars) -> set[Term]:
        nonlocal use_decomposability
        nonlocal srCount
        srCount += 1
        if isinstance(formula, Lit):
            SRs = {Term({formula.name: formula.states})}
        elif isinstance(formula, OR):
            allIvars = all_ivars(formula.subs,ivars_parent=ivars)
            SRs = set().union(*[_GSR_SD(sub,iv) for sub,iv in zip(formula.subs,allIvars)])
            if not use_decomposability or not formula.or_decomposable():
                SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        else: # AND case
            allIvars = all_ivars(formula.subs,ivars_parent=ivars)
            SRs = cartesian_product([_GSR_SD(sub,iv) for sub,iv in zip(formula.subs,allIvars)],append_func=terms_appended)
            SRs = SRs - {TERMFALSE} #### TEMP
            if not use_decomposability or not formula.and_decomposable():
                SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        SRs = prune(SRs,ivars)
        return SRs
    @lru_cache(maxsize=CACHE_SIZE)
    def _SR_SD(formula) -> set[Term]:
        nonlocal srCount
        srCount += 1
        if isinstance(formula, Lit):
            SRs = {Term({formula.name: formula.states})}
        elif isinstance(formula, OR):
            SRs = set().union(*[_SR_SD(sub) for sub in formula.subs])
            if not use_decomposability or not formula.or_decomposable():
                SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        else: # AND case
            SRs = cartesian_product([_SR_SD(sub) for sub in formula.subs],append_func=terms_appended)
            SRs = SRs - {TERMFALSE} ### TEMP
            if not use_decomposability or not formula.and_decomposable():
                SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        return SRs
    
    if var_min:
        SRs = _GSR_SD(formula=formula,ivars=frozenset(formula.iter_var_and_states().keys()))
    else:
        SRs = _SR_SD(formula=formula)
    return SRs,srCount
    