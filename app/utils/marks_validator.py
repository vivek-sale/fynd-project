from ast import literal_eval


def marks_validator(total: int, param: str):
    paramdict = literal_eval(param)
    grades = paramdict.keys()
    for grade in grades:
        if max(paramdict[grade]) >= total >= min(paramdict[grade]):
            return grade
    return None
