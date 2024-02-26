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
        self.clause = None
        self.term = None
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

    def monotone(self) -> bool:
        """
        A NNF is monotone iff for each Variable X, All X-literals are simple and the same.
        """
        for var, states in self.iter_var_and_states().items():
            if len(states) > 1: 
                return False
        return True
    
    def is_clause(self) -> bool:
        ...

    def is_term(self) -> bool:
        ...


class Lit(NNF):
    def __init__(self,name:str,states:t.Iterable[int]) -> None:
        self.name = name
        self.states = frozenset(states)
        self.clause = True
        self.term = True
        self.simplified = True
    
    def __str__(self):
        """String representation for encoding."""
        # return f"{self.name}_{self.state}" if not self.negated else f"~{self.name}_{self.state}"
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
            # if not negated and characteristic == state:
            #     return True
            # elif negated and characteristic != state:
            #     return True
            # else:
            #     return False

    def _iter_var_and_states(self,dictionary:dict) -> None:
        # dictionary[self.name].add((self.state,self.negated))
        dictionary[self.name] =  dictionary[self.name].union(self.states)

    def _or_decomposable(self) -> bool:
        return True #Emmmmmmmmm

    def __hash__(self) -> int:
        return hash((self.name,self.states))

    def is_clause(self) -> bool:
        return True
    
    def is_term(self) -> bool:
        return True


class AND_OR(NNF):
    def _iter_var_and_states(self,dictionary:dict) -> None:
        for sub in self.subs:
            sub._iter_var_and_states(dictionary)
    def subsume(self,RHS:NNF) -> bool:
        ...

class AND(AND_OR):
    def __init__(self,subs:t.Iterable) -> None:
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
            if self.is_term() and RHS.is_term():
                newNode.term = True
            newNode.clause = False
            return newNode
        else:
            newNode = AND([*self.subs,RHS])
            newNode.term = False
            newNode.clause = False
            return newNode

    def __add__(self,RHS:'NNF') -> 'OR': #OR
        if isinstance(RHS,OR):
            newNode = OR([self,*RHS.subs])
            newNode.clause = False
            newNode.term = False
            return newNode
        else:
            newNode = OR([self,RHS])
            newNode.clause = False
            newNode.term = False
            return newNode

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
    
    def subsume(self,RHS) ->bool:
        if self.is_term() and RHS.is_term():
            pass
        else:
            raise ValueError("Only terms have subsumption relationship")
        

class OR(AND_OR):
    def __init__(self,subs:t.Iterable) -> None:
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
            newNode.clause = False
            newNode.term = False
            return newNode
        else:
            newNode = AND([self,RHS])
            newNode.term = False
            newNode.clause = False
            return newNode
    
    def __add__(self,RHS:'NNF') -> 'OR': #OR
        if isinstance(RHS,OR):
            newNode = OR([*self.subs,*RHS.subs])
            if self.is_clause() and RHS.is_clause():
                newNode.clause = True
            newNode.term = False
            return newNode
        else:
            newNode = OR([*self.subs,RHS])
            newNode.term = False
            RHS.term = False
            return newNode

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
    
    @classmethod
    def from_string(cls,s:str):
        subs = s.split("+")
        return cls(subs=[Lit.from_string(sub) for sub in subs])

    def is_clause(self) -> bool:
        if self.clause is None:
            clause = all(isinstance(s,Lit) for s in self.subs)
            self.clause = clause
        return self.clause


class Term(AND):
    def __init__(self,subs:Lit,correctness_check=False):
        self.simplified = True
        self.subs = subs
        if correctness_check:
            self._correctness_check()
        self.subsDict = {sub.name:sub.states for sub in self.subs}
    
    def _correctness_check(self):
        subs = self.subs
        for sub in subs:
            if not isinstance(sub,Lit):
                ValueError("Terms only consists of literals (Lit)")
        variables = [sub.name for sub in subs]
        if len(variables) != len(set(variables)):
            raise ValueError("Each elements in a term must be from a distinct variable")
    

    def subsume(self,RHS:'Term') ->bool:
        if isinstance(RHS,Term):
            for varName,states in self.subsDict.items():
                if varName not in RHS.subsDict: #If X-literal doesn't exist in RHS, it's \top
                    return False
                else:
                    statesRHS = RHS.subsDict[varName]
                    if not statesRHS.issubset(states): 
                        return False #Every X-literal of RHS needs to be a subset
            return True
        else:
            raise ValueError("Only two terms can have subsumption relationship")
 

class Clause(OR):
    def __init__(self,subs:Lit,correctness_check=True):
        self.simplified = True
        self.subs = subs
        if correctness_check:
            self._correctness_check()
        self.subsDict = {sub.name:sub.states for sub in self.subs}
    
    def _correctness_check(self):
        subs = self.subs
        for sub in subs:
            if not isinstance(sub,Lit):
                ValueError("Clauses only consists of literals (Lit)")
        variables = [sub.name for sub in subs]
        if len(variables) != len(set(variables)):
            raise ValueError("Each elements in a clause must be from a distinct variable")


    def subsume(self,RHS) ->bool:
        if isinstance(RHS,Clause):
            for varName,states in self.subsDict.items():
                if varName not in RHS.subsDict: #If X-literal doesn't exist in RHS, it's \bot
                    return False
                else:
                    statesRHS = RHS.subsDict[varName]
                    if not states.issubset(statesRHS): 
                        return False #Every X-literal of RHS needs to be a superset
            return True
        else:
            raise ValueError("Only two clauses can have subsumption relationship")






TRUE = AND([])
FALSE = OR([])


