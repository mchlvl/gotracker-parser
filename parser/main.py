import os
import pandas as pd
from pathlib import Path
from datetime import time, timedelta
from typing import List


def load_data(time_recency: int = 1) -> pd.DataFrame:
    user = os.environ["USERNAME"]
    directory = fr"C:\Users\{user}\AppData\Roaming\TimeTrackerLogs"

    pathlist = Path(directory).glob("**/*.txt")
    pathlist = filter_pathlist(list(pathlist), time_recency)

    data = pd.DataFrame()
    for path in pathlist:
        data = data.append(pd.read_json(path, lines=True))
    print(
        "INFO: loaded",
        len(pathlist),
        "files resulting in data of size",
        data.shape,
    )

    date = data["Date"].apply(pd.to_datetime)
    data["Year"] = date.dt.year
    data["Month"] = date.dt.month
    data["Week"] = date.dt.week
    data["Day"] = date.dt.day
    return data


def filter_pathlist(pathlist: List[str], time_recency: str) -> List[str]:
    # if time_recency.lower() == "latestday":
    #     return [pathlist[-1]]
    # elif time_recency.lower() == "latestweek":
    #     return pathlist[-7:]
    # else:
    #     raise NotImplementedError(f"time: {time_recency}")
    return pathlist[-time_recency:]


def classify(data: pd.DataFrame) -> None:
    data[["Details", "Project", "ExecutableName"]] = data["Window"].str.rsplit(
        " - ", n=2, expand=True
    )
    # replace with regex
    data.loc[
        data["Project"].isnull(), ["Details", "Project", "ExecutableName"]
    ] = data.loc[data["Project"].isnull(), "Window"].str.rsplit(
        " | ", n=2, expand=True
    )
    ix = data.Project.isnull()
    data.loc[ix, "Project"] = data.loc[ix, "Details"]
    data.loc[ix, "Details"] = None

    ix = data.ExecutableName.isnull()
    data.loc[ix, "ExecutableName"] = data.loc[ix, "Project"]
    data.loc[ix, "Project"] = None

    ix = data.Project.isnull()
    data.loc[ix, "Project"] = data.loc[ix, "Details"]
    data.loc[ix, "Details"] = None
    data.fillna("", inplace=True)


def print_data(agg: pd.DataFrame, reset_index: bool = False) -> None:
    strings = agg.select_dtypes(include=["object"])
    if reset_index:
        agg.reset_index(inplace=True)
    string = agg.to_string()
    string = string.encode("ascii", "replace").decode("ascii")
    print(string)


def fraction(x: pd.Series) -> float:
    return 100 * x / float(x.sum())


def delta_to_string(delta: pd.Series):
    delta = pd.to_timedelta(delta, unit="second")
    return (
        delta.astype(str)
        .str[:-10]
        .str.replace(" days ", "d ")
        .str.replace("0d ", "")
    )


def filter_data(
    data: pd.DataFrame,
    level: int,
    groupby_columns: List[str],
    nlargest: int,
    misc_columns: List[str],
    minduration: float,
) -> pd.DataFrame:
    agg = data.groupby(groupby_columns + misc_columns).DurationSeconds.agg(
        Duration="sum", Count="count"
    )

    agg["DurationExe"] = agg.groupby(groupby_columns + misc_columns[:1])[
        "Duration"
    ].sum()
    agg["%OfExe"] = agg.groupby(groupby_columns + misc_columns[:1])[
        "Duration"
    ].apply(lambda x: fraction(x))
    if level >= 6:
        agg["DurationProject"] = agg.groupby(
            groupby_columns + misc_columns[:3]
        )["Duration"].sum()
        agg["%OfProject"] = agg.groupby(groupby_columns + misc_columns[:3])[
            "Duration"
        ].apply(lambda x: fraction(x))

        agg["DurationProject"] = delta_to_string(agg["DurationProject"])

    agg["DurationTotal"] = agg.groupby(groupby_columns)["Duration"].sum()
    agg["%OfTotal"] = agg["Duration"] / agg["DurationTotal"] * 100
    agg = agg.round(2)
    agg = agg.loc[agg["Duration"] >= minduration, :]

    agg["DurationTotal"] = delta_to_string(agg["DurationTotal"])
    agg["DurationExe"] = delta_to_string(agg["DurationExe"])
    return agg


def fitler_nlargets(
    agg: pd.DataFrame,
    level: int,
    nlargest: int,
    groupby_columns: List[str],
    misc_columns: List[str],
) -> pd.DataFrame:
    # handle by exe
    if level in [5, 7]:
        if level <= 3:
            ix = agg.reset_index()
            ix = ix.groupby(groupby_columns).Duration.nlargest(nlargest)
            agg = agg.iloc[ix.index.get_level_values(-1)]
        else:
            ix = agg.reset_index()
            ix = ix.groupby(
                groupby_columns + misc_columns[:-1]
            ).Duration.nlargest(nlargest)
            agg = agg.iloc[ix.index.get_level_values(-1)]
        agg = agg.sort_values(
            groupby_columns + ["DurationExe", "Duration"], ascending=False
        )
    else:
        ix = agg.reset_index()
        ix = ix.groupby(groupby_columns).Duration.nlargest(nlargest)
        agg = agg.iloc[ix.index.get_level_values(-1)]
        agg = agg.sort_values(groupby_columns + ["Duration"], ascending=False)

    # column cleanup
    if level == 2:
        agg.drop(["DurationExe", "%OfExe"], axis=1, inplace=True)
    return agg


def by_agg(
    data: pd.DataFrame,
    groupby_columns: List[str],
    nlargest: int,
    minduration: int,
    misc_columns: List[str],
) -> pd.DataFrame:
    groupby_columns_ext = groupby_columns + misc_columns
    data["End"] = pd.to_timedelta(data["Start"]) + pd.to_timedelta(
        data.DurationSeconds, unit="second"
    )
    onoff = data.groupby(groupby_columns_ext).Start.agg(["min"])
    onoff["max"] = data.groupby(groupby_columns_ext).End.agg(["max"])
    onoff["PotentialDuration"] = pd.to_timedelta(
        onoff["max"]
    ) - pd.to_timedelta(onoff["min"])

    onoff["RecordedDuration"] = pd.to_timedelta(
        data.groupby(groupby_columns_ext).DurationSeconds.agg(["sum"])["sum"],
        unit="second",
    )
    onoff["%ofPotential"] = (
        onoff["RecordedDuration"] / onoff["PotentialDuration"] * 100
    )
    minduration = pd.to_timedelta(minduration, unit="seconds")
    onoff = onoff.loc[onoff["RecordedDuration"] >= minduration, :]

    ix = onoff.reset_index()
    ix = ix.groupby(groupby_columns).RecordedDuration.nlargest(nlargest)
    onoff = onoff.iloc[ix.index.get_level_values(-1)]

    onoff["RecordedDuration"] = (
        onoff["RecordedDuration"].astype(str).str[-18:-10]
    )
    onoff["PotentialDuration"] = (
        onoff["PotentialDuration"].astype(str).str[-18:-10]
    )
    onoff["max"] = onoff["max"].astype(str).str[-18:-10]
    onoff = onoff.round(2)
    onoff = onoff.sort_values(
        groupby_columns + ["RecordedDuration"], ascending=False
    )
    return onoff


def filter_find(data: pd.DataFrame, find: str) -> pd.DataFrame:
    if find:
        iloc = -1
        if ":" in find:
            iloc, find = find.split(":")
            iloc = -int(iloc)
        ix = data.index.get_level_values(iloc).str.lower().str.contains(find)
        data = data[ix]
    return data


def method_pointer(
    data: pd.DataFrame,
    level: int,
    nlargest: int,
    per: str,
    minduration: int,
    reset_index: bool,
    find: str,
) -> None:

    if per == "day":
        groupby_columns = ["Year", "Month", "Day"]
    elif per == "week":
        groupby_columns = ["Year", "Week"]
    elif per == "month":
        groupby_columns = ["Year", "Month"]
    elif per == "year":
        groupby_columns = ["Year"]

    print(
            f"INFO: Level: '{level}', reports up to '{nlargest}' records (totals) of duration >= '{minduration}s', per '{per}'\n"
        )

    # agg time
    if level == 0:
        misc_columns = []
        agg = by_agg(
            data, groupby_columns, nlargest, minduration, misc_columns
        )
    # agg time + exec
    elif level == 1:
        misc_columns = ["Executable"]
        agg = by_agg(
            data, groupby_columns, nlargest, minduration, misc_columns
        )
    # agg time + exec
    elif level == 2:
        misc_columns = ["Executable"]
        agg = filter_data(
            data, level, groupby_columns, nlargest, misc_columns, minduration
        )
        agg = filter_find(agg, find)
        agg = fitler_nlargets(
            agg, level, nlargest, groupby_columns, misc_columns
        )
    # agg time + exec + exec name
    elif level == 3:
        misc_columns = ["Executable", "ExecutableName"]
        agg = filter_data(
            data, level, groupby_columns, nlargest, misc_columns, minduration
        )
        agg = filter_find(agg, find)
        agg = fitler_nlargets(
            agg, level, nlargest, groupby_columns, misc_columns
        )
    # agg time + exec + exec name + Project BY DUR
    elif level == 4:
        misc_columns = ["Executable", "ExecutableName", "Project"]
        agg = filter_data(
            data, level, groupby_columns, nlargest, misc_columns, minduration
        )
        agg = filter_find(agg, find)
        agg = fitler_nlargets(
            agg, level, nlargest, groupby_columns, misc_columns
        )
    # agg time + exec + exec name + Project BY EXE
    elif level == 5:
        misc_columns = ["Executable", "ExecutableName", "Project"]
        agg = filter_data(
            data, level, groupby_columns, nlargest, misc_columns, minduration
        )
        agg = filter_find(agg, find)
        agg = fitler_nlargets(
            agg, level, nlargest, groupby_columns, misc_columns
        )
    # agg time + exec + exec name + Project BY DUR
    elif level == 6:
        misc_columns = ["Executable", "ExecutableName", "Project", "Details"]
        agg = filter_data(
            data, level, groupby_columns, nlargest, misc_columns, minduration
        )
        agg = filter_find(agg, find)
        agg = fitler_nlargets(
            agg, level, nlargest, groupby_columns, misc_columns
        )
    # agg time + exec + exec name + Project BY EXE
    elif level == 7:
        misc_columns = ["Executable", "ExecutableName", "Project", "Details"]
        agg = filter_data(
            data, level, groupby_columns, nlargest, misc_columns, minduration
        )
        agg = filter_find(agg, find)
        agg = fitler_nlargets(
            agg, level, nlargest, groupby_columns, misc_columns
        )
    
    if level > 1:
        agg["Duration"] = delta_to_string(agg["Duration"])

    print_data(agg, reset_index)
