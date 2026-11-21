# -*- coding: utf-8 -*-
import json, sys
from pathlib import Path
sys.path.insert(0, "/Users/macos/Downloads/WorkBuddy/pawtrack/_scratch/paw-final-rework")
from kit import Client, save_payload

c = Client()

# 201 may be depth-truncated; also 说明 texts, 189 structure
ids = [
    "201:1","2:129","2:130","161:4","161:6","161:10",
    "189:42","189:43","189:44","189:20","189:54","189:56",
    "190:45","190:47","179:31","179:35","179:36","179:37","179:38","179:40",
    "197:16","197:17","197:18","198:32","198:33","199:31","199:32","199:43","199:44","199:49","199:50","201:49","201:51",
]
res=c.batch_read(nodeIds=ids, readDepth=4)
dest,_=save_payload("pre-focus-details", res)
print("SAVED", dest)

# also capture 201 from mid content if needed
