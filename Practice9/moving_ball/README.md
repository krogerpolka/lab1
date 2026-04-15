3.3 Moving Ball Game
Objective: Create an interactive game with a moving red ball

Requirements:

Display a red ball (50x50 pixels, radius 25) on white background
Move ball with arrow keys (Up, Down, Left, Right)
Each key press moves ball by 20 pixels
Ball cannot leave the screen boundaries
Ignore input that would move ball off-screen
Implementation Tips:

Use pygame.draw.circle() for the ball
Handle keyboard events
Check boundary conditions before moving
Smooth animation with frame rate control