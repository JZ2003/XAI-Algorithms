import typing as t
from collections import defaultdict 


"""
NOTE: A bug need to be solved: satified_by() function. 
Short-circuit of the any() function will prevent it from raising errors.
"""

"""
NOTE: Right now, functions like _simplify are not cached. Functions like them are pure 
functions, so we can exploit this property and cache their results.
"""

class NNF:
    def __init__(self) -> None:
        self.simplified = None
        
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

    def iter_var_and_states(self) -> dict[str, set[int]]:
        '''
        Return a dictionary that lists all the variables and states that occur 
        in a NNF. dict[varName:set[states]]
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
    
    def and_decomposable(self) -> bool:
        '''
        Determines whether the NNF is and_decomposable.
        A NNF is and_decomposable iff all conjuncts in it don't share variables.
        '''
        return self._and_decomposable()

    def monotone(self) -> bool:
        """
        A NNF is monotone iff for each Variable X, All X-literals are simple and the same.
        """
        for var, states in self.iter_var_and_states().items():
            if len(states) > 1: 
                return False
        return True
    


class Lit(NNF):
    def __init__(self,name:str,states:t.Iterable[int]) -> None:
        super().__init__()
        self.name = name
        self.states = frozenset(states)
        self.simplified = True
    
    def _simplify(self) -> None:
        return

    def __str__(self):
        """String representation for encoding."""
        stateStr = ""
        for i,s in enumerate(self.states):
            stateStr += str(s) 
            if i != len(self.states)-1:
                stateStr += ","
        return f"{self.name}[{stateStr}]"

    @classmethod
    def from_string(cls, encoded_str):
        """Create a Lit instance from a string."""
        start_bracket = encoded_str.find('[')
        end_bracket = encoded_str.rfind(']')

        if start_bracket != -1 and end_bracket != -1 and start_bracket < end_bracket:
            nameStr = encoded_str[:start_bracket]
            stateStr = encoded_str[start_bracket+1:end_bracket]
            stateSet = set()
            for num in stateStr.split(","):
                try:
                    stateSet.add(int(num))
                except:
                    raise ValueError
            return cls(nameStr,stateSet)
        else:
            raise ValueError


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
        # name, state, negated = self.name, self.state, self.negated
        name, state = self.name, self.states
        if name not in world:
            raise ValueError("The world has different set of variables than the NNF")
        else:
            characteristic:int = world[name]
            return characteristic in state

    def _iter_var_and_states(self,dictionary:dict) -> None:
        # dictionary[self.name].add((self.state,self.negated))
        dictionary[self.name] =  dictionary[self.name].union(self.states)

    def _or_decomposable(self) -> bool:
        return True #Emmmmmmmmm
    
    def _and_decomposable(self) -> bool:
        return True

    def __hash__(self) -> int:
        return hash((self.name,self.states))
    

class AND_OR(NNF):
    def __init__(self) -> None:
        super().__init__()

    def _iter_var_and_states(self,dictionary:dict) -> None:
        for sub in self.subs:
            sub._iter_var_and_states(dictionary)
    

class AND(AND_OR):
    def __init__(self,subs:t.Iterable) -> None:
        super().__init__()
        self.subs:NNF = subs
        self._simplify()

    def _simplify(self) -> None:
        if not self.simplified:
            newSubs = []
            for sub in self.subs:
                if isinstance(sub,AND):
                    for ss in sub.subs: 
                        ss._simplify()
                    newSubs.extend(sub.subs)
                else:
                    sub._simplify()
                    newSubs.append(sub)
            self.subs = newSubs      
        self.simplified = True
        
    def __mul__(self,RHS:NNF) -> 'AND': #AND
        if isinstance(RHS,AND):
            newNode = AND([*self.subs,*RHS.subs])
            return newNode
        else:
            newNode = AND([*self.subs,RHS])
            return newNode

    def __add__(self,RHS:'NNF') -> 'OR': #OR
        if isinstance(RHS,OR):
            newNode = OR([self,*RHS.subs])
            return newNode
        else:
            newNode = OR([self,RHS])
            return newNode

    def _satisfied_by(self,world:dict[str,int]) -> bool:  
        return all(sub._satisfied_by(world) for sub in self.subs)

    def _or_decomposable(self) -> bool:
        return all(sub._or_decomposable() for sub in self.subs)

    def _and_decomposable(self) -> bool:
        listSubVars = [set(sub.iter_var_and_states().keys()) for sub in self.subs]
        combinedSet = set().union(*listSubVars)
        sizeSumIndividuals = sum(len(s) for s in listSubVars)
        if len(combinedSet) != sizeSumIndividuals:
            return False
        return all(sub._and_decomposable() for sub in self.subs)

    def __str__(self) -> str:
        if len(self.subs) == 0: return "True"
        subStrs = [str(s) for s in self.subs]
        s = subStrs[0]
        for x in subStrs[1:]:
            s += "*" + x
        return "(" + s + ")"

    @classmethod
    def from_string(cls,s:str):
        subs = s.split("*")
        return cls(subs=[Lit.from_string(sub) for sub in subs])

    
    def __hash__(self) -> int:
        return hash(('AND',self.subs))
    
    def is_clause(self) -> bool:
        return False

    def is_term(self) -> bool:
        if self.term is None:
            term = all(isinstance(s,Lit) for s in self.subs)
            self.term = term
        return self.term

class OR(AND_OR):
    def __init__(self,subs:t.Iterable) -> None:
        super().__init__()
        self.subs:NNF = subs
        self._simplify()
    
    def _simplify(self) -> None:
        if not self.simplified:
            newSubs = []
            for sub in self.subs:
                if isinstance(sub,OR):
                    for ss in sub.subs: 
                        ss._simplify()
                    newSubs.extend(sub.subs)
                else:
                    sub._simplify()
                    newSubs.append(sub)
            self.subs = newSubs      
        self.simplified = True


    def __mul__(self,RHS:NNF) -> 'AND': #AND
        if isinstance(RHS,AND):
            newNode = AND([self,*RHS.subs])
            return newNode
        else:
            newNode = AND([self,RHS])
            return newNode
    
    def __add__(self,RHS:'NNF') -> 'OR': #OR
        if isinstance(RHS,OR):
            newNode = OR([*self.subs,*RHS.subs])
            return newNode
        else:
            newNode = OR([*self.subs,RHS])
            return newNode

    def _satisfied_by(self,world:dict[str,int]) -> bool:
        return any(sub._satisfied_by(world) for sub in self.subs)

    def _or_decomposable(self) -> bool:
        if len(self.subs) == 0: return True
        listSubVars = [set(sub.iter_var_and_states().keys()) for sub in self.subs]
        combinedSet = set().union(*listSubVars)
        sizeSumIndividuals = sum(len(s) for s in listSubVars)
        if len(combinedSet) != sizeSumIndividuals:
            return False
        return all(sub._or_decomposable() for sub in self.subs)
    
    def _and_decomposable(self) -> bool:
        return all(sub._and_decomposable() for sub in self.subs)

    def __hash__(self) -> int:
        return hash(('OR',self.subs))

    def __str__(self) -> str:
        if len(self.subs) == 0: return "False"
        subStrs = [str(s) for s in self.subs]
        s = subStrs[0]
        for x in subStrs[1:]:
            s += "+" + x
        return "(" + s + ")"
    
    @classmethod
    def from_string(cls,s:str):
        subs = s.split("+")
        return cls(subs=[Lit.from_string(sub) for sub in subs])



TRUE = AND([])
FALSE = OR([])


