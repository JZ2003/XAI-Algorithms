import typing as t
from collections import defaultdict 

class NNF:
    def __init__(self) -> None:
        pass
    
    def __mul__(self,RHS:'NNF') -> 'AND': #AND
        if isinstance(self,AND) and isinstance(RHS,AND):
            return AND((*self.subs,*RHS.subs))
        elif isinstance(self,AND):
            return AND((*self.subs,RHS))
        elif isinstance(RHS,AND):
            return AND((self,*RHS.subs))
        else:
            return AND((self,RHS))

    def __add__(self,RHS:'NNF') -> 'OR': #OR
        if isinstance(self,OR) and isinstance(RHS,OR):
            return OR((*self.subs,*RHS.subs))
        elif isinstance(self,OR):
            return OR((*self.subs,RHS))
        elif isinstance(RHS,OR):
            return OR((self,*RHS.subs))
        else:
            return OR((self,RHS))

    def iter_var_and_states(self) -> dict[str, set[tuple[int,bool]]]:
        dictionary = defaultdict(set)
        def _iter_var_and_states(formula:'NNF',dictionary:dict) -> None:
            if isinstance(formula,Var):
                dictionary[formula.name].add((formula.state,formula.negated))
            else: #AND or OR
                for sub in formula.subs:
                    _iter_var_and_states(sub,dictionary)
        _iter_var_and_states(self,dictionary)
        return dictionary

    def satisfied_by(self, world:dict[str,int]) -> bool:
        '''Determine if the NNF is satisfied by a world'''

        def _satisfied_by(formula:'NNF',world:dict[str,int]) -> bool:
            if isinstance(formula, Var):
                name, state, negated = formula.name, formula.state, formula.negated
                if name not in world:
                    raise ValueError("The world has different set of variables than the NNF")
                else:
                    characteristic:int = world[name]
                    if not negated and characteristic == state:
                        return True
                    elif negated and characteristic != state:
                        return True
                    else:
                        return False
            elif isinstance(formula, AND):
                return all(_satisfied_by(sub,world) for sub in formula.subs)
            else: # OR case
                return any(_satisfied_by(sub,world) for sub in formula.subs)
                
        return _satisfied_by(self, world)

    def monotone(self) -> bool:
        '''
        Return True if the NNF is monotone.
        Monotone NNF is positive has only one state for each variable.
        '''
        for var,setOfStates in self.iter_var_and_states().items():
            if len(setOfStates) != 1: return False # Must only have one state
            for t in setOfStates: # Must be positive
                if t[1] is True: return False 
        return True

    def or_decomposable(self) -> bool:

        def _or_decomposable(formula:'NNF') -> bool:
            if isinstance(formula,Var):
                return True
            elif isinstance(formula,AND):
                return all(_or_decomposable(sub) for sub in formula.subs)
            else:# OR case
                if len(formula.subs) == 0: return True
                for sub in formula.subs:
                    if sub.iter_var_and_states().keys() != formula.subs[0].iter_var_and_states().keys():
                        return False
                return all(_or_decomposable(sub) for sub in formula.subs)

        return _or_decomposable(self)

class Var(NNF):
    def __init__(self,name:str,state:int) -> None:
        self.name = name
        self.state = state
        self.negated = False
    
    def __str__(self):
        """String representation for encoding."""
        return f"{self.name}_{self.state}" if not self.negated else f"~{self.name}_{self.state}"

    @classmethod
    def from_string(cls, encoded_str):
        """Create a Var instance from a string."""
        if encoded_str[0] == '~':
            name, state = encoded_str[1:].split('_')
            neg = True
        else:
            name, state = encoded_str.split('_')
            neg = False
        var = cls(name, int(state))
        var.negated = neg
        return var


    def __hash__(self) -> int:
        return hash((self.name,self.state,self.negated))

    def __invert__(self) -> 'Var':
        negVar = Var(self.name,self.state)
        negVar.negated = not self.negated
        return negVar

class AND_OR(NNF):
    pass

class AND(AND_OR):
    def __init__(self,subs:t.Iterable) -> None:
        self.subs:NNF = subs

    def __str__(self) -> str:
        if len(self.subs) == 0: return "True"
        subStrs = [str(s) for s in self.subs]
        s = subStrs[0]
        for x in subStrs[1:]:
            s += "*" + x
        return "(" + s + ")"

    
    def __hash__(self) -> int:
        return hash(('AND',self.subs))


class OR(AND_OR):
    def __init__(self,subs:t.Iterable) -> None:
        self.subs:NNF = subs

    def __hash__(self) -> int:
        return hash(('OR',self.subs))

    def __str__(self) -> str:
        if len(self.subs) == 0: return "False"
        subStrs = [str(s) for s in self.subs]
        s = subStrs[0]
        for x in subStrs[1:]:
            s += "+" + x
        return "(" + s + ")"

TRUE = AND(())
FALSE = OR(())


