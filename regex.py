from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current ctate
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):

    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False


class TerminationState(State):

    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """

    def __init__(self):
        super().__init__()
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return True


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    def __init__(self, symbol: str) -> None:
        super().__init__()
        if not (symbol.isascii() and len(symbol) == 1 and (symbol.isalpha() or symbol.isdigit())):
            raise AttributeError(f"Symbol '{symbol}' is not supported")
        self.next_states = []
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym


class StarState(State):

    def __init__(self, checking_state: State):
        super().__init__()
        self.next_states = [checking_state]

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True
        return False


class PlusState(State):

    def __init__(self, checking_state: State):
        super().__init__()
        self.next_states = [checking_state]

    def check_self(self, char):
        for state in self.next_states:
            if state.check_self(char):
                return True
        return False


class RegexFSM:

    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            tmp_next_state = self.__init_next_state(char, prev_state, tmp_next_state)
            prev_state.next_states.append(tmp_next_state)

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State) -> State:
        new_state = None

        match next_token:
            case next_token if next_token == ".":
                new_state = DotState()
            case next_token if next_token == "*":
                new_state = StarState(tmp_next_state)
                # here you have to think, how to do it.
                if prev_state.next_states:
                    prev_state.next_states.pop()

            case next_token if next_token == "+":
                new_state = PlusState(tmp_next_state)
                if prev_state.next_states:
                    prev_state.next_states.pop()

            case next_token if next_token.isascii():
                new_state = AsciiState(next_token)

            case _:
                raise AttributeError("Character is not supported")

        return new_state

    def check_string(self, string: str) -> bool:
        states = self.curr_state.next_states

        def match(state_idx: int, str_idx: int) -> bool:
            if state_idx == len(states):
                return str_idx == len(string)

            state = states[state_idx]

            if isinstance(state, (StarState, PlusState)):
                i = str_idx
                stops = [i]
                while i < len(string) and state.check_self(string[i]):
                    i += 1
                    stops.append(i)
                if isinstance(state, PlusState):
                    stops = stops[1:]
                for new_i in reversed(stops):
                    if match(state_idx + 1, new_i):
                        return True
                return False

            if str_idx < len(string) and state.check_self(string[str_idx]):
                return match(state_idx + 1, str_idx + 1)
            return False

        return match(0, 0)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"

    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))  # True
    print(regex_compiled.check_string("meow"))  # False
