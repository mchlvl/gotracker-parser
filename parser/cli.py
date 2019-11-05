from main import load_data, classify, method_pointer
import argparse

parser = argparse.ArgumentParser(description="Input arguments")
parser.add_argument(
    "-n",
    "--numberlogs",
    dest="nlogs",
    type=int,
    default=1,
    help="Time selection - last N logs available are selected",
)
parser.add_argument(
    "-p",
    "--per",
    dest="per",
    type=str.lower,
    default="day",
    choices=["day", "week", "month", "year"],
    help="Group results by",
)
parser.add_argument(
    "-l",
    "--level",
    dest="level",
    type=int,
    default=0,
    choices=[0, 1, 2, 3, 4, 5, 6, 7],
    help="Aggregation level.",
)
parser.add_argument(
    "-d",
    "--detailed",
    dest="detailed",
    default=False,
    action="store_true",
    help="Display detailed result breakdown (level 5).",
)
parser.add_argument(
    "-nl",
    "--nlargest",
    dest="nlargest",
    type=int,
    default=10,
    help="Number of records per aggregation level to display.",
)
parser.add_argument(
    "-m",
    "--minduration",
    dest="minduration",
    type=int,
    default=120,
    help="Duration in secods that need to be satisfied on aggregate level.",
)
parser.add_argument(
    "-i",
    "--resetindex",
    dest="resetindex",
    default=False,
    action="store_true",
    help="Whether the full index is to be displayed. Recommended for further cmd filtering.",
)
parser.add_argument(
    "-f", "--find", dest="find", default="", type=str.lower, help="String to find"
)

args = parser.parse_args()
level = args.level
if args.detailed and level < 5:
    level = 5
data = load_data(time_recency=args.nlogs)
classify(data)
method_pointer(
    data, level, args.nlargest, args.per, args.minduration, args.resetindex, args.find
)
