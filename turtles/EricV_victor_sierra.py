import turtle

class victor_sierra:
    def __init__(self, diam):
        self.diam = diam
    
    def triangle(self, angle):
        turtle.right(angle)

        for i in range(3):

            turtle.forward(self.diam)
            turtle.right(120)
        



    def pattern(self):
        for i in range(3):
            turtle.home()
            turtle.left(90)
            angle = i*120
            print(f"triangle {i} at angle {angle}")
            self.triangle(angle)
    def circle(self):
        turtle.penup()
        turtle.goto(0, -self.diam)
        turtle.pendown()
        turtle.circle(self.diam)
        turtle.penup()
        turtle.home()
        turtle.pendown()
        
def main():
    
    vs = victor_sierra(250)
    vs.circle()
    vs.pattern()
    turtle.done()
if __name__ == "__main__":
    main()