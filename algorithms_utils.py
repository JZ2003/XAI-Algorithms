from NNF import *
from TermAndClause import *
from itertools import product


def remove_subsumed(elements: set[HashDict], subsume_func) -> set[HashDict]:
    """
    Given a set of elements (terms or clauses), remove elements that are subsumed by any other element.
    subsume_func: either clause_remove_subsumed or term_remove_subsumed
    return: A set of elements with the subsumed ones removed.
    """
    elements = list(elements)
    subsumed_indices = set()
    for i, elementA in enumerate(elements):
        for j, elementB in enumerate(elements):
            if i != j and subsume_func(elementA, elementB):
                subsumed_indices.add(j)
    return set(element for i, element in enumerate(elements) if i not in subsumed_indices)


def cartesian_product(list_elements: list[set[HashDict]], append_func) -> set[HashDict]:
    """
    Generate the Cartesian product of a list of sets of elements (terms or clauses), applying an append function
    to each combination.
    append_func : either terms_appended or clauses_appended
    return : A list of elements of all combinations in the Cartesian product.
    """

    combinations = product(*list_elements)
    res = set(append_func(combination) for combination in combinations)
    return res

