import pyfiglet
from termcolor import colored

# Create ASCII art using pyfiglet
ascii_art = pyfiglet.figlet_format("PDFInjector", font="slant")
ascii_art_author = pyfiglet.figlet_format("By Kdairatchi", font="digital")

# Print the ASCII art with colors
print(colored(ascii_art, 'cyan'))
print(colored(ascii_art_author, 'magenta'))
