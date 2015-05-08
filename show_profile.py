# -*- coding: utf-8 -*-

import pstats
p = pstats.Stats("profiler.results")
p.strip_dirs().sort_stats("time", "cumtime").print_stats(40)
p.strip_dirs().sort_stats("cumtime", "time").print_stats(40)
p.print_callers(2.0, "get_numbered_keyword")
