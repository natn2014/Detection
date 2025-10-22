class Sequence:
    """Represents a sequence configuration."""
    
    def __init__(self, seq_type='simple', logic=None, di1=None, di2=None, do=None, duration=0, steps=None, initial_states=None, end_states=None, return_to_initial=True):
        self.seq_type = seq_type
        self.logic = logic
        self.di1 = di1
        self.di2 = di2
        self.do = do
        self.duration = duration
        self.steps = steps or []
        self.initial_states = initial_states or {}
        self.end_states = end_states or {}
        self.return_to_initial = return_to_initial

    def to_dict(self):
        """Convert the sequence configuration to a dictionary."""
        seq_dict = {
            'type': self.seq_type,
            'logic': self.logic,
            'di1': self.di1,
            'di2': self.di2,
            'do': self.do,
            'duration': self.duration,
            'steps': self.steps,
            'initial_states': self.initial_states,
            'end_states': self.end_states,
            'return_to_initial': self.return_to_initial
        }
        return seq_dict

    @classmethod
    def from_dict(cls, data):
        """Create a Sequence instance from a dictionary."""
        return cls(
            seq_type=data.get('type', 'simple'),
            logic=data.get('logic'),
            di1=data.get('di1'),
            di2=data.get('di2'),
            do=data.get('do'),
            duration=data.get('duration', 0),
            steps=data.get('steps', []),
            initial_states=data.get('initial_states', {}),
            end_states=data.get('end_states', {}),
            return_to_initial=data.get('return_to_initial', True)
        )