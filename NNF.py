import typing as t
from collections import defaultdict 

class NNF:
    def __init__(self) -> None:
        ...

    # @classmethod
    # def from_string(cls,encoded_str:str) -> 'NNF':
        
    def __mul__(self,RHS:'NNF') -> 'AND': #AND
        ...

    def __add__(self,RHS:'NNF') -> 'OR': #OR
        ...

    def satisfied_by(self, world:dict[str,int]) -> bool:
        '''
        Determine if the NNF is satisfied by a world.
        A world is represented as a dictionary[varName: state].
        '''
        return self._satisfied_by(world)

    def iter_var_and_states(self) -> dict[str, set[tuple[int,bool]]]:
        '''
        Return a dictionary that lists all the variables and states that occur 
        in a NNF. dict[varName:(state,negated)]
        '''
        dictionary = defaultdict(set)
        self._iter_var_and_states(dictionary)
        return dictionary

    def or_decomposable(self) -> bool:
        '''
        Determines whether the NNF is or_decomposable.
        A NNF is or_decomposable iff all disjuncts in it don't share variables.
        '''
        return self._or_decomposable()

    def monotone(self) -> bool:
        '''
        Return True if the NNF is monotone.
        Monotone NNF is positive iff it uses only one state for each variable.
        '''
        for var,setOfStates in self.iter_var_and_states().items():
            if len(setOfStates) != 1: return False # Must only have one state
            for t in setOfStates: # Must be positive
                if t[1] is True: return False 
        return True


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

    def __mul__(self,RHS:NNF) -> 'AND': #AND
        if isinstance(RHS,AND):
            return AND((self,*RHS.subs))
        else:
            return AND((self,RHS))

    def __add__(self,RHS:'NNF') -> 'OR': #OR
        if isinstance(RHS,OR):
            return OR((self,*RHS.subs))
        else:
            return OR((self,RHS))

    def _satisfied_by(self,world:dict[str,int]) -> bool:
        name, state, negated = self.name, self.state, self.negated
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

    def _iter_var_and_states(self,dictionary:dict) -> None:
        dictionary[self.name].add((self.state,self.negated))

    def _or_decomposable(self) -> bool:
        return True

    def __hash__(self) -> int:
        return hash((self.name,self.state,self.negated))

    def __invert__(self) -> 'Var':
        negVar = Var(self.name,self.state)
        negVar.negated = not self.negated
        return negVar

class AND_OR(NNF):
    def _iter_var_and_states(self,dictionary:dict) -> None:
        for sub in self.subs:
            sub._iter_var_and_states(dictionary)

class AND(AND_OR):
    def __init__(self,subs:t.Iterable) -> None:
        self.subs:NNF = subs

    def __mul__(self,RHS:NNF) -> 'AND': #AND
        if isinstance(RHS,AND):
            return AND((*self.subs,*RHS.subs))
        else:
            return AND((*self.subs,RHS))

    def __add__(self,RHS:'NNF') -> 'OR': #OR
        if isinstance(RHS,OR):
            return OR((self,*RHS.subs))
        else:
            return OR((self,RHS))

    def _satisfied_by(self,world:dict[str,int]) -> bool:  
        return all(sub._satisfied_by(world) for sub in self.subs)

    def _or_decomposable(self) -> bool:
        return all(sub._or_decomposable() for sub in self.subs)


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

    def __mul__(self,RHS:NNF) -> 'AND': #AND
        if isinstance(RHS,AND):
            return AND((self,*RHS.subs))
        else:
            return AND((self,RHS))
    
    def __add__(self,RHS:'NNF') -> 'OR': #OR
        if isinstance(RHS,OR):
            return OR((*self.subs,*RHS.subs))
        else:
            return OR((*self.subs,RHS))

    def _satisfied_by(self,world:dict[str,int]) -> bool:
        return any(sub._satisfied_by(world) for sub in self.subs)

    def _or_decomposable(self) -> bool:
        if len(self.subs) == 0: return True
        for sub in self.subs[1:]:
            if not set(sub.iter_var_and_states().keys()).isdisjoint(set(self.subs[0].iter_var_and_states().keys())):
                return False
        return all(sub._or_decomposable() for sub in self.subs)

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


