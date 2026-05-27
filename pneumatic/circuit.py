from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Component:
    comp_type: str          # "cylinder_da", "cylinder_sa", "valve_52", "valve_42",
                            # "valve_32", "valve_22", "flow_control", "check_valve",
                            # "pressure_regulator", "gauge", "supply", "exhaust"
    label: str
    tag: str                # e.g. "CYL1", "V1"
    actuator: str = ""      # solenoid, spring, manual, pilot — for valves
    spring_return: bool = True   # for valves
    position: tuple[int, int] = (0, 0)   # grid col, row


@dataclass
class Connection:
    from_tag: str
    from_port: str
    to_tag: str
    to_port: str


@dataclass
class Circuit:
    title: str = "Pneumatic Circuit"
    drawn_by: str = ""
    date: str = ""
    components: list[Component] = field(default_factory=list)
    connections: list[Connection] = field(default_factory=list)

    def add(self, component: Component) -> None:
        self.components.append(component)

    def connect(self, from_tag: str, from_port: str, to_tag: str, to_port: str) -> None:
        self.connections.append(Connection(from_tag, from_port, to_tag, to_port))

    def get(self, tag: str) -> Optional[Component]:
        for c in self.components:
            if c.tag == tag:
                return c
        return None
