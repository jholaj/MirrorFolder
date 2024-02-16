# Mirroring source folder to replica folder

- One-way periodical synchronization
- Logging in file and terminal (Creation/Removal/Copying/Modifying)
- Comparing hashes of files (MD5)
#### Prerequisites
- Python 3.x
- Built-in libraries: os, argparse, time, shutil, logging, hashlib
#### Usage
```
python main.py -i 1 -l sync_log.txt SOURCE_FOLDER REPLICA_FOLDER
```
#### Options
```
i - interval time (seconds), default -> 1
l - log file, default -> sync_log.txt
```

