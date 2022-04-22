
from datetime import datetime
import pandas as pd

def to_datetime( series ) :
  def _to_datetime_value( v ):
    res = datetime.strptime(v, "%m/%d/%y %H:%M:%S")
    if res.year > 2022:
      res = res.replace( year=res.year-100 )
    return res
  return pd.Series([ _to_datetime_value( v )
                     if isinstance(v, str) else None
                     for v in series ], index=series.index)


def to_datetime_dmY( series ):
  return pd.Series([ datetime.strptime(v, "%d.%m.%Y") if isinstance(v, str) else None
                     for v in series ],
                   index=series.index)