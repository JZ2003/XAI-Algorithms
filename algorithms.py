from NNF import *
import typing as t
from algorithms_utils import *

Term = HashDict
Clause = HashDict


# def NR_monotone(formula:NNF,check_correctness=False) -> set[NNF]:
#     '''
#     Given a monotone NNF, return the set of all its prime implicates.
#     '''
#     def _NR(formula:NNF) -> set[frozenset[str]]:
#         if not formula.monotone(): 
#             raise ValueError('NR algorithm only works on monotone NNF')
#         if isinstance(formula, Lit):
#             NRs = {frozenset([str(formula)])}
#         elif isinstance(formula, AND):
#             NRs = set().union(*[_NR(sub) for sub in formula.subs])
#             NRs = remove_subsumed(NRs)
#         else: # OR case
#             NRs = cartesian_product([_NR(sub) for sub in formula.subs])
#             if not formula.or_decomposable():
#                 NRs = remove_subsumed(NRs)
#         return NRs

#     NRs = _NR(formula)
#     NRs = {OR(subs=tuple(Lit.from_string(s) for s in x)) for x in NRs}
#     return NRs

def SR_monotone(formula:NNF,check_correctness=False) -> set[NNF]:
    '''
    Given a monotone NNF, return the set of all its prime implicants.
    '''

    if check_correctness:
        if not formula.monotone(): 
            raise ValueError('NR algorithm only works on monotone NNF')

    def _SR(formula) -> set[Term]:
        if isinstance(formula, Lit):
            SRs = {Term({formula.name: formula.states})}
        elif isinstance(formula, OR):
            SRs = set().union(*[_SR(sub) for sub in formula.subs])
            SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        else: # AND case
            # print(f"formula: {formula}, type: {type(formula)}")
            SRs = cartesian_product([_SR(sub) for sub in formula.subs],append_func=terms_appended)
            SRs = remove_subsumed(SRs,subsume_func=term_subsume)
        return SRs

    SRs = _SR(formula)
    return SRs

# def SR(formula:NNF,check_correctness=False) -> set[NNF]:
#     '''
#     Given a monotone NNF, return the set of all its prime implicants.
#     '''

#     if check_correctness:
#         if not formula.monotone(): 
#             raise ValueError('NR algorithm only works on monotone NNF')

#     def _SR(formula:NNF) -> set[Term]:
#         if not formula.monotone(): 
#             raise ValueError('NR algorithm only works on monotone NNF')
#         if isinstance(formula, Lit):
#             SRs = {frozenset([str(formula)])}
#         elif isinstance(formula, OR):
#             SRs = set().union(*[_SR(sub) for sub in formula.subs])
#             SRs = remove_subsumed(SRs)
#         else: # AND case
#             SRs = cartesian_product([_SR(sub) for sub in formula.subs])
#             if not formula.or_decomposable():
#                 SRs = remove_subsumed(SRs)
#         return SRs

#     SRs = _SR(formula)
#     SRs = {AND(subs=tuple(Lit.from_string(s) for s in x)) for x in SRs}
#     return SRs