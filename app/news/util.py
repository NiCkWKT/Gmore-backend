def split_summary(summary):
    points = summary.split("@@@@")
    lines = [line.strip() for line in points]
    lines = [line.strip("\n") for line in lines]
    lines = [line.lstrip("- ") for line in lines]
    return lines
