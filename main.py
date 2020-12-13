from puller import pullQB
import tests
import Converter
import pandas as pd
from io import StringIO

x = pullQB()

Converter.convert(x, write=True, file='Quarterbacks.txt')

