class Element:
    def __init__(self, screen, pos):
        self.screen = screen
        self.pos = pos

    def get_pos(self):
        return self.pos
    
    def get_bounds(self):
        pass

    def draw(self):
        pass

    def click(self):
        print("test")