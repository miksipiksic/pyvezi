import sys
import traceback
import pygame

from game import Game

try:
    module_agents = __import__('agents')
    first_agent_class = getattr(module_agents, sys.argv[1] if len(sys.argv) > 1 else 'Human')
    second_agent_class = getattr(module_agents, sys.argv[2] if len(sys.argv) > 2 else 'ExampleAgent')
    max_depth = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    max_think_time = int(sys.argv[4]) if len(sys.argv) > 4 else 10
    actions_filename = sys.argv[5] if len(sys.argv) > 5 else None
    g = Game([first_agent_class(), second_agent_class()], max_depth, max_think_time, actions_filename)
    g.run()
except (Exception,):
    traceback.print_exc()
    input()
finally:
    pygame.display.quit()
    pygame.quit()
