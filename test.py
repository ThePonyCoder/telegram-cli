import curses
from time import sleep


main_window = curses.initscr()
curses.start_color()


curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
names = ['asdzxc','pony 123', 'alekseB', 'amazonka', 'zver1337', 'aleluja']
for id,i in enumerate(names+names):
    main_window.insstr(id,1,f'{id:>2}  {i}',curses.color_pair(1) | curses.A_BOLD)
main_window.refresh()

# curses.flash()
# curses.echo()
