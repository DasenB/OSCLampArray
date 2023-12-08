
class Box:
    id: str
    description: str
    value: int
    selected: bool
    disabled: bool
    position: (int, int)
    size: (int, int)
    on_message: str
    off_message: str
    value_message: str

    def __init__(self, id: str, description: str = "", on_message: str = "", off_message: str = "", value_message: str = "") -> None:
        self.id = id
        self.value = 0
        self.selected = False
        self.disabled = True
        self.position = (100, 300)
        self.size = (50, 50)
        self.on_message = on_message
        self.off_message = off_message
        self.value_message = value_message
        if description != "":
            self.description = description
        else:
            self.description = str(self.id)
