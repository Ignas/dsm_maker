import sys
from . import main


if __name__ == '__main__':
    if len(sys.argv) > 1:
        in_filename = sys.argv[1]
    else:
        in_filename = "graph.dot"
    if len(sys.argv) > 2:
        out_filename = sys.argv[2]
    else:
        out_filename = "result.svg"
    if len(sys.argv) > 3:
        title = sys.argv[3]
    else:
        title = "DSM"

    main(in_filename, out_filename, title)
