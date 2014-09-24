import game

####   QUERY GAME TYPE  ####
####   QUERY PLAYER COLORS, TEAMS  ####
####   QUERY POWER SELECTION   ####
####   SETUP GAME   ####

####   START TURN: WHOSE TURN?   ####
####   PRESENT, CHOOSE, EXECUTE ACTION   ####
####   DRAW TO FIVE   ####


####   WHENEVER HALTS:   ####
####   CREATE REPORT OBJECT   ####
####   CREATE QUERY OBJECT   ####
####   FORMAT R & Q OBJECTS   ####
####   PRESENT UPON REQUEST FORMATTED OUTPUT   ####

####                        POST                    ####
####            Present Option List, ask for input  ####
####                Default option list: what game? ####

####                    GET                         ####
####                Execute Action                  ####
####               if not firstturn: Draw to 5      ####
####                Who's turn is it?               ####
####             What options do they have?         ####
####                Create Option List              ####





def post():
    pass
    """
    Check who you are
    Show you public info + private info
    if you have an option tray, show that
    """

def get():
    pass
    """
    check who you are
    pass your choice to your option tray
    now what?  Create a new option tray eventually
    post()
    """


def now_what():
    check suffering: cry (turn order), attack, dashing strike
        if so create opt table for that suffering
    else w
