from typing import Self


class StatusFSM:
    @classmethod
    def _get_transitions(cls) -> dict[Self, list[Self]]:
        raise NotImplementedError("Subclasses must implement _get_transitions()")

    @classmethod
    def can_transition_to(cls, from_state: Self, to_state: Self) -> bool:
        """Check if transitioning from `from_state` to `to_state` is valid."""
        transitions = cls._get_transitions()
        return to_state in transitions.get(from_state, [])

    @classmethod
    def get_valid_transitions(cls, from_state: Self) -> list[Self]:
        """Get all valid next states for a given `from_state`."""
        return cls._get_transitions().get(from_state, [])
